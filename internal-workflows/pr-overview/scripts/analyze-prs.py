#!/usr/bin/env python3
"""
Analyze all fetched PR data against the blocker checklist and produce analysis.json.

Usage:
    python3 scripts/analyze-prs.py --output-dir artifacts/pr-review

Input:  {output-dir}/index.json and {output-dir}/prs/{number}.json
Output: {output-dir}/analysis.json
"""

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone


# ── Jira exclusions ──────────────────────────────────────────────────────────
JIRA_EXCLUDE = {"CVE", "GHSA", "HTTP", "API", "URL", "PR", "WIP"}



def parse_date(s):
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception:
        return None



# ── Blocker checks ───────────────────────────────────────────────────────────


def check_ci(check_runs, status_rollup):
    """Evaluate CI status. Returns (status, detail)."""
    if check_runs:
        failing = [
            cr
            for cr in check_runs
            if cr.get("status") == "completed"
            and cr.get("conclusion")
            in ("failure", "timed_out", "cancelled", "action_required")
        ]
        if failing:
            names = [cr.get("name", "unknown") for cr in failing[:3]]
            extra = len(failing) - 3
            detail = ", ".join(names)
            if extra > 0:
                detail += f" (+{extra} more)"
            return "FAIL", f"Failing: {detail}"

        # Check for in-progress runs (not yet completed)
        in_progress = [
            cr
            for cr in check_runs
            if cr.get("status") in ("queued", "in_progress")
        ]
        if in_progress:
            names = [cr.get("name", "unknown") for cr in in_progress[:3]]
            return "warn", f"CI in progress: {', '.join(names)}"

        return "pass", "\u2014"

    # Fallback to statusCheckRollup
    if status_rollup:
        failing = [
            s
            for s in status_rollup
            if s.get("conclusion", "").upper()
            in ("FAILURE", "TIMED_OUT", "CANCELLED", "ACTION_REQUIRED")
            or s.get("state", "").upper() in ("FAILURE", "ERROR")
        ]
        if failing:
            names = [s.get("name", "") or s.get("context", "unknown") for s in failing[:3]]
            extra = len(failing) - 3
            detail = ", ".join(names)
            if extra > 0:
                detail += f" (+{extra} more)"
            return "FAIL", f"Failing: {detail}"

        pending = [
            s
            for s in status_rollup
            if s.get("state", "").upper() in ("PENDING", "EXPECTED")
        ]
        if pending:
            return "warn", "CI pending"

    return "pass", "\u2014"


def check_conflicts(mergeable):
    if mergeable == "MERGEABLE":
        return "pass", "\u2014"
    elif mergeable == "CONFLICTING":
        return "FAIL", "Has merge conflicts"
    else:
        return "FAIL", f"Conflict status: {mergeable or 'unknown'}"


def check_reviews(reviews, review_comments, pr_comments):
    """Handle deterministic review checks only. Comment evaluation is the agent's job.

    Returns (status, detail, comments_for_review).
    - status/detail cover only CHANGES_REQUESTED and inline threads.
    - comments_for_review is a list of comment excerpts for the agent to evaluate.
    """
    issues = []

    # 1. Check for unresolved CHANGES_REQUESTED (handle DISMISSED)
    user_states = {}
    for r in reviews:
        login = r.get("user", {}).get("login", "")
        state = r.get("state", "")
        if state == "CHANGES_REQUESTED":
            user_states[login] = "CHANGES_REQUESTED"
        elif state in ("APPROVED", "DISMISSED"):
            if user_states.get(login) == "CHANGES_REQUESTED":
                user_states[login] = state

    unresolved = [u for u, s in user_states.items() if s == "CHANGES_REQUESTED"]
    if unresolved:
        issues.append(f"CHANGES_REQUESTED from {', '.join('@' + u for u in unresolved)}")

    # 2. Check inline review comments (count threads)
    if review_comments:
        paths = set(c.get("path", "") for c in review_comments if c.get("path"))
        if paths:
            issues.append(
                f"{len(review_comments)} inline threads on {', '.join(list(paths)[:2])}"
            )

    # 3. Surface comments for agent evaluation (no parsing, no regex)
    # Include last few comments from each source, trimmed to reasonable length.
    comments_for_review = []

    # Last 3 PR comments (includes bot reviews and human discussion)
    for c in pr_comments[-3:]:
        author = c.get("author", {}).get("login", "")
        body = (c.get("body", "") or "")[:500]
        if body.strip():
            comments_for_review.append({"author": author, "body": body})

    # Last 3 formal reviews with body content
    for r in reviews[-3:]:
        login = r.get("user", {}).get("login", "")
        state = r.get("state", "")
        body = (r.get("body", "") or "")[:300]
        if body.strip():
            comments_for_review.append({"author": login, "state": state, "body": body})

    if issues:
        return "FAIL", "; ".join(issues), comments_for_review
    if comments_for_review:
        return "needs_review", "Has comments — agent to evaluate", comments_for_review
    return "pass", "\u2014", []


def check_jira(title, body, branch):
    text = (title or "") + " " + (body or "") + " " + (branch or "")
    if re.search(r"RHOAIENG-\d+", text):
        return "pass", "\u2014"
    for m in re.finditer(r"([A-Z]{2,})-\d+", text):
        prefix = m.group(1)
        if prefix not in JIRA_EXCLUDE:
            return "pass", "\u2014"
    return "warn", "No Jira reference found"


def check_staleness(updated_at_str, now):
    """Compute staleness signals for agent judgment. Returns (status, detail, staleness_data)."""
    if not updated_at_str:
        return "FAIL", "No updatedAt date found", {"days_old": None}
    updated = parse_date(updated_at_str)
    if not updated:
        return "FAIL", "Cannot parse date", {"days_old": None}
    days_old = (now - updated).days
    if days_old > 30:
        return "FAIL", f"Last updated {updated.date()} \u2014 {days_old} days ago", {"days_old": days_old}
    return "pass", "\u2014", {"days_old": days_old}


# ── Superseded PR detection ─────────────────────────────────────────────────


def detect_superseded(results, index_map):
    """Detect PRs that may be superseded by newer PRs touching the same files."""
    # Build a map of files touched by each PR (from index data)
    pr_files = {}
    for r in results:
        num = r["number"]
        idx = index_map.get(num, {})
        # changedFiles count is in the index, but actual file list is in detail
        # We'll use branch name similarity and title similarity as signals
        pr_files[num] = {
            "branch": r["branch"],
            "title": r["title"].lower(),
            "created": idx.get("createdAt", ""),
            "updated": r["updatedAt"],
            "is_draft": r["isDraft"],
            "changed_files": idx.get("changedFiles", 0),
        }

    superseded = {}  # pr_number -> superseding pr_number

    for r in results:
        num = r["number"]
        info = pr_files[num]

        for other in results:
            other_num = other["number"]
            if other_num == num:
                continue
            other_info = pr_files[other_num]

            # Skip if the other PR is older
            if other_info["created"] <= info["created"]:
                continue

            # Check if branches suggest supersession (e.g., feat/foo-v2 supersedes feat/foo)
            if (
                info["branch"]
                and other_info["branch"]
                and info["branch"] in other_info["branch"]
                and info["branch"] != other_info["branch"]
            ):
                superseded[num] = other_num
                break

            # Check if titles are very similar (edit distance proxy: one contains the other)
            if (
                len(info["title"]) > 15
                and len(other_info["title"]) > 15
                and (
                    info["title"] in other_info["title"]
                    or other_info["title"] in info["title"]
                )
                and info["created"] < other_info["created"]
            ):
                superseded[num] = other_num
                break

    return superseded


# ── Diff hunk overlap analysis ───────────────────────────────────────────────


def parse_hunks(patch):
    """Parse hunk headers from a unified diff patch string."""
    if not patch:
        return []
    hunks = []
    for m in re.finditer(r"@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@", patch):
        start = int(m.group(1))
        count = int(m.group(2)) if m.group(2) is not None else 1
        hunks.append((start, start + count - 1))
    return hunks


def hunks_overlap(h1, h2):
    return h1[0] <= h2[1] and h2[0] <= h1[1]


def compute_overlaps(pr_file_hunks):
    """Find line-level overlaps between all pairs of mergeable PRs."""
    nums = sorted(pr_file_hunks.keys())
    overlaps = []
    shared_no_overlap = []

    for i, num_a in enumerate(nums):
        for num_b in nums[i + 1 :]:
            files_a = set(pr_file_hunks[num_a].keys())
            files_b = set(pr_file_hunks[num_b].keys())
            shared = files_a & files_b

            if not shared:
                continue

            has_overlap = False
            for fname in shared:
                for ha in pr_file_hunks[num_a][fname]:
                    for hb in pr_file_hunks[num_b][fname]:
                        if hunks_overlap(ha, hb):
                            overlaps.append(
                                {
                                    "pr_a": num_a,
                                    "pr_b": num_b,
                                    "file": fname,
                                    "range_a": list(ha),
                                    "range_b": list(hb),
                                }
                            )
                            has_overlap = True

            if not has_overlap:
                shared_no_overlap.append(
                    {"pr_a": num_a, "pr_b": num_b, "shared_files": list(shared)}
                )

    return overlaps, shared_no_overlap


# ── Merge order computation ──────────────────────────────────────────────────


def compute_merge_order(results, overlaps, pr_file_hunks):
    """Compute a recommended merge sequence for clean, mergeable PRs."""
    clean_mergeable = [
        r["number"]
        for r in results
        if not r["isDraft"] and r["fail_count"] == 0 and r["conflict_status"] == "pass"
    ]

    if not clean_mergeable:
        return []

    # Build overlap graph: edges between PRs that overlap
    overlap_graph = defaultdict(set)
    for o in overlaps:
        if o["pr_a"] in clean_mergeable and o["pr_b"] in clean_mergeable:
            overlap_graph[o["pr_a"]].add(o["pr_b"])
            overlap_graph[o["pr_b"]].add(o["pr_a"])

    pr_map = {r["number"]: r for r in results}
    ordered = []
    remaining = set(clean_mergeable)

    # Greedy: always pick the PR with fewest overlap partners, smallest size
    while remaining:
        best = min(
            remaining,
            key=lambda n: (
                len(overlap_graph.get(n, set()) & remaining),
                pr_map[n]["size_score"],
            ),
        )
        ordered.append(best)
        remaining.remove(best)

    return ordered


# ── Main ─────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(description="Analyze PRs for merge readiness")
    parser.add_argument(
        "--output-dir",
        default="artifacts/pr-review",
        help="Directory with fetched PR data",
    )
    args = parser.parse_args()

    output_dir = args.output_dir
    now = datetime.now(timezone.utc)

    # Load index
    with open(os.path.join(output_dir, "index.json")) as f:
        index = json.load(f)
    index_map = {pr["number"]: pr for pr in index}

    # Analyze each PR
    results = []
    pr_file_hunks = {}  # for overlap analysis

    for idx_pr in index:
        num = idx_pr["number"]
        pr_file = os.path.join(output_dir, "prs", f"{num}.json")

        # Load detailed data
        pr_data = {}
        if os.path.exists(pr_file) and os.path.getsize(pr_file) > 10:
            with open(pr_file) as f:
                pr_data = json.load(f)

        pr = pr_data.get("pr", {})
        reviews = pr_data.get("reviews", [])
        review_comments = pr_data.get("review_comments", [])
        check_runs = pr_data.get("check_runs", [])
        diff_files = pr_data.get("diff_files", [])

        # Use index as fallback for fields missing in detail
        title = pr.get("title") or idx_pr.get("title", "")
        author = (pr.get("author") or idx_pr.get("author", {})).get("login", "unknown")
        is_draft = pr.get("isDraft", idx_pr.get("isDraft", False))
        mergeable = pr.get("mergeable") or idx_pr.get("mergeable", "UNKNOWN")
        updated_at = pr.get("updatedAt") or idx_pr.get("updatedAt", "")
        created_at = pr.get("createdAt") or idx_pr.get("createdAt", "")
        branch = pr.get("headRefName") or idx_pr.get("headRefName", "")
        body = pr.get("body") or idx_pr.get("body", "")
        url = pr.get("url") or idx_pr.get("url", "")
        additions = pr.get("additions", idx_pr.get("additions", 0)) or 0
        deletions = pr.get("deletions", idx_pr.get("deletions", 0)) or 0
        changed_files = pr.get("changedFiles", idx_pr.get("changedFiles", 0)) or 0
        labels = [lb.get("name", "") for lb in (pr.get("labels") or idx_pr.get("labels", []))]
        milestone = pr.get("milestone")
        milestone_title = milestone.get("title", "") if milestone else ""
        pr_comments = pr.get("comments", [])
        status_rollup = pr.get("statusCheckRollup", [])

        # Run blocker checks
        ci_status, ci_detail = check_ci(check_runs, status_rollup)
        conflict_status, conflict_detail = check_conflicts(mergeable)
        review_status, review_detail, comments_for_review = check_reviews(reviews, review_comments, pr_comments)
        jira_status, jira_detail = check_jira(title, body, branch)
        stale_status, stale_detail, staleness_data = check_staleness(updated_at, now)

        # Count FAILs (warn doesn't count)
        fail_count = sum(
            1
            for s in [ci_status, conflict_status, review_status, stale_status]
            if s == "FAIL"
        )

        # Priority labels
        has_priority = any(
            lb in ("priority/critical", "bug", "hotfix", "priority/high") for lb in labels
        )

        # Size score (for ranking)
        size_score = additions + deletions + changed_files * 10
        size_str = f"{changed_files} files (+{additions}/-{deletions})"

        # Build file hunks for overlap analysis
        if not is_draft and mergeable == "MERGEABLE" and diff_files:
            file_hunks = {}
            for df in diff_files:
                fname = df.get("filename", "")
                patch = df.get("patch", "")
                hunks = parse_hunks(patch)
                if fname and hunks:
                    file_hunks[fname] = hunks
            if file_hunks:
                pr_file_hunks[num] = file_hunks

        results.append(
            {
                "number": num,
                "rank": 0,  # set after sorting
                "title": title,
                "url": url,
                "author": author,
                "isDraft": is_draft,
                "size": size_str,
                "size_score": size_score,
                "updatedAt": updated_at[:10] if updated_at else "",
                "createdAt": created_at[:10] if created_at else "",
                "branch": branch,
                "labels": labels,
                "milestoneCurrently": milestone_title,
                "ci_status": ci_status,
                "ci_detail": ci_detail,
                "conflict_status": conflict_status,
                "conflict_detail": conflict_detail,
                "review_status": review_status,
                "review_detail": review_detail,
                "comments_for_review": comments_for_review,
                "jira_status": jira_status,
                "jira_detail": jira_detail,
                "stale_status": stale_status,
                "stale_detail": stale_detail,
                "days_since_update": staleness_data["days_old"],
                "overlap_status": "\u2014",
                "overlap_detail": "\u2014",
                "notes": "",
                "fail_count": fail_count,
                "has_priority": has_priority,
                "superseded_by": None,
                "recommend_close": False,
                "recommend_close_reason": "",
            }
        )

    # Detect superseded PRs
    superseded = detect_superseded(results, index_map)
    for r in results:
        if r["number"] in superseded:
            r["superseded_by"] = superseded[r["number"]]
            r["notes"] = f"May be superseded by #{superseded[r['number']]}"

    # Compute diff overlaps
    overlaps, shared_no_overlap = compute_overlaps(pr_file_hunks)

    # Set overlap status per PR
    pr_map = {r["number"]: r for r in results}
    overlap_prs = set()
    warn_prs = set()

    for o in overlaps:
        overlap_prs.add(o["pr_a"])
        overlap_prs.add(o["pr_b"])

    for s in shared_no_overlap:
        if s["pr_a"] not in overlap_prs:
            warn_prs.add(s["pr_a"])
        if s["pr_b"] not in overlap_prs:
            warn_prs.add(s["pr_b"])

    for r in results:
        num = r["number"]
        if r["isDraft"] or r["conflict_status"] == "FAIL":
            r["overlap_status"] = "\u2014"
            r["overlap_detail"] = "\u2014"
        elif num in overlap_prs:
            partners = set()
            files = set()
            for o in overlaps:
                if o["pr_a"] == num:
                    partners.add(o["pr_b"])
                    files.add(o["file"])
                elif o["pr_b"] == num:
                    partners.add(o["pr_a"])
                    files.add(o["file"])
            partner_str = ", ".join(f"#{p}" for p in sorted(partners))
            file_str = ", ".join(sorted(files)[:2])
            r["overlap_status"] = "FAIL"
            r["overlap_detail"] = f"Line overlap with {partner_str} on {file_str}"
            if not r["notes"]:
                r["notes"] = f"Merge order matters: overlaps with {partner_str}"
        elif num in warn_prs:
            r["overlap_status"] = "warn"
            r["overlap_detail"] = "Shares files but no line overlap"
        elif num in pr_file_hunks:
            r["overlap_status"] = "pass"
            r["overlap_detail"] = "\u2014"

    # Flag PRs to recommend closing (for agent to review)
    for r in results:
        reasons = []
        days = r["days_since_update"]
        if r["isDraft"] and days is not None and days > 21 and r["conflict_status"] == "FAIL":
            reasons.append(f"Draft with conflicts, inactive {days}d")
        if r["superseded_by"]:
            reasons.append(f"Superseded by #{r['superseded_by']}")
        if days is not None and days > 60:
            reasons.append(f"Inactive for {days} days")
        if days is not None and days > 30 and r["fail_count"] >= 2:
            reasons.append(f"Stale ({days}d) with {r['fail_count']} blockers")
        if reasons:
            r["recommend_close"] = True
            r["recommend_close_reason"] = "; ".join(reasons)

    # Rank PRs
    results.sort(
        key=lambda r: (
            1 if r["isDraft"] else 0,
            r["fail_count"],
            0 if r["has_priority"] else 1,
            r["size_score"],
        )
    )
    for i, r in enumerate(results):
        r["rank"] = i + 1

    # Compute merge order for clean PRs
    merge_order = compute_merge_order(results, overlaps, pr_file_hunks)

    # Stats
    non_draft = [r for r in results if not r["isDraft"]]
    stats = {
        "total": len(results),
        "drafts": len(results) - len(non_draft),
        "clean": sum(1 for r in non_draft if r["fail_count"] == 0),
        "one_blocker": sum(1 for r in non_draft if r["fail_count"] == 1),
        "needs_work": sum(1 for r in non_draft if r["fail_count"] >= 2),
        "recommend_close": sum(1 for r in results if r["recommend_close"]),
    }

    output = {
        "generated_at": now.strftime("%Y-%m-%dT%H:%M:%S UTC"),
        "stats": stats,
        "merge_order": merge_order,
        "prs": results,
        "overlaps": overlaps,
        "shared_no_overlap": shared_no_overlap,
    }

    output_path = os.path.join(output_dir, "analysis.json")
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Analysis complete: {output_path}")
    print(f"  Total: {stats['total']} PRs ({stats['drafts']} drafts)")
    print(f"  Clean: {stats['clean']} | One blocker: {stats['one_blocker']} | Needs work: {stats['needs_work']}")
    print(f"  Recommend closing: {stats['recommend_close']}")
    print(f"  Overlaps: {len(overlaps)} line-level, {len(shared_no_overlap)} shared-file-only")
    if merge_order:
        print(f"  Merge order: {' → '.join(f'#{n}' for n in merge_order[:10])}")


if __name__ == "__main__":
    main()
