# Bugfix Guidance — eval-hub/eval-hub
<!-- last-analyzed: 2026-03-29 | bugfix-merged: 48 | bugfix-closed: 4 -->

## Titles
`fix: <lowercase description>` (39/48 merged)
`fix(<scope>): <lowercase description>` (9/48 merged — use when change is scoped)

## Branches
No strict convention enforced. Common patterns:
- Short descriptive: `adapter-mode`, `storage-fix`, `tenant-filter` (~33/48)
- Prefixed: `fix-<description>` (~10/48) or `fix/<description>` (~5/48)

## Scope Values
Use fix(<scope>) when the change is confined to one subsystem (from 9 merged PRs):
`sidecar` | `collections` | `storage` | `k8s` | `cli` | `build` | `cancel` | `ci` | `mlflow`

## Test Requirements
Go source file changes must include corresponding `_test.go` files (~36/48 merged):
- `evaluations.go` → `evaluations_test.go` (6+ PRs)
- `job_builders.go` → `job_builders_test.go` (6+ PRs)
- `collections.go` → `collections_test.go` (3+ PRs)
- `loader.go` → `loader_test.go` (2+ PRs)

Handler/runtime changes should also update BDD feature files (10+ PRs):
- `tests/features/*.feature`
- `tests/features/step_definitions_test.go`
- `tests/kubernetes/features/` for k8s runtime changes (4+ PRs)

## Co-Changes
- `internal/runtimes/k8s/job_builders.go` → always include `job_builders_test.go` (6/6 PRs)
- `internal/storage/sql/*.go` → always include `*_test.go` counterpart (5/5 PRs)

## Don'ts
- Don't submit docs-only changes via fix/ branches — 2 closed PRs rejected as "not required" / "not relevant here" (#369, #368)
