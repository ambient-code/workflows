# Document Review Workflow

Systematic workflow for reviewing a project's documentation — assessing quality, completeness, accuracy, and consistency, then generating actionable findings and fixes.

## Features

- Auto-discovers all documentation files across the project
- Evaluates docs against 7 quality dimensions
- Classifies findings by severity for prioritized action
- Cross-references documentation claims against source code
- Runs review, verify, and install-test in parallel as sub-agents for speed
- Executes installation instructions on a live cluster to verify accuracy
- Interacts with the installed project as a user would to verify usage docs
- Tracks common installation errors and their solutions for fix generation
- Automatically reverts cluster changes after install-test via cleanup agent
- Validates sub-agent output and retries on quality failures
- Generates inline fix suggestions grouped by file
- Supports a speedrun mode for one-shot review

## Directory Structure

```text
workflows/document-review/
├── .ambient/
│   └── ambient.json              # Workflow configuration
├── .claude/
│   ├── commands/
│   │   ├── scan.md               # Discover and catalog docs
│   │   ├── review.md             # Quality review
│   │   ├── verify.md             # Code cross-referencing
│   │   ├── report.md             # Consolidated report
│   │   ├── fix.md                # Fix suggestions
│   │   ├── create-prs.md         # PR creation
│   │   ├── install-test.md       # Installation testing
│   │   ├── usage-test.md         # Post-install usage testing
│   │   ├── cleanup.md            # Cluster cleanup
│   │   └── speedrun.md           # Full pipeline
│   └── skills/
│       ├── controller/SKILL.md   # Phase orchestration
│       ├── scan/SKILL.md         # Document discovery
│       ├── review/SKILL.md       # Quality evaluation
│       ├── verify/SKILL.md       # Source code verification
│       ├── install-test/SKILL.md # Installation instruction testing
│       ├── usage-test/SKILL.md   # Post-install usage verification
│       ├── cleanup/SKILL.md      # Cluster change reversal
│       ├── validate/SKILL.md     # Output validation
│       ├── report/SKILL.md       # Report generation
│       ├── fix/SKILL.md          # Fix suggestion generation
│       └── create-prs/SKILL.md   # PR creation from fixes
├── templates/                    # Output format templates
│   ├── inventory.md
│   ├── findings-review.md
│   ├── findings-verify.md
│   ├── findings-install-test.md
│   ├── findings-usage-test.md
│   ├── cluster-changes.md
│   ├── cleanup-report.md
│   ├── report.md
│   ├── fixes.md
│   └── pr-log.md
├── CLAUDE.md                     # Behavioral context
└── README.md                     # This file
```

## Commands

| Command | Purpose |
|---------|---------|
| `/scan` | Discover and catalog all documentation in the project |
| `/review` | Deep quality review against 7 dimensions |
| `/verify` | Cross-reference docs against source code (optional) |
| `/install-test` | Execute installation instructions on a cluster (optional) |
| `/usage-test` | Interact with the installed project and verify usage docs (optional) |
| `/cleanup` | Revert cluster changes from install-test and usage-test (runs automatically) |
| `/report` | Consolidate all findings into a deduplicated report |
| `/fix` | Generate inline fix suggestions (optional) |
| `/create-prs` | Create GitHub pull requests from fix suggestions (optional) |
| `/speedrun` | Run scan → review + verify + install-test → usage-test → cleanup → report in one shot |

## Workflow Phases

```text
scan ──┬──> review (sub-agent) ──────────────────┬──> validate ──> report ──> fix ──> create-prs
       ├──> verify (sub-agent) ──────────────────┤       ↑  │
       └──> install-test (sub-agent) ────────────┘       └──┘
                    │                                (retry on fail,
                    ├──> usage-test (if succeeded)    max 1 retry)
                    └──> cleanup
```

Review, verify, and install-test are independent after scan — they run in parallel as sub-agents, each writing to its own findings file. After a successful install-test, a usage-test agent interacts with the installed project as a user would, verifying that usage documentation matches the actual experience. A cleanup agent then reverts all cluster changes from both install-test and usage-test using the change log. A validation sub-agent checks findings output for coverage, structure, and evidence quality, retrying failed agents once before proceeding.

### 1. Scan

Discovers all documentation files using glob patterns. Catalogs each file by path, format, topic, audience, and whether it contains executable instructions. Produces an inventory.

### 2. Review

Deep-reads each document evaluating 7 quality dimensions: accuracy, completeness, consistency, clarity, currency, structure, and examples. Identifies target audience per document and assesses audience-appropriateness. Classifies findings by severity.

### 3. Verify (Optional)

Cross-references documentation claims against actual source code. Checks CLI flags, API endpoints, configuration options, default values, and behavior descriptions. Flags undocumented features found in code.

### 4. Install-test (Optional)

Executes documented installation instructions on a live OpenShift cluster. Compares actual results against documented expectations step by step. When a step fails, troubleshoots the root cause to determine the correct procedure. Tracks every error a user might encounter along with its solution, producing a troubleshooting guide that `/fix` uses to add error-handling guidance to the documentation. Logs all cluster changes to a change log for cleanup.

### 5. Usage-test (Optional)

Runs automatically after a successful install-test. Interacts with the installed project as a user would — executing documented API calls, CLI commands, workflows, and interactions on the live cluster. Compares the actual user experience against what the documentation describes. Appends cluster changes to the same change log for cleanup. Produces a troubleshooting guide that `/fix` uses to add error-handling guidance to usage documentation.

### 6. Cleanup (Automatic)

Runs automatically after usage-test and install-test complete. Reads the cluster change log and reverts all modifications in reverse order — deleting created resources, restoring modified resources, and undoing shell script effects. Reports any changes that could not be reverted so the user can clean up manually.

### 8. Report

Consolidates all findings from review, verify, install-test, and usage-test into a single deduplicated report. Findings are grouped by severity (Critical → Low) with a dimension × severity summary table. Reads from whichever findings files exist.

### 9. Fix (Optional)

Generates inline fix suggestions for each finding. Quotes problematic text, provides replacement, and explains rationale. Groups suggestions into pull request units with automatable classification and self-contained context for reliable text matching.

### 10. Create PRs (Optional)

Creates draft GitHub pull requests from automatable fix suggestions. Only fixes classified as `Automatable: Yes` are applied — non-automatable fixes that need human decisions are skipped entirely. All PRs are created as drafts so a human reviewer can verify the changes before merging. Produces a PR log tracking what was created and any fixes skipped.

## Quality Dimensions

| Dimension | What It Checks |
|-----------|---------------|
| Accuracy | Do docs match reality? |
| Completeness | Are there gaps or missing docs? |
| Consistency | Do docs agree with each other? |
| Clarity | Is language clear for the audience? |
| Currency | Dead links, deprecated refs? |
| Structure | Logical organization? |
| Examples | Code samples present and correct? |

## Finding Severities

| Severity | Definition |
|----------|-----------|
| Critical | Incorrect information, broken commands, or missing steps that block users |
| High | Significant gaps, contradictions, or outdated content |
| Medium | Issues that cause confusion but have workarounds |
| Low | Minor improvements to clarity, structure, or presentation |

## Output Artifacts

Output files are written to `artifacts/`:

| File | Content |
|------|---------|
| `artifacts/inventory.md` | Documentation file catalog |
| `artifacts/findings-review.md` | Detailed findings by document |
| `artifacts/findings-verify.md` | Code verification findings |
| `artifacts/findings-install-test.md` | Installation test findings and troubleshooting guide |
| `artifacts/findings-usage-test.md` | Usage test findings and troubleshooting guide |
| `artifacts/cluster-changes.md` | Log of all cluster modifications for cleanup |
| `artifacts/cleanup-report.md` | Cleanup results and any failed reverts |
| `artifacts/report.md` | Consolidated findings report |
| `artifacts/fixes.md` | Inline fix suggestions with PR grouping |
| `artifacts/pr-log.md` | Created PR links and status |

## Prerequisites

Most phases require only read access to the target project. The optional
phases have additional requirements:

| Phase | Requirement |
|-------|-------------|
| `/install-test`, `/usage-test`, `/cleanup` | `$CLUSTER_URL`, `$CLUSTER_USERNAME`, `$CLUSTER_PASSWORD` (see below) |
| `/create-prs` | `$GITHUB_TOKEN` with permission to fork, push, and open PRs (see below) |

### Cluster Credentials for `/install-test` and `/usage-test`

The `/install-test` phase executes documented installation instructions on a
live OpenShift cluster. After a successful install, `/usage-test` interacts
with the installed project to verify usage documentation. `/cleanup` then
reverts all cluster changes.

These phases require three environment variables:

```bash
export CLUSTER_URL=https://api.my-cluster.example.com:6443
export CLUSTER_USERNAME=admin
export CLUSTER_PASSWORD=secret
```

The workflow logs in with:

```bash
oc login -u "$CLUSTER_USERNAME" -p "$CLUSTER_PASSWORD" --server="$CLUSTER_URL"
```

When these variables are not set, the controller skips install-test and
usage-test automatically — the remaining phases (scan, review, verify, report,
fix) work without cluster access.

### GitHub Token for `/create-prs`

The `/create-prs` phase forks the target repository, pushes branches to the
fork, and opens draft pull requests against the upstream repository. This
requires a GitHub token with the right scopes.

**Classic Personal Access Token (recommended):**

A Classic PAT with the **`public_repo`** scope is sufficient for public
repositories. This single scope covers forking, pushing to the fork, and
creating PRs on the upstream repo.

```bash
export GITHUB_TOKEN=ghp_...
# or
gh auth login --with-token <<< "$GITHUB_TOKEN"
```

If the target repository is private, use the **`repo`** scope instead.

**Fine-grained Personal Access Token (untested alternative):**

Fine-grained PATs are more restrictive but harder to configure for this
workflow because the fork does not exist when the token is created and the
upstream repository is owned by someone else. If using a fine-grained PAT:

- Scope to **All repositories** owned by the token holder
- Required permissions:
  - **Contents:** Read and Write (push to the fork)
  - **Pull requests:** Read and Write (open PRs)
  - **Administration:** Read and Write (create the fork)

This configuration has not been tested. The fork-then-PR-upstream flow may
encounter edge cases with fine-grained PAT scoping.

## Quick Start

1. Point the workflow at a project repository
2. Run `/scan` to discover documentation (or `/speedrun` for the full pipeline)
3. Run `/review` for quality analysis
4. Optionally run `/verify` to check docs against code
5. Optionally run `/install-test` to execute installation steps on a cluster
6. Usage-test runs automatically after a successful install-test
7. Run `/report` to consolidate all findings
8. Optionally run `/fix` for concrete fix suggestions
9. Optionally run `/create-prs` to submit fixes as GitHub pull requests
