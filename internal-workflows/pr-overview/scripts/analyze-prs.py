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


# -- Jira exclusions --
JIRA_EXCLUDE = {"CVE", "GHSA", "HTTP", "API", "URL", "PR", "WIP"}

# -- PR type priority (lower = higher priority in the queue) --
TYPE_SIGNALS = {
    "bug-fix": {
        "labels": {"bug", "bugfix", "fix"},
        "branches": ("fix/", "bugfix/", "hotfix/", "bug/"),
        "titles": ("fix:", "fix(", "bugfix:", "hotfix:"),
    },
    "feature": {
        "labels": {"feature", "enhancement"},
        "branches": ("feat/", "feature/"),
        "titles": ("feat:", "feat(", "feature:", "add:"),
    },
    "refactor": {
        "labels": {"refactor", "cleanup", "tech-debt"},
        "branches": ("refactor/", "cleanup/", "tech-debt/"),
        "titles": ("refactor:", "refactor(", "cleanup:"),
    },
    "docs": {
        "labels": {"docs", "documentation"},
        "branches": ("docs/", "doc/"),
        "titles": ("docs:", "doc:"),
    },
    "chore": {
        "labels": {"chore", "ci", "dependencies", "deps"},
        "branches": ("chore/", "ci/", "deps/", "dependabot/", "renovate/"),
        "titles": ("chore:", "chore(", "ci:", "ci(", "build:", "build("),
    },
}

TYPE_PRIORITY = {
    "bug-fix": 0,
    "feature": 1,
    "unknown": 2,
    "refactor": 3,
    "chore": 4,
    "docs": 5,
}


def parse_date(s):
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception:
        return None


# -- PR type classification --


def classify_pr_type(title, branch, labels, diff_files=None):
    """Classify a PR by type based on available signals."""
    label_names = {lb.lower() for lb in labels}
    branch_lower = (branch or "").lower()
    title_lower = (title or "").lower().strip()

    for pr_type, signals in TYPE_SIGNALS.items():
        if label_names & signals["labels"]:
            return pr_type

    for pr_type, signals in TYPE_SIGNALS.items():
        if any(branch_lower.startswith(p) for p in signals["branches"]):
            return pr_type

    for pr_type, signals in TYPE_SIGNALS.items():
        if any(title_lower.startswith(p) for p in signals["titles"]):
            return pr_type

    # Heuristic: if diff is available, check file types
    if diff_files:
        filenames = [df.get("filename", "") for df in diff_files]
        md_count = sum(1 for f in filenames if f.endswith(".md"))
        ci_count = sum(
            1
            for f in filenames
            if ".github/" in f
            or f.endswith((".yml", ".yaml"))
            or f in ("Makefile", "Dockerfile", ".dockerignore", ".gitignore")
        )

        if md_count == len(filenames) and len(filenames) > 0:
            return "docs"
        if ci_count == len(filenames) and len(filenames) > 0:
            return "chore"

    # Check title keywords as last resort
    if title_lower:
        if any(w in title_lower for w in ("fix ", "fixed ", "fixes ", "bug")):
            return "bug-fix"

    return "unknown"


# -- Blocker checks --


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

        in_progress = [
            cr
            for cr in check_runs
            if cr.get("status") in ("queued", "in_progress")
        ]
        if in_progress:
            names = [cr.get("name", "unknown") for cr in in_progress[:3]]
            return "warn", f"CI in progress: {', '.join(names)}"

        return "pass", "\u2014"

    if status_rollup:
        failing = [
            s
            for s in status_rollup
            if s.get("conclusion", "").upper()
            in ("FAILURE", "TIMED_OUT", "CANCELLED", "ACTION_REQUIRED")
            or s.get("state", "").upper() in ("FAILURE", "ERROR")
        ]
        if failing:
            names = [
                s.get("name", "") or s.get("context", "unknown") for s in failing[:3]
            ]
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
    elif mergeable == "UNKNOWN":
        return "warn", "Merge status not yet computed"
    else:
        return "FAIL", f"Conflict status: {mergeable or 'unknown'}"


def check_reviews(reviews, review_comments, pr_comments, fetch_ok=True):
    """Handle deterministic review checks only. Comment evaluation is the sub-agent's job.

    Returns (status, detail, has_comments).
    """
    if not fetch_ok:
        return "FAIL", "PR data incomplete \u2014 fetch may have failed", True

    issues = []

    # Check for unresolved CHANGES_REQUESTED
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
        issues.append(
            f"CHANGES_REQUESTED from {', '.join('@' + u for u in unresolved)}"
        )

    # Note inline review comments (informational, not a blocker — most are resolved)
    if review_comments:
        paths = set(c.get("path", "") for c in review_comments if c.get("path"))
        if paths:
            # Don't add to issues — inline comments are not blockers.
            # They're noted in the summary but don't contribute to fail_count.
            pass

    # Check if there are any comments worth reviewing
    has_comments = bool(pr_comments) or any(r.get("body") for r in reviews)

    if issues:
        return "FAIL", "; ".join(issues), has_comments
    if has_comments:
        return "needs_review", "Has comments \u2014 sub-agent to evaluate", True
    return "pass", "\u2014", False


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
    if not updated_at_str:
        return "FAIL", "No updatedAt date found", {"days_old": None}
    updated = parse_date(updated_at_str)
    if not updated:
        return "FAIL", "Cannot parse date", {"days_old": None}
    days_old = (now - updated).days
    if days_old > 30:
        return (
            "FAIL",
            f"Last updated {updated.date()} \u2014 {days_old} days ago",
            {"days_old": days_old},
        )
    return "pass", "\u2014", {"days_old": days_old}


# -- Superseded PR detection --


def detect_superseded(results, index_map):
    pr_files = {}
    for r in results:
        num = r["number"]
        idx = index_map.get(num, {})
        pr_files[num] = {
            "branch": r["branch"],
            "title": r["title"].lower(),
            "created": idx.get("createdAt", ""),
            "updated": r["updatedAt"],
            "is_draft": r["isDraft"],
            "changed_files": idx.get("changedFiles", 0),
        }

    superseded = {}

    for r in results:
        num = r["number"]
        info = pr_files[num]

        for other in results:
            other_num = other["number"]
            if other_num == num:
                continue
            other_info = pr_files[other_num]

            if other_info["created"] <= info["created"]:
                continue

            if (
                info["branch"]
                and other_info["branch"]
                and info["branch"] in other_info["branch"]
                and info["branch"] != other_info["branch"]
            ):
                superseded[num] = other_num
                break

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


# -- Diff hunk overlap analysis --


def parse_hunks(patch):
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


# -- Review order computation --


def compute_review_order(results, overlaps, pr_file_hunks):
    """Compute a recommended review/merge sequence for clean, mergeable PRs."""
    clean_mergeable = [
        r["number"]
        for r in results
        if not r["isDraft"] and r["fail_count"] == 0 and r["conflict_status"] == "pass"
    ]

    if not clean_mergeable:
        return []

    overlap_graph = defaultdict(set)
    for o in overlaps:
        if o["pr_a"] in clean_mergeable and o["pr_b"] in clean_mergeable:
            overlap_graph[o["pr_a"]].add(o["pr_b"])
            overlap_graph[o["pr_b"]].add(o["pr_a"])

    pr_map = {r["number"]: r for r in results}
    ordered = []
    remaining = set(clean_mergeable)

    while remaining:
        best = min(
            remaining,
            key=lambda n: (
                TYPE_PRIORITY.get(pr_map[n]["pr_type"], 99),
                len(overlap_graph.get(n, set()) & remaining),
                0 if pr_map[n]["has_priority"] else 1,
                pr_map[n]["size_score"],
            ),
        )
        ordered.append(best)
        remaining.remove(best)

    return ordered


# -- Unified comment stream extraction --


def merge_comment_sources(pr_comments, reviews, review_comments):
    """Merge all comment sources into a single chronological list.

    This is the shared implementation — pr-fixer/scripts/merge-comments.py
    has an identical copy for CLI use. Keep them in sync.
    """
    all_comments = []

    for c in pr_comments:
        all_comments.append(
            {
                "source": "pr_comment",
                "author": c.get("author", {}).get("login", ""),
                "timestamp": c.get("createdAt", ""),
                "body": c.get("body", ""),
            }
        )

    for r in reviews:
        body = r.get("body", "")
        if not body or not body.strip():
            continue
        all_comments.append(
            {
                "source": "review",
                "author": r.get("user", {}).get("login", ""),
                "state": r.get("state", ""),
                "timestamp": r.get("submitted_at", ""),
                "body": body,
            }
        )

    for rc in review_comments:
        body = rc.get("body", "")
        if not body or not body.strip():
            continue
        all_comments.append(
            {
                "source": "inline_comment",
                "author": rc.get("user", {}).get("login", ""),
                "path": rc.get("path", ""),
                "timestamp": rc.get("created_at", ""),
                "body": body,
            }
        )

    all_comments.sort(key=lambda c: c.get("timestamp", ""))
    return all_comments


def extract_unified_comments(pr_data):
    """Extract and merge all comments from a PR data dict."""
    return merge_comment_sources(
        pr_data.get("pr", {}).get("comments", []),
        pr_data.get("reviews", []),
        pr_data.get("review_comments", []),
    )


# -- Main --


def main():
    parser = argparse.ArgumentParser(description="Analyze PRs for review readiness")
    parser.add_argument(
        "--output-dir",
        default="artifacts/pr-review",
        help="Directory with fetched PR data",
    )
    args = parser.parse_args()

    output_dir = args.output_dir
    now = datetime.now(timezone.utc)

    with open(os.path.join(output_dir, "index.json")) as f:
        index = json.load(f)
    index_map = {pr["number"]: pr for pr in index}

    results = []
    pr_file_hunks = {}
    pr_data_cache = {}  # stash pr_data for needs_review PRs to avoid re-reading

    for idx_pr in index:
        num = idx_pr["number"]
        pr_file = os.path.join(output_dir, "prs", f"{num}.json")

        pr_data = {}
        fetch_ok = False
        try:
            with open(pr_file) as f:
                pr_data = json.load(f)
            fetch_ok = bool(pr_data.get("pr"))
        except (FileNotFoundError, json.JSONDecodeError):
            pass

        pr = pr_data.get("pr", {})
        reviews = pr_data.get("reviews", [])
        review_comments = pr_data.get("review_comments", [])
        check_runs = pr_data.get("check_runs", [])
        diff_files = pr_data.get("diff_files", [])

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
        labels = [
            lb.get("name", "") for lb in (pr.get("labels") or idx_pr.get("labels", []))
        ]
        is_fork = pr.get(
            "isCrossRepository", idx_pr.get("isCrossRepository", False)
        )
        fork_owner = (
            pr.get("headRepositoryOwner")
            or idx_pr.get("headRepositoryOwner")
            or {}
        ).get("login", "")
        milestone = pr.get("milestone")
        milestone_title = milestone.get("title", "") if milestone else ""
        pr_comments = pr.get("comments", [])
        status_rollup = pr.get("statusCheckRollup", [])

        # Classify PR type
        pr_type = classify_pr_type(title, branch, labels, diff_files)

        # Run blocker checks
        ci_status, ci_detail = check_ci(check_runs, status_rollup)
        conflict_status, conflict_detail = check_conflicts(mergeable)
        review_status, review_detail, has_comments = check_reviews(
            reviews, review_comments, pr_comments, fetch_ok
        )
        if review_status == "needs_review":
            pr_data_cache[num] = pr_data
        jira_status, jira_detail = check_jira(title, body, branch)
        stale_status, stale_detail, staleness_data = check_staleness(updated_at, now)

        fail_count = sum(
            1
            for s in [ci_status, conflict_status, review_status, stale_status]
            if s == "FAIL"
        )

        has_priority = any(
            lb in ("priority/critical", "bug", "hotfix", "priority/high")
            for lb in labels
        )

        size_score = additions + deletions + changed_files * 10
        size_str = f"{changed_files} files (+{additions}/-{deletions})"

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
                "rank": 0,
                "title": title,
                "url": url,
                "author": author,
                "isDraft": is_draft,
                "is_fork": is_fork,
                "fork_owner": fork_owner,
                "pr_type": pr_type,
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
                "has_comments": has_comments,
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

    # Recompute fail_count now that overlap_status is set
    for r in results:
        r["fail_count"] = sum(
            1
            for s in [r["ci_status"], r["conflict_status"], r["review_status"],
                       r["stale_status"], r["overlap_status"]]
            if s == "FAIL"
        )

    # Flag PRs to recommend closing
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

    # Rank PRs: type priority, then blocker count, then priority labels, then size
    results.sort(
        key=lambda r: (
            1 if r["isDraft"] else 0,
            TYPE_PRIORITY.get(r["pr_type"], 99),
            r["fail_count"],
            0 if r["has_priority"] else 1,
            r["size_score"],
        )
    )
    for i, r in enumerate(results):
        r["rank"] = i + 1

    # Compute review order for clean PRs
    review_order = compute_review_order(results, overlaps, pr_file_hunks)

    # Stats
    non_draft = [r for r in results if not r["isDraft"]]
    stats = {
        "total": len(results),
        "drafts": len(results) - len(non_draft),
        "clean": sum(1 for r in non_draft if r["fail_count"] == 0),
        "one_blocker": sum(1 for r in non_draft if r["fail_count"] == 1),
        "needs_work": sum(1 for r in non_draft if r["fail_count"] >= 2),
        "recommend_close": sum(1 for r in results if r["recommend_close"]),
        "fork_prs": sum(1 for r in results if r["is_fork"]),
        "by_type": {},
    }

    # Type breakdown
    for r in results:
        t = r["pr_type"]
        stats["by_type"][t] = stats["by_type"].get(t, 0) + 1

    # Collect PRs needing sub-agent review
    needs_review_nums = [r["number"] for r in results if r["review_status"] == "needs_review"]

    # Write per-PR analysis files
    analysis_dir = os.path.join(output_dir, "analysis")
    os.makedirs(analysis_dir, exist_ok=True)

    for r in results:
        pr_path = os.path.join(analysis_dir, f"{r['number']}.json")
        with open(pr_path, "w") as f:
            json.dump(r, f, indent=2, ensure_ascii=False)

    # Write per-PR summary markdown (compact, agent-friendly)
    summaries_dir = os.path.join(output_dir, "summaries")
    os.makedirs(summaries_dir, exist_ok=True)

    for r in results:
        num = r["number"]
        lines = [
            f"# PR #{num}: {r['title']}",
            f"",
            f"- **Author:** {r['author']}",
            f"- **Type:** {r['pr_type']}",
            f"- **Size:** {r['size']}",
            f"- **Updated:** {r['updatedAt']}",
            f"- **Branch:** {r['branch']}",
            f"- **Draft:** {'yes' if r['isDraft'] else 'no'}",
            f"- **Fork:** {'yes (' + r['fork_owner'] + ')' if r['is_fork'] else 'no'}",
            f"",
            f"## Blocker Summary ({r['fail_count']} blockers)",
            f"",
            f"| Check | Status | Detail |",
            f"|-------|--------|--------|",
            f"| CI | {r['ci_status']} | {r['ci_detail']} |",
            f"| Conflicts | {r['conflict_status']} | {r['conflict_detail']} |",
            f"| Reviews | {r['review_status']} | {r['review_detail']} |",
            f"| Jira | {r['jira_status']} | {r['jira_detail']} |",
            f"| Staleness | {r['stale_status']} | {r['stale_detail']} |",
            f"| Overlap | {r['overlap_status']} | {r['overlap_detail']} |",
        ]

        if r["recommend_close"]:
            lines.append(f"")
            lines.append(f"**Recommend closing:** {r['recommend_close_reason']}")

        if r["notes"]:
            lines.append(f"")
            lines.append(f"**Notes:** {r['notes']}")

        # Add comment count summary
        raw = pr_data_cache.get(num, {})
        if raw:
            pr_comments_list = raw.get("pr", {}).get("comments", [])
            reviews_list = raw.get("reviews", [])
            review_comments_list = raw.get("review_comments", [])
            lines.append(f"")
            lines.append(
                f"**Comments:** {len(pr_comments_list)} PR comments, "
                f"{len(reviews_list)} reviews, "
                f"{len(review_comments_list)} inline comments"
            )

        summary_path = os.path.join(summaries_dir, f"{num}.md")
        with open(summary_path, "w") as f:
            f.write("\n".join(lines) + "\n")

    # Write unified comment stream per PR
    reviews_dir = os.path.join(output_dir, "reviews")

    for num in needs_review_nums:
        pr_reviews_dir = os.path.join(reviews_dir, str(num))
        os.makedirs(pr_reviews_dir, exist_ok=True)

        raw = pr_data_cache.get(num, {})
        if not raw:
            continue

        all_comments = extract_unified_comments(raw)
        pr = raw.get("pr", {})

        # Write meta file
        meta = {
            "number": num,
            "title": pr.get("title", ""),
            "author": (pr.get("author") or {}).get("login", ""),
            "total_comments": len(all_comments),
        }
        with open(os.path.join(pr_reviews_dir, "meta.json"), "w") as f:
            json.dump(meta, f, indent=2, ensure_ascii=False)

        # Write each comment as a numbered file, chronological order
        for i, comment in enumerate(all_comments, 1):
            comment_path = os.path.join(pr_reviews_dir, f"{i:02d}.json")
            with open(comment_path, "w") as f:
                json.dump(comment, f, indent=2, ensure_ascii=False)

    # Write compact summary
    pr_index = []
    for r in results:
        pr_index.append(
            {
                "number": r["number"],
                "rank": r["rank"],
                "title": r["title"],
                "author": r["author"],
                "isDraft": r["isDraft"],
                "pr_type": r["pr_type"],
                "fail_count": r["fail_count"],
                "review_status": r["review_status"],
                "recommend_close": r["recommend_close"],
                "is_fork": r["is_fork"],
            }
        )

    summary = {
        "generated_at": now.strftime("%Y-%m-%dT%H:%M:%S UTC"),
        "stats": stats,
        "review_order": review_order,
        "needs_review": needs_review_nums,
        "pr_index": pr_index,
        "overlaps": overlaps,
        "shared_no_overlap": shared_no_overlap,
    }

    summary_path = os.path.join(output_dir, "analysis.json")
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print("Analysis complete:")
    print(f"  Summary: {summary_path}")
    print(f"  Per-PR:  {analysis_dir}/{{number}}.json")
    print(f"  Reviews: {reviews_dir}/{{number}}/meta.json + 01.json, 02.json, ...")
    print(f"  Total: {stats['total']} PRs ({stats['drafts']} drafts)")
    print(
        f"  Clean: {stats['clean']} | One blocker: {stats['one_blocker']} | Needs work: {stats['needs_work']}"
    )
    print(f"  Recommend closing: {stats['recommend_close']}")
    print(f"  Type breakdown: {stats['by_type']}")
    print(
        f"  Needs sub-agent review: {len(needs_review_nums)} PRs \u2014 {needs_review_nums}"
    )
    print(
        f"  Overlaps: {len(overlaps)} line-level, {len(shared_no_overlap)} shared-file-only"
    )
    if review_order:
        arrow = " \u2192 "
        print(
            f"  Review order: {arrow.join(f'#{n}' for n in review_order[:10])}"
        )


if __name__ == "__main__":
    main()
