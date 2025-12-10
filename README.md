# OOTB Workflow Templates

Out-of-the-box workflow templates for the Ambient Code Platform (vTeam). These workflows provide structured processes for AI agents to follow when working on complex tasks.

## Overview

Workflows are Git repositories containing scripts, templates, agent configurations, and slash commands that guide Claude and other AI agents through multi-step processes. They help maintain consistency, quality, and best practices across your development workflow.

## Available Workflows

### Spec Kit Workflow

A comprehensive workflow for planning and implementing features using a specification-first approach.

**Status:** Production Ready

**Location:** `workflows/spec-kit`

**Structure:**
```
workflows/default/
├── .specify/               # Workflow configuration
│   ├── scripts/           # Automation scripts
│   │   └── bash/         # Shell scripts for workflow steps
│   ├── templates/        # Document templates
│   │   ├── spec-template.md
│   │   ├── plan-template.md
│   │   ├── tasks-template.md
│   │   └── checklist-template.md
│   └── memory/           # Workflow knowledge base
│       └── constitution.md
└── .claude/              # Claude AI configuration
    ├── agents/           # Agent personas and instructions
    │   ├── archie-architect.md
    │   ├── parker-product_manager.md
    │   ├── stella-staff_engineer.md
    │   └── [20+ other agents]
    └── commands/         # Slash commands
        ├── /specify.md   # Create feature specifications
        ├── /plan.md      # Generate implementation plans
        ├── /tasks.md     # Break down into tasks
        └── /implement.md # Execute implementation

```

**Workflow Phases:**

1. **Specify** (`/specify`) - Create detailed feature specifications
2. **Plan** (`/plan`) - Generate technical implementation plans
3. **Tasks** (`/tasks`) - Break down plans into actionable tasks
4. **Implement** (`/implement`) - Execute the implementation
5. **Analyze** (`/analyze`) - Review and analyze outcomes

**Best For:**
- Feature development
- Complex implementations
- Teams needing structured planning
- Documentation-first approaches

### Template Workflow

A comprehensive, self-contained template demonstrating all available configuration options for creating custom ACP workflows.

**Status:** Production Ready

**Location:** `workflows/template-workflow`

**Features:**
- Fully documented `ambient.json` with inline comments
- Example slash commands demonstrating workflow phases
- Sample agent personas for different roles
- Complete field reference documentation
- Best practices and usage patterns

**Best For:**
- Creating custom workflows
- Learning workflow structure
- Understanding configuration options
- Starting point for new workflow types

### Bug Fix Workflow

A systematic workflow for analyzing, fixing, and verifying software bugs with comprehensive testing and documentation.

**Status:** Production Ready

**Location:** `workflows/bugfix`

**Features:**
- Systematic bug reproduction and documentation
- Root cause analysis and impact assessment
- Fix implementation following best practices
- Comprehensive testing and regression test creation
- Complete documentation and release notes generation

## Using Workflows in ACP

### 1. Via Session UI

When creating or working with a session:

1. Navigate to your session detail page
2. Open the **Workflows** accordion
3. Select a workflow:
   - **Spec Kit Workflow** - Specification-driven feature development
   - **Bug Fix Workflow** - Systematic bug resolution
   - **Template Workflow** - Starting point for custom workflows
   - **Custom Workflow...** - Load your own workflow from any Git repository

The workflow will be cloned into your session's workspace and set as Claude's working directory.

### 2. Via API

```bash
POST /api/projects/{project}/agentic-sessions/{session}/workflow

{
  "gitUrl": "https://github.com/ambient-code/workflows.git",
  "branch": "main",
  "path": "workflows/spec-kit"
}
```

### 3. Via Session Creation

Workflows can be pre-configured when creating sessions through automation or templates.

## Workspace Structure

When a workflow is activated, your session workspace is organized as:

```
/workspace/sessions/{session-name}/
├── workflows/
│   ├── spec-kit/          # Spec Kit workflow (when selected)
│   │   ├── .specify/      # Scripts, templates, memory
│   │   └── .claude/       # Agents and commands
│   ├── bugfix/            # Bug Fix workflow (when selected)
│   │   ├── .ambient/      # Workflow configuration
│   │   └── .claude/       # Agents and commands
│   └── template-workflow/ # Template workflow (when selected)
│       ├── .ambient/      # Workflow configuration
│       └── .claude/       # Agents and commands
└── artifacts/             # Output directory for generated files
    ├── specs/            # Feature specifications (spec-kit)
    ├── bugfix/           # Bug fix artifacts (bugfix workflow)
    └── [custom]/         # Custom workflow outputs
```

**Key Concepts:**

- **Working Directory**: Claude works from `workflows/{workflow-name}/`
- **Artifacts Directory**: All outputs go to `artifacts/` (kept separate from workflow logic)
- **Workflow Switching**: You can switch workflows mid-session without losing your artifacts

## Creating Custom Workflows

**Quick Start:** See the [Workflow Development Guide](WORKFLOW_DEVELOPMENT_GUIDE.md) for a complete guide to creating custom workflows.

### Basic Structure

```
my-workflow/
├── .specify/              # (Optional) Specify framework integration
│   ├── scripts/
│   ├── templates/
│   └── memory/
├── .claude/               # (Optional) Claude-specific config
│   ├── agents/
│   └── commands/
└── README.md             # Workflow documentation
```

### Requirements

1. **Git Repository**: Must be accessible via HTTPS or SSH
2. **Branch**: Specify which branch to use (default: `main`)
3. **Path**: Optionally specify a subdirectory within the repo

### Best Practices

1. **Keep workflows focused** - One workflow per process type
2. **Document commands** - Provide clear instructions for each slash command
3. **Include templates** - Help agents maintain consistency
4. **Version control** - Use branches for workflow versions
5. **Test iteratively** - Validate workflows in real sessions

### Example: Minimal Custom Workflow

```bash
# Create a new workflow repo
mkdir my-custom-workflow
cd my-custom-workflow
git init

# Add Claude commands
mkdir -p .claude/commands
cat > .claude/commands/review.md << 'EOF'
# /review - Code Review

Review the code in the artifacts directory:
1. Check for common issues
2. Verify best practices
3. Suggest improvements
4. Document findings in artifacts/review.md
EOF

# Commit and push
git add .
git commit -m "Initial workflow"
git remote add origin https://github.com/your-org/my-custom-workflow.git
git push -u origin main
```

Load it in ACP:
1. Select "Custom Workflow..." in the UI
2. Enter Git URL: `https://github.com/your-org/my-custom-workflow.git`
3. Branch: `main`
4. Path: (leave empty if workflow is at repo root)
5. Click "Load Workflow"

## Workflow Development Guide

### Agent Personas

Agents provide specialized expertise and perspectives. Each agent should have:

```markdown
# Agent Name - Role

## Expertise
- Key area 1
- Key area 2

## Responsibilities
- What this agent does
- When to invoke this agent

## Communication Style
- How this agent communicates
```

### Slash Commands

Commands guide Claude through specific tasks:

```markdown
# /command-name - Short Description

## Purpose
What this command accomplishes

## Prerequisites
- File or state required before running

## Process
1. Step one
2. Step two
3. Step three

## Output
- What files/artifacts are created
- Where they are stored (always in artifacts/)
```

### Templates

Provide structure for consistency:

```markdown
# [Template Name]

## Section 1
Instructions for this section...

## Section 2
Instructions for this section...
```

## Configuration

### Future Platform Integration

The Ambient Code Platform will eventually point to this repository (`https://github.com/ambient-code/workflows`) as the official source for OOTB workflows.

### Environment Variables (Future)

Organizations will be able to configure OOTB workflows via environment variables in the ACP backend deployment, allowing customization without code changes.

**Planned Configuration:**
```yaml
# Future ACP backend environment variables
OOTB_WORKFLOWS_REPO: "https://github.com/ambient-code/workflows.git"
OOTB_WORKFLOWS_BRANCH: "main"
```

### Backend API (Future)

The backend will provide a public endpoint to list available OOTB workflows:

```bash
GET /api/workflows/ootb

Response:
{
  "workflows": [
    {
      "id": "spec-kit",
      "name": "Spec Kit Workflow",
      "description": "Comprehensive workflow for planning and implementing features...",
      "gitUrl": "https://github.com/ambient-code/workflows.git",
      "branch": "main",
      "path": "workflows/spec-kit",
      "enabled": true
    },
    {
      "id": "bugfix",
      "name": "Bug Fix Workflow",
      "description": "Systematic workflow for bug resolution...",
      "gitUrl": "https://github.com/ambient-code/workflows.git",
      "branch": "main",
      "path": "workflows/bugfix",
      "enabled": true
    },
    {
      "id": "template-workflow",
      "name": "Template Workflow",
      "description": "Starting point for custom workflows...",
      "gitUrl": "https://github.com/ambient-code/workflows.git",
      "branch": "main",
      "path": "workflows/template-workflow",
      "enabled": true
    }
  ]
}
```

The frontend will automatically fetch and display configured workflows.

## Troubleshooting

### Workflow Not Cloning

- **Check URL**: Ensure the Git URL is accessible
- **Check Branch**: Verify the branch exists
- **Check Permissions**: Private repos need authentication configured

### Commands Not Working

- **Check Path**: Ensure `.claude/commands/` directory exists
- **Check Format**: Commands must be markdown files
- **Check Session**: Workflow must be activated in the session

### Artifacts in Wrong Location

- **Workflow scripts should always write to `/workspace/artifacts/`**
- Check that scripts use absolute paths or `$WORKSPACE/artifacts/`
- The workflows directory is for logic only, not outputs

## Contributing

To contribute a new OOTB workflow:

1. Fork this repository
2. Create a new directory under `workflows/`
3. Follow the structure guidelines above
4. Submit a pull request with documentation
5. Include example usage and test results

## Support

- **Documentation**: [ACP User Guide](https://ambient-code.github.io/platform)
- **Issues**: [GitHub Issues](https://github.com/ambient-code/workflows/issues)
- **Discussions**: [GitHub Discussions](https://github.com/ambient-code/workflows/discussions)

## License

This repository and all OOTB workflows are provided under the MIT License. See LICENSE file for details.

---

**Repository:** [ambient-code/workflows](https://github.com/ambient-code/workflows)
**Available Workflows:** Spec Kit, Bug Fix, Template
**Platform:** Ambient Code Platform

