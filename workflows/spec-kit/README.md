# Spec Kit Workflow

Comprehensive specification-driven development workflow for feature planning, task breakdown, and implementation.

## Overview

The Spec Kit Workflow guides you through a structured approach to feature development:

1. **Specify** - Create detailed feature specifications
2. **Analyze** - Perform cross-artifact consistency analysis
3. **Clarify** - Identify and resolve underspecified areas
4. **Plan** - Generate technical implementation plans
5. **Tasks** - Break down plans into actionable tasks
6. **Implement** - Execute the implementation
7. **Checklist** - Generate custom verification checklists

## Quick Start

### In an ACP Session

1. Select "Spec Kit Workflow" from the workflows dropdown
2. Wait for workspace initialization
3. Run the initialization script: `./.specify/scripts/bash/init-workspace.sh`
4. Start with `/speckit.specify [feature-description]`

### Available Commands

- `/speckit.specify` - Create or update feature specification
- `/speckit.analyze` - Analyze consistency across spec, plan, and tasks
- `/speckit.clarify` - Ask targeted clarification questions
- `/speckit.plan` - Generate implementation plan
- `/speckit.tasks` - Generate actionable task breakdown
- `/speckit.implement` - Execute the implementation
- `/speckit.checklist` - Generate custom verification checklist
- `/speckit.constitution` - Create or update project constitution

## Workflow Phases

### 1. Specify (`/speckit.specify`)

Creates a detailed feature specification from natural language description.

**Input:** Feature description
**Output:** `artifacts/specs/**/spec.md`

### 2. Analyze (`/speckit.analyze`)

Performs non-destructive cross-artifact analysis for consistency and quality.

**Input:** Existing spec.md, plan.md, tasks.md
**Output:** Analysis report with recommendations

### 3. Clarify (`/speckit.clarify`)

Identifies underspecified areas and asks up to 5 targeted clarification questions.

**Input:** Current spec.md
**Output:** Updated spec.md with clarifications

### 4. Plan (`/speckit.plan`)

Generates technical implementation plan using the plan template.

**Input:** spec.md
**Output:** `artifacts/specs/**/plan.md`

### 5. Tasks (`/speckit.tasks`)

Generates dependency-ordered, actionable task breakdown.

**Input:** spec.md, plan.md
**Output:** `artifacts/specs/**/tasks.md`

### 6. Implement (`/speckit.implement`)

Executes the implementation by processing all tasks in tasks.md.

**Input:** tasks.md
**Output:** Code changes, implementation artifacts

### 7. Checklist (`/speckit.checklist`)

Generates a custom verification checklist based on user requirements.

**Input:** Feature requirements
**Output:** Custom checklist

## Agent Orchestration

The Spec Kit Workflow includes agents for different roles and perspectives. These agents are invoked automatically as needed:

**Engineering & Architecture:**
- Archie (Architect), Stella (Staff Engineer), Emma (Engineering Manager), Lee (Team Lead), Taylor (Team Member), Neil (Test Engineer)

**Product & Strategy:**
- Parker (Product Manager), Olivia (Product Owner), Dan (Senior Director), Diego (Program Manager), Sam (Scrum Master), Jack (Delivery Owner)

**UX & Design:**
- Aria (UX Architect), Uma (UX Team Lead), Felix (UX Feature Lead), Steve (UX Designer), Ryan (UX Researcher), Phoenix (PxE Specialist)

**Content & Documentation:**
- Terry (Technical Writer), Tessa (Writing Manager), Casey (Content Strategist)

**Note:** Platform agents (Amber, Parker, Stella, Ryan, Steve, Terry) are also available when running in the Ambient Code Platform.

## Directory Structure

```
spec-kit/
├── .ambient/
│   └── ambient.json           # Workflow configuration
├── .specify/
│   ├── scripts/               # Automation scripts
│   │   └── bash/
│   │       └── init-workspace.sh
│   ├── templates/             # Document templates
│   │   ├── spec-template.md
│   │   ├── plan-template.md
│   │   ├── tasks-template.md
│   │   ├── ideate-template.md
│   │   ├── checklist-template.md
│   │   └── agent-file-template.md
│   └── memory/                # Workflow knowledge base
│       └── constitution.md
├── .claude/
│   ├── agents/                # Agent personas (20+ agents)
│   └── commands/              # Slash commands
│       ├── speckit.specify.md
│       ├── speckit.analyze.md
│       ├── speckit.clarify.md
│       ├── speckit.plan.md
│       ├── speckit.tasks.md
│       ├── speckit.implement.md
│       ├── speckit.checklist.md
│       └── speckit.constitution.md
├── CLAUDE.md                  # Agent usage guidelines
└── README.md                  # This file
```

## Artifacts Generated

All outputs are stored in `artifacts/specs/`:

```
artifacts/specs/
└── [feature-name]/
    ├── spec.md         # Feature specification
    ├── plan.md         # Implementation plan
    └── tasks.md        # Task breakdown
```

## Best Practices

1. **Always initialize first:** Run `./.specify/scripts/bash/init-workspace.sh` before starting
2. **Start with /specify:** Begin with a clear feature description
3. **Iterate on clarity:** Use `/speckit.clarify` to refine underspecified areas
4. **Sequential phases:** Follow specify → plan → tasks → implement for best results
5. **Review before implementing:** Use `/speckit.analyze` to check consistency

## Customization

### Templates

Customize templates in `.specify/templates/` to match your organization's standards:
- `spec-template.md` - Feature specification format
- `plan-template.md` - Implementation plan format
- `tasks-template.md` - Task breakdown format

### Constitution

Update `.specify/memory/constitution.md` to encode your project's principles and constraints.

### Agents

Add or modify agents in `.claude/agents/` to match your team's roles and expertise.

## Troubleshooting

**Symlink errors during initialization:**
- Ensure you run init script from the workflow directory
- Check permissions on artifacts directory

**Commands not found:**
- Verify workflow is loaded in session
- Check `.claude/commands/` directory exists

**Templates not being used:**
- Confirm templates exist in `.specify/templates/`
- Check systemPrompt references correct template paths

## Integration with ACP

This workflow integrates with the Ambient Code Platform:
- Load via workflow selection UI
- Automatically clones into session workspace
- Platform agents available alongside workflow agents
- Artifacts stored in shared artifacts directory

## Support

- **Issues:** [github.com/ambient-code/workflows/issues](https://github.com/ambient-code/workflows/issues)
- **Workflow Development Guide:** [WORKFLOW_DEVELOPMENT_GUIDE.md](../../WORKFLOW_DEVELOPMENT_GUIDE.md)
- **Platform Documentation:** [ambient-code.github.io/platform](https://ambient-code.github.io/platform)

---

**Status:** Production Ready
**Version:** 1.0
**Maintained By:** Ambient Code Platform Team
