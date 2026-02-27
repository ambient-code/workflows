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
from datetime import datetime, timezone


# ── Jira exclusions ──────────────────────────────────────────────────────────
JIRA_EXCLUDE = {"CVE", "GHSA", "HTTP", "API", "URL", "PR", "WIP"}

# ── Security blocker patterns ────────────────────────────────────────────────
SECURITY_PATTERNS = [
    "data race",
    "race condition",
    "nil pointer dereference",
    "hardcoded token",
    "hardcoded secret",
    "hardcoded password",
    "hardcoded credential",
    "hardcoded api",
    "prompt injection",
    "sql injection",
    "command injection",
    "rbac bypass",
    "auth bypass",
    "compile error",
    "does not compile",
    "syntax error",
    "missing ownerreference",
]


def parse_date(s):
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception:
        return None


def is_none_content(text):
    """Check if blocker/critical section content is effectively 'None'."""
    text = text.strip()
    if not text:
        return True
    clean = re.sub(r"[_*`]", "", text).strip()
    if not clean:
        return True
    first_word = clean.split()[0].rstrip(".,;:!-\u2013\u2014") if clean.split() else ""
    return first_word.lower() == "none"


def is_genuine_blocker(text):
    """Check if blocker/critical text describes a real security/compile issue."""
    if is_none_content(text):
        return False
    text_lower = text.lower()
    return any(pat in text_lower for pat in SECURITY_PATTERNS)


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

    return "pass", "\u2014"


def check_conflicts(mergeable):
    if mergeable == "MERGEABLE":
        return "pass", "\u2014"
    elif mergeable == "CONFLICTING":
        return "FAIL", "Has merge conflicts"
    else:
        return "FAIL", f"Conflict status: {mergeable or 'unknown'}"


def check_reviews(reviews, review_comments, pr_comments):
    """Evaluate review status across all three data sources."""
    issues = []

    # 1. Check for unresolved CHANGES_REQUESTED
    user_states = {}
    for r in reviews:
        login = r.get("user", {}).get("login", "")
        state = r.get("state", "")
        if state == "CHANGES_REQUESTED":
            user_states[login] = "CHANGES_REQUESTED"
        elif state == "APPROVED" and user_states.get(login) == "CHANGES_REQUESTED":
            user_states[login] = "APPROVED"

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

    # 3. Check bot review comments (last one only)
    bot_comments = [
        c
        for c in pr_comments
        if "github-actions" in c.get("author", {}).get("login", "")
        or "[bot]" in c.get("author", {}).get("login", "")
    ]
    if bot_comments:
        last_bot = bot_comments[-1]
        body = last_bot.get("body", "")

        # Extract blocker section
        blocker_match = re.search(
            r"(?:###?\s*)?(?:\U0001f6ab\s*)?Blocker\s*Issues?\s*\n(.*?)(?=\n###?\s|\Z)",
            body,
            re.DOTALL | re.IGNORECASE,
        )
        if blocker_match:
            content = blocker_match.group(1).strip()
            if not is_none_content(content) and is_genuine_blocker(content):
                # Summarize to first 80 chars
                summary = content.split("\n")[0][:80]
                issues.append(f"Bot blocker: {summary}")

        # Extract critical section
        critical_match = re.search(
            r"(?:###?\s*)?(?:\U0001f534\s*)?Critical\s*Issues?\s*\n(.*?)(?=\n###?\s|\Z)",
            body,
            re.DOTALL | re.IGNORECASE,
        )
        if critical_match:
            content = critical_match.group(1).strip()
            if not is_none_content(content) and is_genuine_blocker(content):
                summary = content.split("\n")[0][:80]
                issues.append(f"Bot critical: {summary}")

    if issues:
        return "FAIL", "; ".join(issues)
    return "pass", "\u2014"


def check_jira(title, body, branch):
    text = (title or "") + " " + (body or "") + " " + (branch or "")
    if re.search(r"RHOAIENG-\d+", text):
        return "pass", "\u2014"
    for m in re.finditer(r"([A-Z]{2,})-\d+", text):
        prefix = m.group(1)
        if prefix not in JIRA_EXCLUDE:
            return "pass", "\u2014"
    return "warn", "No Jira reference found"


def check_staleness(updated_at_str, cutoff):
    if not updated_at_str:
        return "FAIL", "No updatedAt date found"
    updated = parse_date(updated_at_str)
    if not updated:
        return "FAIL", "Cannot parse date"
    if updated < cutoff:
        return "FAIL", f"Last updated {updated.date()} \u2014 more than 30 days ago"
    return "pass", "\u2014"


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
    stale_cutoff = now.replace(day=now.day) - __import__("datetime").timedelta(days=30)

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
        review_status, review_detail = check_reviews(reviews, review_comments, pr_comments)
        jira_status, jira_detail = check_jira(title, body, branch)
        stale_status, stale_detail = check_staleness(updated_at, stale_cutoff)

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
                "branch": branch,
                "labels": labels,
                "milestoneCurrently": milestone_title,
                "ci_status": ci_status,
                "ci_detail": ci_detail,
                "conflict_status": conflict_status,
                "conflict_detail": conflict_detail,
                "review_status": review_status,
                "review_detail": review_detail,
                "jira_status": jira_status,
                "jira_detail": jira_detail,
                "stale_status": stale_status,
                "stale_detail": stale_detail,
                "overlap_status": "\u2014",
                "overlap_detail": "\u2014",
                "notes": "",
                "fail_count": fail_count,
                "has_priority": has_priority,
            }
        )

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
            # Find which PRs this one overlaps with
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
            r["notes"] = f"Merge order matters: overlaps with {partner_str}"
        elif num in warn_prs:
            r["overlap_status"] = "warn"
            r["overlap_detail"] = "Shares files but no line overlap"
        elif num in pr_file_hunks:
            r["overlap_status"] = "pass"
            r["overlap_detail"] = "\u2014"

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

    # Stats
    non_draft = [r for r in results if not r["isDraft"]]
    stats = {
        "total": len(results),
        "drafts": len(results) - len(non_draft),
        "clean": sum(1 for r in non_draft if r["fail_count"] == 0),
        "one_blocker": sum(1 for r in non_draft if r["fail_count"] == 1),
        "needs_work": sum(1 for r in non_draft if r["fail_count"] >= 2),
    }

    output = {
        "generated_at": now.strftime("%Y-%m-%dT%H:%M:%S UTC"),
        "stats": stats,
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
    print(f"  Overlaps: {len(overlaps)} line-level, {len(shared_no_overlap)} shared-file-only")


if __name__ == "__main__":
    main()
