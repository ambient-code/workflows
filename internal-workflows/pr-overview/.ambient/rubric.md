# PR Review Workflow — Execution Efficiency Rubric

This rubric evaluates how efficiently the PR review agent executed the workflow. It is triggered after the merge meeting report is written. The purpose is to identify inefficiencies — wasted tool calls, workarounds, truncation issues, failed commands — so the workflow can be continuously improved. The output is a score out of 25 (aggregate of 5 criteria at 5 points each) and a brief explanation.

---

## Criterion 1: Data Pipeline Efficiency (1-5 points)

Did the fetch and analysis scripts run cleanly without manual intervention?

- **Score 1**: Scripts failed entirely. Agent had to rewrite or replace them from scratch.
- **Score 2**: Scripts ran but with errors (jq failures, missing fields, scope issues). Agent wrote workaround scripts to re-fetch data.
- **Score 3**: Scripts completed but with warnings (Unicode sanitization needed, some PRs had empty data). Agent handled it without major workarounds.
- **Score 4**: Scripts ran cleanly. Minor issues (e.g., one PR failed to fetch) resolved by the script's own error handling.
- **Score 5**: Both `fetch-prs.sh` and `analyze-prs.py` ran in a single call each with no errors, no workarounds, and no manual re-runs.

**Red flags**: Agent writing its own fetch/analysis Python script instead of using the provided ones. Re-running the same script multiple times. Manually fetching individual PRs.

---

## Criterion 2: Context Management (1-5 points)

Did the agent avoid flooding its context with large data?

- **Score 1**: Agent read raw PR files (50KB+) directly into its context. Multiple "output too large" truncation errors. Critical data was lost.
- **Score 2**: Agent read analysis.json when it was too large, causing truncation. Had to re-read with offset/limit workarounds.
- **Score 3**: Agent used the split file structure (analysis.json summary + per-PR files) but read more files than necessary — e.g., reading all 49 PR detail files instead of just the ones needed.
- **Score 4**: Agent read only the summary and the specific per-PR files needed. Used sub-agents for review evaluation. Minor unnecessary reads.
- **Score 5**: Agent read the compact summary once, delegated review evaluation to parallel sub-agents, and only read individual analysis files for report generation. Zero truncation, zero wasted reads.

**Red flags**: "Output too large" messages. Agent reading `prs/{number}.json` directly instead of `reviews/{number}/` comment files. Reading the same file multiple times.

---

## Criterion 3: Tool Call Economy (1-5 points)

Did the agent complete the workflow in a reasonable number of tool calls?

- **Score 1**: 50+ tool calls. Extensive thrashing — rewriting scripts, debugging edge cases inline, running analysis multiple times.
- **Score 2**: 40-49 tool calls. Significant wasted calls on exploration, debugging, or re-doing completed work.
- **Score 3**: 30-39 tool calls. Some unnecessary investigation but generally on track. Maybe read a few extra files or ran extra verification commands.
- **Score 4**: 20-29 tool calls. Efficient execution with minimal waste. Used parallel sub-agents where appropriate.
- **Score 5**: Under 20 tool calls. Ran scripts, delegated review to sub-agents, synced milestone, wrote report, updated milestone description — all with no wasted steps.

**Benchmark**: The ideal workflow is approximately:
1. Read CLAUDE.md + template (2 calls)
2. Run fetch-prs.sh (1 call)
3. Run analyze-prs.py (1 call)
4. Spawn parallel sub-agents for review evaluation (1-3 calls)
5. Run test-merge-order.sh (1 call)
6. Find/create milestone + sync PRs (2-3 calls)
7. Read analysis summary + needed per-PR files (3-5 calls)
8. Write report (1 call)
9. Update milestone description (1 call)
Total: ~15-20 calls

---

## Criterion 4: Error Recovery (1-5 points)

When something went wrong, did the agent recover gracefully or spiral?

- **Score 1**: A single error caused the agent to abandon the approach entirely and start over with a different strategy (e.g., rewriting the analysis script from scratch).
- **Score 2**: Errors caused multi-step debugging sessions (5+ tool calls to diagnose and fix a single issue).
- **Score 3**: Agent encountered errors and recovered within 2-3 tool calls but wasted time on the wrong diagnosis first.
- **Score 4**: Agent encountered a minor error and recovered in 1 call (e.g., a missing file, retried with correct path).
- **Score 5**: No errors encountered, or the agent's first recovery attempt succeeded immediately.

**Red flags**: Agent writing replacement scripts when the provided one fails. Retrying the same failing command. Long debugging chains where the agent tries multiple hypotheses before finding the issue.

---

## Criterion 5: Completeness (1-5 points)

Did the agent complete ALL 8 checklist items?

- **Score 1**: Completed 4 or fewer items. Major deliverables missing (no report, no milestone update).
- **Score 2**: Completed 5-6 items. Report was written but milestone was not updated, or review evaluation was skipped.
- **Score 3**: Completed 7 items. One step was skipped or done incorrectly (e.g., milestone synced but description not updated).
- **Score 4**: All 8 items completed but with minor issues (e.g., merge test skipped because script wasn't found, report missing one section).
- **Score 5**: All 8 items completed correctly: fetch → analyze → review evaluation → merge test → milestone find/create → milestone sync → write report → update milestone description.

**The 8 checklist items**:
1. Run fetch-prs.sh
2. Run analyze-prs.py
3. Evaluate review comments (via sub-agents)
4. Run test-merge-order.sh
5. Find or create Merge Queue milestone
6. Sync PRs to milestone
7. Write the merge meeting report
8. Update milestone description with the report
