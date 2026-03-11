#!/usr/bin/env python3
"""
Analyze structured PR data and produce per-PR analysis + ranked queue.

Reads: {output-dir}/{number}/summary.json (and diff.json for overlaps)
Writes: {output-dir}/{number}/analysis.json
        {output-dir}/queue.json

Usage:
    python3 scripts/analyze-prs.py --output-dir artifacts/pr-review
"""

import argparse
import json
import os
import re
from datetime import datetime, timezone

JIRA_EXCLUDE = {"CVE", "GHSA", "HTTP", "API", "URL", "PR", "WIP"}

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

TYPE_PRIORITY = {"bug-fix": 0, "feature": 1, "unknown": 2, "refactor": 3, "chore": 4, "docs": 5}


def classify_type(summary):
    labels = {lb.lower() for lb in summary.get("labels", [])}
    branch = (summary.get("branch") or "").lower()
    title = (summary.get("title") or "").lower().strip()
    for pr_type, signals in TYPE_SIGNALS.items():
        if labels & signals["labels"]:
            return pr_type
    for pr_type, signals in TYPE_SIGNALS.items():
        if any(branch.startswith(p) for p in signals["branches"]):
            return pr_type
    for pr_type, signals in TYPE_SIGNALS.items():
        if any(title.startswith(p) for p in signals["titles"]):
            return pr_type
    if title and any(w in title for w in ("fix ", "fixed ", "fixes ", "bug")):
        return "bug-fix"
    return "unknown"


def check_ci(summary):
    ci = summary.get("ci", {})
    failing = ci.get("failing", [])
    if ci.get("status") == "failing":
        detail = ", ".join(failing[:3])
        if len(failing) > 3:
            detail += f" (+{len(failing) - 3} more)"
        return "FAIL", f"Failing: {detail}"
    if ci.get("status") == "pending":
        return "warn", "CI in progress"
    return "pass", "\u2014"


def check_conflicts(summary):
    m = summary.get("mergeable", "UNKNOWN")
    if m == "MERGEABLE":
        return "pass", "\u2014"
    if m == "CONFLICTING":
        return "FAIL", "Has merge conflicts"
    if m == "UNKNOWN":
        return "warn", "Merge status not yet computed"
    return "FAIL", f"Conflict status: {m}"


def check_reviews(summary):
    reviews = summary.get("reviews", {})
    comments = summary.get("comments", {})
    cr_by = reviews.get("changes_requested_by", [])
    if cr_by:
        return "FAIL", f"CHANGES_REQUESTED from {', '.join('@' + u for u in cr_by)}"
    if comments.get("inline_threads", 0) > 0:
        return "needs_review", f"{comments['inline_threads']} inline threads"
    if comments.get("total", 0) > 0:
        return "needs_review", "Has comments"
    return "pass", "\u2014"


def check_jira(summary):
    text = " ".join([summary.get("title", ""), summary.get("body", ""), summary.get("branch", "")])
    if re.search(r"RHOAIENG-\d+", text):
        return "pass", "\u2014"
    for m in re.finditer(r"([A-Z]{2,})-\d+", text):
        if m.group(1) not in JIRA_EXCLUDE:
            return "pass", "\u2014"
    return "warn", "No Jira reference found"


def check_staleness(summary, now):
    updated = summary.get("updatedAt", "")
    if not updated:
        return "FAIL", "No updatedAt date", None
    try:
        dt = datetime.fromisoformat(updated.replace("Z", "+00:00"))
    except Exception:
        return "FAIL", "Cannot parse date", None
    days = (now - dt).days
    if days > 30:
        return "FAIL", f"Last updated {dt.date()} \u2014 {days} days ago", days
    return "pass", "\u2014", days


def parse_hunks(patch):
    if not patch:
        return []
    return [
        (int(m.group(1)), int(m.group(1)) + int(m.group(2) or 1) - 1)
        for m in re.finditer(r"@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@", patch)
    ]


def compute_overlaps(pr_hunks):
    nums = sorted(pr_hunks.keys())
    overlaps = []
    for i, a in enumerate(nums):
        for b in nums[i + 1:]:
            shared = set(pr_hunks[a]) & set(pr_hunks[b])
            for fname in shared:
                for ha in pr_hunks[a][fname]:
                    for hb in pr_hunks[b][fname]:
                        if ha[0] <= hb[1] and hb[0] <= ha[1]:
                            overlaps.append({"pr_a": a, "pr_b": b, "file": fname})
    return overlaps


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="artifacts/pr-review")
    args = parser.parse_args()
    output_dir = args.output_dir
    now = datetime.now(timezone.utc)

    pr_dirs = [
        e for e in os.listdir(output_dir)
        if os.path.isdir(os.path.join(output_dir, e))
        and os.path.exists(os.path.join(output_dir, e, "summary.json"))
    ]
    if not pr_dirs:
        print("No PR data found.")
        return

    summaries = {}
    for d in pr_dirs:
        with open(os.path.join(output_dir, d, "summary.json")) as f:
            summaries[d] = json.load(f)

    results = []
    pr_hunks = {}

    for pr_dir, s in summaries.items():
        num = s["number"]
        pr_type = classify_type(s)
        ci_status, ci_detail = check_ci(s)
        conflict_status, conflict_detail = check_conflicts(s)
        review_status, review_detail = check_reviews(s)
        jira_status, jira_detail = check_jira(s)
        stale_status, stale_detail, days_old = check_staleness(s, now)

        if not s.get("isDraft") and s.get("mergeable") == "MERGEABLE":
            diff_path = os.path.join(output_dir, pr_dir, "diff.json")
            try:
                with open(diff_path) as f:
                    diff_data = json.load(f)
                fh = {}
                for df in diff_data.get("files", []):
                    hunks = parse_hunks(df.get("patch", ""))
                    if df.get("filename") and hunks:
                        fh[df["filename"]] = hunks
                if fh:
                    pr_hunks[num] = fh
            except (FileNotFoundError, json.JSONDecodeError):
                pass

        size = s.get("size", {})
        has_priority = any(lb in ("priority/critical", "bug", "hotfix", "priority/high") for lb in s.get("labels", []))

        results.append({
            "number": num, "title": s.get("title", ""), "url": s.get("url", ""),
            "author": s.get("author", ""), "isDraft": s.get("isDraft", False),
            "isFork": s.get("isFork", False), "forkOwner": s.get("forkOwner", ""),
            "pr_type": pr_type,
            "size": f"{size.get('files', 0)} files (+{size.get('additions', 0)}/-{size.get('deletions', 0)})",
            "size_score": size.get("additions", 0) + size.get("deletions", 0) + size.get("files", 0) * 10,
            "updatedAt": (s.get("updatedAt") or "")[:10], "createdAt": (s.get("createdAt") or "")[:10],
            "branch": s.get("branch", ""), "labels": s.get("labels", []),
            "ci_status": ci_status, "ci_detail": ci_detail,
            "conflict_status": conflict_status, "conflict_detail": conflict_detail,
            "review_status": review_status, "review_detail": review_detail,
            "jira_status": jira_status, "jira_detail": jira_detail,
            "stale_status": stale_status, "stale_detail": stale_detail,
            "days_since_update": days_old,
            "overlap_status": "\u2014", "overlap_detail": "\u2014",
            "fail_count": 0, "has_priority": has_priority,
            "recommend_close": False, "recommend_close_reason": "",
        })

    overlaps = compute_overlaps(pr_hunks)
    overlap_prs = {o["pr_a"] for o in overlaps} | {o["pr_b"] for o in overlaps}
    for r in results:
        num = r["number"]
        if not r["isDraft"] and r["conflict_status"] != "FAIL" and num in overlap_prs:
            partners, files = set(), set()
            for o in overlaps:
                if o["pr_a"] == num: partners.add(o["pr_b"]); files.add(o["file"])
                elif o["pr_b"] == num: partners.add(o["pr_a"]); files.add(o["file"])
            r["overlap_status"] = "FAIL"
            r["overlap_detail"] = f"Line overlap with {', '.join(f'#{p}' for p in sorted(partners))} on {', '.join(sorted(files)[:2])}"
        elif num in pr_hunks:
            r["overlap_status"] = "pass"

    for r in results:
        r["fail_count"] = sum(1 for s in [r["ci_status"], r["conflict_status"], r["review_status"], r["stale_status"], r["overlap_status"]] if s == "FAIL")

        # Build blocker_icons and issue_snippet for the report template
        icons = []
        snippets = []
        if r["ci_status"] == "FAIL":
            icons.append("CI")
            snippets.append(r["ci_detail"])
        if r["conflict_status"] == "FAIL":
            icons.append("CONFLICT")
            snippets.append(r["conflict_detail"])
        if r["review_status"] == "FAIL":
            icons.append("REVIEW")
            snippets.append(r["review_detail"])
        elif r["review_status"] == "needs_review":
            icons.append("REVIEW?")
            snippets.append("Needs evaluation")
        if r["stale_status"] == "FAIL":
            icons.append("STALE")
            snippets.append(r["stale_detail"])
        if r["overlap_status"] == "FAIL":
            icons.append("OVERLAP")
            snippets.append(r["overlap_detail"])
        r["blocker_icons"] = ", ".join(icons) if icons else "\u2014"
        r["issue_snippet"] = "; ".join(snippets) if snippets else "\u2014"
        # For "Almost Ready" section — single blocker description
        if r["fail_count"] == 1 and icons:
            r["single_blocker"] = icons[0]
            r["what_needed"] = snippets[0] if snippets else "\u2014"
        else:
            r["single_blocker"] = ""
            r["what_needed"] = ""

    for r in results:
        reasons = []
        days = r["days_since_update"]
        if r["isDraft"] and days and days > 21 and r["conflict_status"] == "FAIL":
            reasons.append(f"Draft with conflicts, inactive {days}d")
        if days and days > 60:
            reasons.append(f"Inactive for {days} days")
        if days and days > 30 and r["fail_count"] >= 2:
            reasons.append(f"Stale ({days}d) with {r['fail_count']} blockers")
        if reasons:
            r["recommend_close"] = True
            r["recommend_close_reason"] = "; ".join(reasons)

    results.sort(key=lambda r: (1 if r["isDraft"] else 0, TYPE_PRIORITY.get(r["pr_type"], 99), r["fail_count"], 0 if r["has_priority"] else 1, r["size_score"]))
    for i, r in enumerate(results):
        r["rank"] = i + 1

    review_order = [r["number"] for r in results if not r["isDraft"] and r["fail_count"] == 0 and r["conflict_status"] == "pass"]
    needs_review = [r["number"] for r in results if r["review_status"] == "needs_review"]

    for r in results:
        p = os.path.join(output_dir, str(r["number"]), "analysis.json")
        if os.path.isdir(os.path.join(output_dir, str(r["number"]))):
            with open(p, "w") as f:
                json.dump(r, f, indent=2, ensure_ascii=False)

    non_draft = [r for r in results if not r["isDraft"]]
    stats = {
        "total": len(results), "drafts": len(results) - len(non_draft),
        "clean": sum(1 for r in non_draft if r["fail_count"] == 0),
        "one_blocker": sum(1 for r in non_draft if r["fail_count"] == 1),
        "needs_work": sum(1 for r in non_draft if r["fail_count"] >= 2),
        "recommend_close": sum(1 for r in results if r["recommend_close"]),
        "fork_prs": sum(1 for r in results if r["isFork"]),
        "by_type": {},
    }
    for r in results:
        stats["by_type"][r["pr_type"]] = stats["by_type"].get(r["pr_type"], 0) + 1

    queue = {
        "generated_at": now.strftime("%Y-%m-%dT%H:%M:%S UTC"),
        "stats": stats, "review_order": review_order, "needs_review": needs_review,
        "prs": [{"number": r["number"], "rank": r["rank"], "title": r["title"], "author": r["author"],
                 "pr_type": r["pr_type"], "fail_count": r["fail_count"], "isDraft": r["isDraft"],
                 "isFork": r["isFork"], "review_status": r["review_status"], "recommend_close": r["recommend_close"]}
                for r in results],
    }
    with open(os.path.join(output_dir, "queue.json"), "w") as f:
        json.dump(queue, f, indent=2, ensure_ascii=False)

    print(f"Analysis complete: {stats['total']} PRs")
    print(f"  Clean: {stats['clean']} | One blocker: {stats['one_blocker']} | Needs work: {stats['needs_work']}")
    print(f"  Types: {stats['by_type']}")
    print(f"  Needs review: {len(needs_review)} PRs")
    if review_order:
        print(f"  Review order: {' -> '.join(f'#{n}' for n in review_order[:10])}")


if __name__ == "__main__":
    main()
