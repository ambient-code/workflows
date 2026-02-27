# Merge Meeting — {{REPO}}

**Date:** {{DATE}}
**Open PRs:** {{TOTAL_PRS}} | **Clean (no blockers):** {{CLEAN_COUNT}} | **In Merge Queue:** {{MILESTONE_COUNT}}

### At a Glance

{{AT_A_GLANCE}}

---

## Clean PRs ({{CLEAN_COUNT}})

> Ready to merge — listed in recommended merge order (smallest and least conflicting first).

| # | PR | Author | Size | Updated | Notes |
|---|---|---|---|---|---|
{{#each CLEAN_PR_ROWS}}
| {{RANK}} | [#{{NUMBER}}]({{URL}}) — {{TITLE}} | {{AUTHOR}} | {{SIZE}} | {{UPDATED}} | {{NOTES}} |
{{/each}}

---

## PRs With Blockers

{{#each BLOCKER_PR_ENTRIES}}

### {{RANK}}. [#{{NUMBER}}]({{URL}}) — {{TITLE}}

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

{{#if RECOMMEND_CLOSE_ENTRIES}}
## Recommend Closing

> These PRs appear abandoned, superseded, or too stale to be worth maintaining. Use your judgment — close or ping the author.

| PR | Author | Reason | Last Updated |
|---|---|---|---|
{{#each RECOMMEND_CLOSE_ENTRIES}}
| [#{{NUMBER}}]({{URL}}) — {{TITLE}} | {{AUTHOR}} | {{REASON}} | {{UPDATED}} |
{{/each}}

---

{{/if}}

## Summary

- **Ready now:** {{CLEAN_COUNT}} PRs with zero blockers
- **In Merge Queue:** {{MILESTONE_COUNT}} PRs
- **One blocker away:** {{NEAR_COUNT}} PRs
- **Needs work:** {{WORK_COUNT}} PRs
- **Recommend closing:** {{CLOSE_COUNT}} PRs
