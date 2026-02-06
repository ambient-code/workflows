# ACP Workflow Templates

Out-of-the-box workflow templates for the Ambient Code Platform (ACP). These workflows provide structured processes for AI agents to follow when working on complex tasks.

> **For workflow developers:** See the [Workflow Development Guide](WORKFLOW_DEVELOPMENT_GUIDE.md) for comprehensive documentation on creating and modifying workflows.

## Overview

Workflows are structured configurations that guide Claude through multi-step processes. Each workflow defines:

- **System prompt**: Core instructions defining Claude's behavior and methodology
- **Startup prompt**: Initial greeting when the workflow activates
- **Commands**: Slash commands (e.g., `/diagnose`, `/fix`) for specific workflow phases
- **Artifacts**: Output locations for generated files

The platform automatically discovers workflows from this repository. Any directory under `workflows/` with a valid `.ambient/ambient.json` file appears in the UI.

## Available Workflows

| Workflow | Description | Commands |
|----------|-------------|----------|
| [**bugfix**](workflows/bugfix/) | Systematic bug resolution with reproduction, diagnosis, fix, and testing phases | `/reproduce`, `/diagnose`, `/fix`, `/test`, `/document` |
| [**triage**](workflows/triage/) | Issue backlog triage with actionable reports and bulk operations | Conversational |
| [**spec-kit**](workflows/spec-kit/) | Spec-driven development for feature planning and implementation | `/speckit.specify`, `/speckit.plan`, `/speckit.tasks`, `/speckit.implement` |
| [**prd-rfe-workflow**](workflows/prd-rfe-workflow/) | Create Product Requirements Documents and break them into RFE tasks | `/prd.discover`, `/prd.create`, `/rfe.breakdown`, `/rfe.prioritize` |
| [**amber-interview**](workflows/amber-interview/) | Collect user feedback through guided conversations | `/feedback`, `/interview` |
| [**template-workflow**](workflows/template-workflow/) | Starter template demonstrating workflow structure | `/init`, `/analyze`, `/plan`, `/execute`, `/verify` |

### Bug Fix Workflow

A systematic 5-phase workflow for resolving software bugs:

1. **Reproduce** - Confirm and document the bug behavior
2. **Diagnose** - Perform root cause analysis
3. **Fix** - Implement the solution
4. **Test** - Verify with regression tests
5. **Document** - Create release notes and update issues

Automatically invokes specialized agents (Stella for complex debugging, Neil for testing strategy) when needed.

### Triage Workflow

Efficiently triage repository issue backlogs:

- Analyzes all open issues
- Generates recommendations (CLOSE, FIX_NOW, BACKLOG, NEEDS_INFO, etc.)
- Produces an interactive HTML report with accept/reject checkboxes
- Creates bulk operation scripts for executing approved actions

### Spec Kit Workflow

Specification-driven development workflow:

- Create detailed feature specifications
- Generate technical implementation plans
- Break down plans into actionable tasks
- Guide implementation with checklists

### PRD/RFE Workflow

Product requirements documentation workflow:

- Discovery phase for understanding needs
- Requirements gathering
- PRD creation with structured templates
- Breakdown into Request for Enhancement (RFE) items
- Prioritization matrix

## Using Workflows

### In the ACP UI

1. Navigate to your session
2. Open the **Workflows** panel
3. Select a workflow from the list
4. The workflow loads and displays its startup prompt

### Custom Workflows

To test a workflow from a branch or external repository:

1. Select **"Custom Workflow..."** in the UI
2. Enter the Git URL, branch, and path
3. Click **"Load Workflow"**

This is useful for:

- Testing changes before merging to main
- Using workflows from other repositories
- Development and iteration

## Creating or Modifying Workflows

See the **[Workflow Development Guide](WORKFLOW_DEVELOPMENT_GUIDE.md)** for complete instructions on:

- Workflow structure and required files
- Creating workflows from scratch or template
- Using the `workflow-creator` skill
- Testing with "Custom Workflow..."
- Best practices for commands, skills, and system prompts

## Reference Documentation

| Document | Purpose |
|----------|---------|
| [WORKFLOW_DEVELOPMENT_GUIDE.md](WORKFLOW_DEVELOPMENT_GUIDE.md) | Complete guide for workflow developers |
| [AMBIENT_JSON_SCHEMA.md](AMBIENT_JSON_SCHEMA.md) | ambient.json field reference |
| [WORKSPACE_NAVIGATION_GUIDELINES.md](WORKSPACE_NAVIGATION_GUIDELINES.md) | Best practices for file navigation in systemPrompts |
| [AGENTS.md](AGENTS.md) | Guidelines for AI agents modifying this repository |

## Contributing

To contribute a workflow:

1. Fork this repository
2. Create a new workflow directory under `workflows/`
3. Follow the structure guidelines
4. Test using the "Custom Workflow" feature
5. Submit a pull request with documentation

## License

This repository is provided under the MIT License. See LICENSE for details.
