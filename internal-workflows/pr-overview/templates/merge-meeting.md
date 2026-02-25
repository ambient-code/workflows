# Merge Meeting — {{REPO}}

**Date:** {{DATE}}
**Open PRs:** {{TOTAL_PRS}} | **Clean (no blockers):** {{CLEAN_COUNT}}

> PRs ranked by merge readiness — fewest blockers first, then by priority signals and size.

---

{{#each PR_ENTRIES}}

## {{RANK}}. [#{{NUMBER}}]({{URL}}) — {{TITLE}}

**Author:** {{AUTHOR}} | **Size:** {{SIZE}} | **Updated:** {{UPDATED}} | **Branch:** `{{BRANCH}}`

| Blocker | Status | Detail |
|---------|--------|--------|
| CI | {{CI_STATUS}} | {{CI_DETAIL}} |
| Merge conflicts | {{CONFLICT_STATUS}} | {{CONFLICT_DETAIL}} |
| Human review comments | {{HUMAN_REVIEW_STATUS}} | {{HUMAN_REVIEW_DETAIL}} |
| Agent review issues | {{AGENT_REVIEW_STATUS}} | {{AGENT_REVIEW_DETAIL}} |
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
- **One blocker away:** {{NEAR_COUNT}} PRs
- **Needs work:** {{WORK_COUNT}} PRs
- **Recommend closing:** {{CLOSE_COUNT}} PRs (stale / superseded)
