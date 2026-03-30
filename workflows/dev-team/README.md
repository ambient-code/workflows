# Dev Team

Assemble and lead a team of AI agents to accomplish any development task with high quality. The workflow acts as a team lead that classifies your task, selects the right specialists, coordinates parallel execution with quality gates, and delivers verified results.

## Overview

This workflow uses a dynamic team assembly pattern. Rather than fixed phases, it adapts to your task type:

| Task Type | What It Does |
|-----------|-------------|
| **Code** | Implement, fix, or refactor code with automated review |
| **PR Review** | Review pull requests for bugs, security, and conventions |
| **Doc Review** | Verify technical documents against current code |
| **Strategy** | Research, analyze, and recommend architectural decisions |
| **Communication** | Draft proposals, status updates, or cross-team messages |

## Getting Started

1. Load the workflow in your ACP session
2. Describe what you need done, or use `/dev-team [task description]`
3. The team lead classifies your task, proposes a team, and asks for approval
4. Agents execute in parallel with quality gates
5. Results are synthesized and delivered

## How It Works

### Phase 1: Classify and Scope

The lead reads your task, classifies it, and investigates the relevant codebase context.

### Phase 2: Design the Team

2-4 agents are selected from the role catalog:

- **Implementer** -- Writes production code following project conventions
- **Researcher** -- Investigates codebase, reads docs, gathers data
- **Writer** -- Drafts documents, communications, proposals
- **QE Engineer** -- Writes tests and validates behavior
- **Checker** -- Reviews all output for quality (always included)
- **Security Reviewer** -- Reviews from an adversarial security perspective

### Phase 3: Present Plan

The lead presents the team composition, task breakdown, and dependencies for your approval.

### Phase 4: Execute

Agents are spawned in parallel. The lead coordinates, enforces quality gates, and handles revision cycles (max 2 rounds).

### Phase 5: Deliver

Results are synthesized in a format appropriate to the task type.

## Available Skills

| Skill | Description |
|-------|-------------|
| `/dev-team [task]` | Classify a task, assemble a team, and execute |
| `/pr` | Create a pull request with systematic fork/auth handling |

## Output Artifacts

- **Code changes**: Applied directly in the repository (with worktree isolation for multi-agent writes)
- **Reviews and reports**: Presented inline
- **Documents**: Saved to `artifacts/dev-team/`

## Quality Standards

Every task gets built-in quality gates:

- At least one executor + one checker on every task
- All claims must cite evidence (file paths, line numbers)
- All criticism must be actionable (problem + location + fix)
- Task-type-specific standards (code conventions, review format, etc.)

## Configuration

Configured via `.ambient/ambient.json`. The skill definition is in `.claude/skills/dev-team/SKILL.md`.

## Customization

- **Adjust team defaults**: Edit the "Default Teams by Task Type" table in the skill
- **Add roles**: Extend the Role Catalog section
- **Change quality standards**: Modify the Phase 3 standards in the skill
- **Tune coordination**: Adjust max revision rounds, auto-proceed rules, etc.
