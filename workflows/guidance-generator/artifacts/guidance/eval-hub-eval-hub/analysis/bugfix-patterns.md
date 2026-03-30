# Bugfix PR Pattern Analysis — eval-hub/eval-hub
<!-- analyzed: 2026-03-29 | bugfix-merged: 48 | bugfix-closed: 4 -->

## Data Summary
- 48 merged, 4 closed bugfix PRs analyzed
- Threshold applied: 3+ PRs per rule

## TITLE_FORMAT
Primary: `fix: <lowercase description>` (39/48 merged)
Scoped:  `fix(<scope>): <lowercase description>` (9/48 merged)
No other prefix patterns observed.

## SCOPE_VALUES
sidecar, collections, storage, k8s, cli, build, cancel, ci, mlflow (9 scoped PRs)

## BRANCH_FORMAT
No strict convention. Patterns:
- Short descriptive (no prefix): ~33/48 (adapter-mode, storage-fix, tenant-filter)
- `fix-<description>`: ~10/48 (fix-sidecar-shutdown, fix-lighteval)
- `fix/<description>`: ~5/48 (fix/cancel-should-fail-unit-benchmarks)

## TEST_FILES_REQUIRED
Go source changes almost always paired with `_test.go` counterparts (~36/48 merged)
- evaluations.go + evaluations_test.go (6+ PRs)
- job_builders.go + job_builders_test.go (6+ PRs)
- collections.go + collections_test.go (3+ PRs)

## FEATURE_TESTS
PRs touching handler/runtime behavior include BDD test files (10+ PRs):
- tests/features/*.feature
- tests/features/step_definitions_test.go

## CO_CHANGE_k8s
job_builders.go always paired with job_builders_test.go (6/6 PRs)

## CO_CHANGE_storage
SQL storage changes always paired with *_test.go files (5/5 PRs)

## LABELS
kind/fix: 11/48 PRs (23%) — optional, inconsistently applied

## DONT_docs_only_via_fix_branch
2 closed PRs rejected for docs-only content via fix/ branches:
- #369 closed "not required", #368 closed "not relevant here"
