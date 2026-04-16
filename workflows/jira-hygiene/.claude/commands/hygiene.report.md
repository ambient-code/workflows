# /hygiene.report - Generate Master Hygiene Report

## Purpose

Generate a comprehensive master report that combines all hygiene checks into a single dashboard view. This provides an at-a-glance overview of all project hygiene issues.

## Prerequisites

- `/hygiene.setup` must be run first

## Arguments

Optional:
- `--output <path>` - Custom output path (default: artifacts/jira-hygiene/reports/master-report.md)
- `--format <md|html>` - Output format (default: md)

## Process

1. **Load configuration**:
   - Read `artifacts/jira-hygiene/config.json`
   - Extract base_jql and settings

2. **Run all hygiene checks WITH PAGINATION** (read-only queries):

   **Note**: All queries use base_jql and paginate to fetch complete counts
   
   **Standard pagination pattern for each query**:
   ```
   all_results = []
   start_at = 0
   max_results = 50
   
   Loop:
     response = GET /rest/api/3/search?jql={jql}&startAt={start_at}&maxResults={max_results}
     results = response['issues']
     all_results.extend(results)
     
     if start_at + len(results) >= response['total']:
       break
     
     start_at += max_results
     sleep(0.5)
   ```

   a. **Orphaned Stories WITH PAGINATION**:
      ```jql
      ({base_jql}) AND issuetype = Story AND "Epic Link" is EMPTY
      ```
      - Paginate to count ALL orphaned stories
      - List top 5 by age

   b. **Orphaned Epics WITH PAGINATION**:
      ```jql
      ({base_jql}) AND issuetype = Epic AND "Parent Link" is EMPTY
      ```
      - Paginate to count ALL orphaned epics
      - List top 5 by age

   c. **Blocking Tickets WITH PAGINATION**:
      ```jql
      ({base_jql}) AND issueFunction in linkedIssuesOf("({base_jql})", "blocks")
      ```
      - Paginate to count ALL blocking tickets
      - Count tickets being blocked
      - List all with blocked ticket counts

   d. **Stale Tickets BY PRIORITY WITH PAGINATION**:
      - For each priority: `({base_jql}) AND priority = {PRIORITY} AND updated < -{DAYS}d`
      - Apply configured thresholds
      - Paginate each priority query separately
      - Count by priority level
      - List top 5 oldest per priority

   e. **Untriaged Items WITH PAGINATION**:
      ```jql
      ({base_jql}) AND status = New AND created < -7d
      ```
      - Paginate to count ALL untriaged
      - List top 5 by age

   f. **Blocking-Closed Mismatches WITH PAGINATION**:
      - Query blocking tickets (with pagination)
      - For each, check if all blocked items are closed
      - Count mismatches
      - List all

   g. **In-Progress Unassigned WITH PAGINATION**:
      ```jql
      ({base_jql}) AND status = "In Progress" AND assignee is EMPTY
      ```
      - Paginate to count ALL
      - List all

   h. **Missing Activity Type WITH PAGINATION**:
      ```jql
      ({base_jql}) AND "{activity_type_field_id}" is EMPTY
      ```
      - Use activity_type_field_id from config.json (e.g., "customfield_10050")
      - Paginate to count ALL
      - List top 10 by priority

3. **Calculate health score**:
   
   **Scoring formula**:
   - Start with 100 points
   - Deduct points for each issue:
     - Orphaned story: -0.5 points
     - Orphaned epic: -1 point
     - Blocking ticket: -2 points
     - Stale ticket (High): -1 point
     - Stale ticket (Medium): -0.5 points
     - Stale ticket (Low): -0.25 points
     - Untriaged item: -0.5 points
     - Blocking-closed mismatch: -1 point
     - In-progress unassigned: -1 point
     - Missing activity type: -0.25 points
   - Minimum score: 0
   
   **Score interpretation**:
   - 90-100: Excellent (🟢)
   - 70-89: Good (🟡)
   - 50-69: Needs Attention (🟠)
   - 0-49: Critical (🔴)

4. **Generate master report**:
   - Write to `artifacts/jira-hygiene/reports/master-report.md`
   - Include:
     - Executive summary with health score
     - Quick stats dashboard
     - Detailed sections for each category
     - Recommended actions (which commands to run)
     - Links to detailed reports
     - JQL search links for each category

5. **Display summary**:
   ```
   Project Hygiene Report: {PROJECT}
   Health Score: {SCORE}/100 ({RATING})
   
   Issues Found:
   • {N} orphaned stories
   • {N} orphaned epics
   • {N} blocking tickets
   • {N} stale tickets
   • {N} untriaged items
   • {N} blocking-closed mismatches
   • {N} in-progress unassigned
   • {N} missing activity types
   
   Full report: artifacts/jira-hygiene/reports/master-report.md
   ```

## Output

- `artifacts/jira-hygiene/reports/master-report.md` (or custom path)

## Example Master Report

```markdown
# Jira Hygiene Master Report: PROJ

**Generated**: 2026-04-07 10:30 UTC  
**Health Score**: 73/100 🟡 Good  
**[View Project in Jira](https://company.atlassian.net/projects/PROJ)**

---

## Executive Summary

Your project has **good** overall hygiene with some areas needing attention. The main issues are:
- 15 orphaned stories need epic links
- 8 stale medium-priority tickets ready for closure
- 3 blocking tickets preventing other work

**Recommended Actions**:
1. Run `/hygiene.link-epics` to link 15 orphaned stories
2. Run `/hygiene.close-stale` to close 12 stale tickets
3. Review 3 blocking tickets manually

---

## Quick Stats Dashboard

| Category | Count | Status | Action |
|----------|-------|--------|--------|
| Orphaned Stories | 15 | 🟡 | [Link to epics](#orphaned-stories) |
| Orphaned Epics | 2 | 🟢 | [Link to initiatives](#orphaned-epics) |
| Blocking Tickets | 3 | 🟡 | [Review](#blocking-tickets) |
| Stale Tickets | 12 | 🟠 | [Close stale](#stale-tickets) |
| Untriaged Items | 5 | 🟡 | [Triage](#untriaged-items) |
| Blocking-Closed | 1 | 🟢 | [Review](#blocking-closed-mismatches) |
| In-Progress Unassigned | 2 | 🟢 | [Assign](#in-progress-unassigned) |
| Missing Activity Type | 8 | 🟡 | [Set type](#missing-activity-type) |

**Status Legend**: 🟢 Good (0-5) | 🟡 Monitor (6-15) | 🟠 Action Needed (16-30) | 🔴 Critical (30+)

---

## Orphaned Stories

**Count**: 15 stories  
**Impact**: Stories without epic links are hard to organize and prioritize  
**[View in Jira](https://company.atlassian.net/issues/?jql=project+%3D+PROJ+AND+issuetype+%3D+Story+AND+%22Epic+Link%22+is+EMPTY)**

**Oldest 5**:

| Story | Summary | Age | Priority |
|-------|---------|-----|----------|
| [PROJ-123](https://company.atlassian.net/browse/PROJ-123) | Implement user login | 45d | High |
| [PROJ-145](https://company.atlassian.net/browse/PROJ-145) | Add export feature | 38d | Medium |
| [PROJ-167](https://company.atlassian.net/browse/PROJ-167) | Fix broken link | 32d | Low |
| [PROJ-189](https://company.atlassian.net/browse/PROJ-189) | Update documentation | 28d | Low |
| [PROJ-201](https://company.atlassian.net/browse/PROJ-201) | Improve performance | 25d | High |

**Recommended Action**: Run `/hygiene.link-epics`

---

## Orphaned Epics

**Count**: 2 epics  
**Impact**: Epics without initiative links lack strategic alignment  
**[View in Jira](https://company.atlassian.net/issues/?jql=project+%3D+PROJ+AND+issuetype+%3D+Epic+AND+%22Parent+Link%22+is+EMPTY)**

**All Orphaned Epics**:

| Epic | Summary | Age | Story Count |
|------|---------|-----|-------------|
| [EPIC-12](https://company.atlassian.net/browse/EPIC-12) | Payment Integration | 60d | 8 stories |
| [EPIC-15](https://company.atlassian.net/browse/EPIC-15) | Mobile App | 45d | 5 stories |

**Recommended Action**: Run `/hygiene.link-initiatives`

---

## Blocking Tickets

**Count**: 3 tickets blocking 5 other tickets  
**Impact**: Work is blocked, preventing progress on 5 tickets  
**[View in Jira](https://company.atlassian.net/issues/?jql=project+%3D+PROJ+AND+issueFunction+in+linkedIssuesOf%28%22project+%3D+PROJ%22%2C+%22blocks%22%29)**

**All Blocking Tickets**:

| Blocking Ticket | Summary | Blocks | Assignee | Status |
|-----------------|---------|--------|----------|--------|
| [PROJ-50](https://company.atlassian.net/browse/PROJ-50) | Database migration | [PROJ-51](https://company.atlassian.net/browse/PROJ-51), [PROJ-52](https://company.atlassian.net/browse/PROJ-52) | John Doe | In Progress |
| [PROJ-75](https://company.atlassian.net/browse/PROJ-75) | Security audit | [PROJ-80](https://company.atlassian.net/browse/PROJ-80) | Unassigned | To Do |
| [PROJ-90](https://company.atlassian.net/browse/PROJ-90) | API changes | [PROJ-91](https://company.atlassian.net/browse/PROJ-91), [PROJ-92](https://company.atlassian.net/browse/PROJ-92) | Jane Smith | Code Review |

**Recommended Action**: Review progress, assign unassigned blockers

---

## Stale Tickets

**Count**: 12 tickets (by priority)  
**Impact**: Cluttering backlog, unclear if still relevant  

**Breakdown by Priority**:

| Priority | Threshold | Count | Oldest |
|----------|-----------|-------|--------|
| High | 7 days | 2 | 15d |
| Medium | 14 days | 8 | 45d |
| Low | 30 days | 2 | 60d |

**Top 5 Oldest**:

| Ticket | Summary | Priority | Days Stale |
|--------|---------|----------|------------|
| [PROJ-100](https://company.atlassian.net/browse/PROJ-100) | Old feature request | Low | 60d |
| [PROJ-110](https://company.atlassian.net/browse/PROJ-110) | Performance issue | Medium | 45d |
| [PROJ-120](https://company.atlassian.net/browse/PROJ-120) | UI bug | Medium | 38d |
| [PROJ-130](https://company.atlassian.net/browse/PROJ-130) | Documentation update | Medium | 32d |
| [PROJ-140](https://company.atlassian.net/browse/PROJ-140) | Integration request | Medium | 28d |

**Recommended Action**: Run `/hygiene.close-stale`

---

## Untriaged Items

**Count**: 5 items in "New" status for >7 days  
**Impact**: Backlog not properly prioritized  
**[View in Jira](https://company.atlassian.net/issues/?jql=project+%3D+PROJ+AND+status+%3D+New+AND+created+%3C+-7d)**

**All Untriaged**:

| Ticket | Summary | Age | Reporter |
|--------|---------|-----|----------|
| [PROJ-200](https://company.atlassian.net/browse/PROJ-200) | Add export feature | 12d | John Doe |
| [PROJ-201](https://company.atlassian.net/browse/PROJ-201) | Fix broken link | 10d | Jane Smith |
| [PROJ-202](https://company.atlassian.net/browse/PROJ-202) | Improve performance | 9d | Bob Johnson |
| [PROJ-203](https://company.atlassian.net/browse/PROJ-203) | New integration | 8d | Alice Lee |
| [PROJ-204](https://company.atlassian.net/browse/PROJ-204) | Update docs | 8d | John Doe |

**Recommended Action**: Run `/hygiene.triage-new`

---

## Blocking-Closed Mismatches

**Count**: 1 ticket  
**Impact**: Blocker may be ready to close  

**All Mismatches**:

| Blocking Ticket | Summary | Blocks (All Closed) |
|-----------------|---------|---------------------|
| [PROJ-300](https://company.atlassian.net/browse/PROJ-300) | Security audit | [PROJ-305](https://company.atlassian.net/browse/PROJ-305) (closed 5d ago) |

**Recommended Action**: Review and close or update links

---

## In-Progress Unassigned

**Count**: 2 tickets  
**Impact**: Unclear ownership, work may be abandoned  
**[View in Jira](https://company.atlassian.net/issues/?jql=project+%3D+PROJ+AND+status+%3D+%22In+Progress%22+AND+assignee+is+EMPTY)**

**All Unassigned**:

| Ticket | Summary | Status | Age |
|--------|---------|--------|-----|
| [PROJ-400](https://company.atlassian.net/browse/PROJ-400) | Refactor module | In Progress | 8d |
| [PROJ-401](https://company.atlassian.net/browse/PROJ-401) | API endpoint | In Progress | 5d |

**Recommended Action**: Assign or move back to backlog

---

## Missing Activity Type

**Count**: 8 tickets  
**Impact**: Reporting and categorization incomplete  

**Top 10 by Priority**:

| Ticket | Summary | Priority | Issue Type |
|--------|---------|----------|------------|
| [PROJ-500](https://company.atlassian.net/browse/PROJ-500) | Fix login bug | High | Bug |
| [PROJ-501](https://company.atlassian.net/browse/PROJ-501) | Document API | Medium | Task |
| [PROJ-502](https://company.atlassian.net/browse/PROJ-502) | Add feature | Medium | Story |
| [PROJ-503](https://company.atlassian.net/browse/PROJ-503) | Update system | Low | Task |
| [PROJ-504](https://company.atlassian.net/browse/PROJ-504) | Research spike | Low | Task |
| [PROJ-505](https://company.atlassian.net/browse/PROJ-505) | Test automation | Low | Task |

**Recommended Action**: Run `/hygiene.activity-type`

---

## Health Score Breakdown

**Total Score**: 73/100 🟡 Good

**Deductions**:
- Orphaned stories (15 × 0.5): -7.5 points
- Orphaned epics (2 × 1): -2 points
- Blocking tickets (3 × 2): -6 points
- Stale High (2 × 1): -2 points
- Stale Medium (8 × 0.5): -4 points
- Stale Low (2 × 0.25): -0.5 points
- Untriaged (5 × 0.5): -2.5 points
- Blocking-closed (1 × 1): -1 point
- In-progress unassigned (2 × 1): -2 points
- Missing activity type (8 × 0.25): -2 points

**Total Deductions**: -27 points

---

## Next Steps

**Priority 1 - High Impact** (address first):
1. `/hygiene.link-epics` - Link 15 orphaned stories
2. Review 3 blocking tickets - Unblock 5 downstream tickets

**Priority 2 - Medium Impact** (address this week):
3. `/hygiene.close-stale` - Close 12 stale tickets
4. `/hygiene.triage-new` - Triage 5 items

**Priority 3 - Low Impact** (address as time allows):
5. `/hygiene.link-initiatives` - Link 2 orphaned epics
6. `/hygiene.activity-type` - Set activity type for 8 tickets
7. Assign 2 in-progress tickets
8. Review 1 blocking-closed mismatch

**Estimated Time**: 30-45 minutes to address all issues

---

## Report Details

**Project**: PROJ  
**Generated**: 2026-04-07 10:30 UTC  
**Total Unresolved Tickets**: 250  
**Issues Found**: 48 (19% of tickets need hygiene attention)

**Related Reports**:
- [Blocking Tickets](./blocking-tickets.md)
- [Blocking-Closed Mismatches](./blocking-closed-mismatch.md)
- [In-Progress Unassigned](./unassigned-progress.md)
```

## Notes

- All queries are read-only (no modifications made)
- Health score is a guideline, not absolute measure
- Customize thresholds via config.json
- Run this report weekly for ongoing hygiene monitoring
- Consider adding to cron for automated reporting
