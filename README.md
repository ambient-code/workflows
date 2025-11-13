# OOTB Workflow Templates

Out-of-the-box workflow templates for the Ambient Code Platform (vTeam). These workflows provide structured processes for AI agents to follow when working on complex tasks.

## Overview

Workflows are Git repositories containing scripts, templates, agent configurations, and slash commands that guide Claude and other AI agents through multi-step processes. They help maintain consistency, quality, and best practices across your development workflow.

## Available Workflows

### Spec Kit Workflow (Default)

A comprehensive workflow for planning and implementing features using a specification-first approach.

**Default Configuration:**
- **Repository:** `https://github.com/Gkrumbach07/spec-kit-template.git`
- **Branch:** `main`
- **Path:** `workflows/spec-kit`

*Note: These defaults can be overridden via environment variables in the ACP backend deployment. See Configuration section below.*

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

### Bug Fix Workflow (Coming Soon)

A streamlined workflow optimized for bug triage, reproduction, and fixes.

**Planned Features:**
- Bug analysis and reproduction
- Root cause identification
- Fix implementation and validation
- Regression test generation

## Using Workflows in ACP

### 1. Via Session UI

When creating or working with a session:

1. Navigate to your session detail page
2. Open the **Workflows** accordion
3. Select a workflow:
   - **Spec Kit Workflow (OOTB)** - The default specification workflow
   - **Bug Fix Workflow** - (Coming soon)
   - **Custom Workflow...** - Load your own workflow

The workflow will be cloned into your session's workspace and set as Claude's working directory.

### 2. Via API

```bash
POST /api/projects/{project}/agentic-sessions/{session}/workflow

{
  "gitUrl": "https://github.com/Gkrumbach07/spec-kit-template.git",
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
│   ├── default/           # Empty unless workflow selected
│   └── spec-kit/          # Active workflow (when selected)
│       ├── .specify/      # Scripts, templates, memory
│       └── .claude/       # Agents and commands
└── artifacts/             # Output directory for generated files
    ├── spec/             # Generated specifications
    ├── plans/            # Implementation plans
    ├── tasks/            # Task breakdowns
    └── implementation/   # Code and artifacts
```

**Key Concepts:**

- **Working Directory**: Claude works from `workflows/{workflow-name}/`
- **Artifacts Directory**: All outputs go to `artifacts/` (kept separate from workflow logic)
- **Workflow Switching**: You can switch workflows mid-session without losing your artifacts

## Creating Custom Workflows

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

### Environment Variables

The ACP backend supports configuring OOTB workflows via environment variables. This allows organizations to fork and customize workflows without changing code.

**Spec Kit Workflow:**
- `OOTB_SPEC_KIT_REPO` - Git repository URL (default: `https://github.com/Gkrumbach07/spec-kit-template.git`)
- `OOTB_SPEC_KIT_BRANCH` - Branch to use (default: `main`)
- `OOTB_SPEC_KIT_PATH` - Path within repository (default: `workflows/spec-kit`)

**Bug Fix Workflow:**
- `OOTB_BUG_FIX_REPO` - Git repository URL (required to enable)
- `OOTB_BUG_FIX_BRANCH` - Branch to use (default: `main`)
- `OOTB_BUG_FIX_PATH` - Path within repository (optional)

**Example Deployment:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
spec:
  template:
    spec:
      containers:
      - name: backend
        env:
        - name: OOTB_SPEC_KIT_REPO
          value: "https://github.com/your-org/custom-spec-kit.git"
        - name: OOTB_SPEC_KIT_BRANCH
          value: "production"
```

### Backend API

The backend provides a public endpoint to list available OOTB workflows:

```bash
GET /api/workflows/ootb

Response:
{
  "workflows": [
    {
      "id": "spec-kit",
      "name": "Spec Kit Workflow",
      "description": "Comprehensive workflow for planning and implementing features...",
      "gitUrl": "https://github.com/Gkrumbach07/spec-kit-template.git",
      "branch": "main",
      "path": "workflows/spec-kit",
      "enabled": true
    },
    {
      "id": "bug-fix",
      "name": "Bug Fix Workflow",
      "description": "Streamlined workflow for bug triage...",
      "gitUrl": "",
      "branch": "main",
      "path": "",
      "enabled": false
    }
  ]
}
```

The frontend automatically fetches and displays configured workflows.

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

- **Documentation**: [ACP User Guide](https://ambient-code.github.io/vteam)
- **Issues**: [GitHub Issues](https://github.com/Gkrumbach07/spec-kit-template/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Gkrumbach07/spec-kit-template/discussions)

## License

This repository and all OOTB workflows are provided under the MIT License. See LICENSE file for details.

---

**Repository:** [Gkrumbach07/spec-kit-template](https://github.com/Gkrumbach07/spec-kit-template)  
**Default Workflow:** Spec Kit (`workflows/spec-kit`)  
**Platform:** Ambient Code Platform (vTeam)

