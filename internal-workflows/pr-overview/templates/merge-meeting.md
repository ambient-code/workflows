# Merge Meeting — {{REPO}}

**Date:** {{DATE}}
**Open PRs:** {{TOTAL_PRS}} | **Clean (no blockers):** {{CLEAN_COUNT}} | **In Merge Queue:** {{MILESTONE_COUNT}}

> PRs ranked by merge readiness — fewest blockers first, then by priority signals and size.

---

{{#each PR_ENTRIES}}

## {{RANK}}. [#{{NUMBER}}]({{URL}}) — {{TITLE}}

**Author:** {{AUTHOR}} | **Size:** {{SIZE}} | **Updated:** {{UPDATED}} | **Branch:** `{{BRANCH}}`

| Blocker | Status | Detail |
|---------|--------|--------|
| CI | {{CI_STATUS}} | {{CI_DETAIL}} |
| Merge conflicts | {{CONFLICT_STATUS}} | {{CONFLICT_DETAIL}} |
| Review comments | {{REVIEW_STATUS}} | {{REVIEW_DETAIL}} |
| Jira hygiene | {{JIRA_STATUS}} | {{JIRA_DETAIL}} |
| Staleness | {{STALE_STATUS}} | {{STALE_DETAIL}} |
| Diff overlap risk | {{OVERLAP_STATUS}} | {{OVERLAP_DETAIL}} |

{{#if NOTES}}
> {{NOTES}}
{{/if}}

---

{{/each}}

## Summary

- **Ready now:** {{CLEAN_COUNT}} PRs with zero blockers
- **In Merge Queue:** {{MILESTONE_COUNT}} PRs
- **One blocker away:** {{NEAR_COUNT}} PRs
- **Needs work:** {{WORK_COUNT}} PRs
- **Recommend closing:** {{CLOSE_COUNT}} PRs (stale / superseded)
