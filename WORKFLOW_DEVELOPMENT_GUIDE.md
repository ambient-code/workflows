# Workflow Development Guide

A guide for developers who want to create or modify workflows for the Ambient Code Platform (ACP).

## Overview: How Platform and Workflows Are Related

The Ambient Code Platform includes two main repositories:

| Repository | Purpose | Location |
|------------|---------|----------|
| **platform** | The ACP application (backend, frontend, operator, runners) | `platform/` directory |
| **workflows** | Workflow definitions used by the platform | `workflows/` directory (also at [github.com/ambient-code/workflows](https://github.com/ambient-code/workflows)) |

The platform fetches workflows **dynamically from GitHub at runtime**. When you select a workflow in the UI, the platform:

1. Calls the GitHub API to list available workflows
2. Reads workflow metadata from each workflow's `.ambient/ambient.json`
3. Clones the selected workflow into your session's workspace

This means changes to workflows in GitHub are automatically available to all platform users (after a ~5 minute cache expires).

### Automatic Workflow Discovery

**You don't need to register new workflows anywhere.** The platform automatically discovers all workflows by scanning the repository.

Here's how it works:

1. The platform lists all **directories** under `workflows/` in the configured repo
2. For each directory, it looks for `.ambient/ambient.json`
3. If found, it reads `name` and `description` to display in the UI
4. If not found, the workflow still appears (using the directory name as the display name)

**To add a new OOTB workflow:**

```text
workflows/
├── bugfix/                    # Existing workflow
├── triage/                    # Existing workflow
└── my-new-workflow/           # ← Just add a new directory!
    └── .ambient/
        └── ambient.json       # With name + description
```

That's it! Push to GitHub, wait ~5 minutes for the cache, and your workflow appears in the UI.

> 💡 **Note:** The 5-minute cache exists to avoid GitHub API rate limits. During development, use "Custom Workflow" to bypass the cache and test immediately.

---

## Workflow Structure

ACP uses **Claude Code** as its runner, which means workflows can leverage the full [Claude Code extension system](https://code.claude.com/docs/en/features-overview). This includes skills, commands, subagents, hooks, and MCP integrations.

### Directory Structure

```text
my-workflow/
├── .ambient/
│   └── ambient.json           # REQUIRED - ACP workflow configuration
├── .claude/
│   ├── commands/              # Slash commands (invoked with /command-name)
│   │   ├── diagnose.md
│   │   └── fix.md
│   ├── skills/                # Reusable knowledge and workflows
│   │   └── my-skill/
│   │       └── SKILL.md
│   └── settings.json          # Claude Code settings (tool permissions, etc.)
├── templates/                 # Optional - Reference files Claude uses to generate outputs
│   └── report-template.md
├── scripts/                   # Optional - Script templates for executable artifacts
│   └── bulk-operations.sh
├── CLAUDE.md                  # Persistent context loaded every session
├── README.md                  # Workflow documentation
└── FIELD_REFERENCE.md         # Optional - Configuration reference
```

### Claude Code Extension Types

Since ACP runs on Claude Code, you can use any of these extension types in your workflow:

| Extension | Location | Purpose | When to Use |
|-----------|----------|---------|-------------|
| **CLAUDE.md** | Root of workflow | Persistent context loaded every session | Project conventions, "always do X" rules |
| **Commands** | `.claude/commands/*.md` | Slash commands invoked with `/<name>` | Workflow phases, repeatable tasks |
| **Skills** | `.claude/skills/<name>/SKILL.md` | Reusable knowledge and workflows | Reference docs, complex multi-step processes |
| **Subagents** | Defined in skills | Isolated workers with their own context | Context isolation, parallel tasks |
| **Hooks** | `.claude/hooks/` | Scripts that run on events | Linting after edits, automated validation |
| **MCP** | `.claude/settings.json` | External service connections | Database queries, API integrations |

> 📖 For complete details on each extension type, see the [Claude Code documentation](https://code.claude.com/docs/en/features-overview).

---

### ACP-Specific: The `ambient.json` File (Required)

In addition to standard Claude Code extensions, ACP workflows **require** an `ambient.json` configuration file at `.ambient/ambient.json`. This is what makes a directory an ACP workflow (vs. just a Claude Code project).  Here is an example:

```json
{
  "name": "Fix a bug",
  "description": "Systematic workflow for analyzing, fixing, and verifying software bugs ...",
  "systemPrompt": "You are Amber, the Ambient Code Platform's expert colleague orchestrating systematic bug resolution. You help developers fix ....",
  "startupPrompt": "Welcome to the Bug Fix Workflow! ... Provide a bug description, issue URL, or symptoms you're experiencing, and I'll orchestrate a systematic fix!",
  "results": {
    "Bug Reports": "artifacts/bugfix/reports/*.md",
    "Root Cause Analysis": "artifacts/bugfix/analysis/*.md",
    "Fix Implementation": "artifacts/bugfix/fixes/**/*",
    "Test Cases": "artifacts/bugfix/tests/**/*",
    "Test Results": "artifacts/bugfix/tests/verification.md",
    "Documentation": "artifacts/bugfix/docs/*.md",
    "Release Notes": "artifacts/bugfix/docs/release-notes.md",
    "Execution Logs": "artifacts/bugfix/logs/*.log"
  }
}
```

| Field | Required | Purpose |
|-------|----------|---------|
| `name` | ✅ | Display name in the UI |
| `description` | ✅ | Brief explanation shown in workflow selector |
| `systemPrompt` | ✅ | Core instructions defining Claude's behavior |
| `startupPrompt` | ✅ | Initial greeting when workflow activates |
| `results` | ❌ | Maps artifact names to output paths (for UI discovery) |

> 📖 See [AMBIENT_JSON_SCHEMA.md](AMBIENT_JSON_SCHEMA.md) for complete field documentation.

---

### CLAUDE.md (Persistent Context) — Optional

You can optionally place a `CLAUDE.md` file at the root of your workflow for supplementary instructions. Claude Code loads this automatically at the start of every session.

**How CLAUDE.md relates to `systemPrompt`:**

| Source | Loaded by | Best for |
|--------|-----------|----------|
| `systemPrompt` (ambient.json) | ACP runner, injected as "Workflow Instructions" | Workflow phases, methodology, output locations |
| `CLAUDE.md` | Claude Code, automatically | "Always remember" rules, agent usage, coding style |

These **don't conflict** — they complement each other. The `systemPrompt` defines *what the workflow does*, while `CLAUDE.md` can add *how Claude should behave* while doing it.

**Most workflows skip CLAUDE.md** because:
- `systemPrompt` is already required and covers most needs
- Adding both can feel redundant for simple workflows
- It's genuinely optional

**When CLAUDE.md is useful:**
- Sub-agent usage guidelines (see `workflows/spec-kit/CLAUDE.md` for an example)
- Coding conventions that apply across all phases
- "Never do X" rules that shouldn't clutter the systemPrompt
- Team-specific preferences

**Example: `CLAUDE.md`**

```markdown
# Bug Fix Workflow Guidelines

## Sub-Agent Usage
You have access to specialized sub-agents. Use them proactively when appropriate.

### Available Agents
- **Stella (Staff Engineer)**: Complex debugging, root cause analysis
- **Neil (Test Engineer)**: Testing strategy, test automation

## Conventions
- Always use file:line notation when referencing code (e.g., `handlers.go:245`)
- Include timestamps in generated reports
```

> 💡 **Tip:** Keep CLAUDE.md focused on behavioral guidance. Put workflow methodology in `systemPrompt`.

---

### Slash Commands (`.claude/commands/`)

Commands guide Claude through specific workflow phases. Each command is a markdown file that defines a repeatable task.

**Example: `.claude/commands/diagnose.md`**

```markdown
# /diagnose - Root Cause Analysis

## Purpose
Analyze the bug to identify the root cause and assess impact.

## Prerequisites
- Bug has been reproduced (run /reproduce first)
- Reproduction report exists at artifacts/bugfix/reports/reproduction.md

## Process
1. Review reproduction report
2. Analyze relevant code paths
3. Form and test hypotheses
4. Document root cause

## Output
- `artifacts/bugfix/analysis/root-cause.md`
```

---

### Skills (`.claude/skills/`)

Skills are reusable knowledge packages that can include instructions, workflows, and reference material. Unlike commands (which are simple), skills can be more complex and can even spawn subagents.

**Structure:**

```text
.claude/skills/
└── workflow-creator/
    └── SKILL.md
```

**Example: `.claude/skills/workflow-creator/SKILL.md`**

```markdown
---
name: workflow-creator
description: Creates production-ready ACP workflows with proper structure
---

# Workflow Creator Skill

You are an expert ACP Workflow Specialist...

## Your Role
Help users create production-ready ACP workflows through an interactive process.

## Process
1. Ask targeted questions to understand needs
2. Generate all required files
3. Explain each component
...
```

Skills can be:
- **Reference skills**: Knowledge Claude uses throughout your session (API docs, style guides)
- **Action skills**: Triggered with `/<skill-name>` to perform specific tasks

---

### Subagents

Subagents are isolated workers that run in their own context and return summarized results. Define them in skills when you need:

- **Context isolation**: Work happens separately, only summary returns
- **Parallel tasks**: Multiple agents working simultaneously
- **Specialized workers**: Focused expertise for specific subtasks

> 📖 See [Claude Code Subagents documentation](https://code.claude.com/docs/en/sub-agents) for details.

---

### Hooks (`.claude/hooks/`)

Hooks are deterministic scripts that run on specific events—no LLM involved. Use them for predictable automation.

**Examples:**
- Run ESLint after every file edit
- Validate JSON schemas before commits
- Send notifications when certain files change

> 📖 See [Claude Code Hooks documentation](https://code.claude.com/docs/en/hooks) for details.

---

### MCP (Model Context Protocol)

MCP connects Claude to external services like databases, Slack, browsers, or custom APIs. Configure MCP servers in `.claude/settings.json`.

**Example use cases:**
- Query a database for bug history
- Post status updates to Slack
- Fetch data from internal APIs

> 📖 See [Claude Code MCP documentation](https://code.claude.com/docs/en/mcp) for details.

---

## Development Workflow

### Recommended Approach: Test with Custom Workflows

**Don't push directly to main!** Instead, test your changes using the "Custom Workflow" feature:

```text
┌─────────────────────────────────────────────────────────────┐
│  1. Create a feature branch                                 │
│     git checkout -b feature/my-workflow-improvement         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  2. Make your changes in workflows/workflows/<name>/        │
│     - Edit .ambient/ambient.json                            │
│     - Edit .claude/commands/*.md                            │
│     - Edit .claude/agents/*.md                              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  3. Push your branch to GitHub                              │
│     git push origin feature/my-workflow-improvement         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  4. Test in ACP using "Custom Workflow..."                  │
│     - Git URL: https://github.com/ambient-code/workflows    │
│     - Branch: feature/my-workflow-improvement               │
│     - Path: workflows/<your-workflow>                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  5. Iterate: make changes → push → reload workflow → test   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  6. Once satisfied, open PR to main branch                  │
└─────────────────────────────────────────────────────────────┘
```

### Step-by-Step Example

Let's say you want to improve the bugfix workflow:

**1. Clone and branch:**

```bash
cd /path/to/acp-workflows/workflows
git checkout -b feature/bugfix-improvements
```

**2. Make your changes:**

```bash
# Edit the workflow configuration
vim workflows/bugfix/.ambient/ambient.json

# Add or modify a command
vim workflows/bugfix/.claude/commands/diagnose.md

# Add or modify a skill
vim workflows/bugfix/.claude/skills/root-cause-analysis/SKILL.md

# Edit persistent context
vim workflows/bugfix/CLAUDE.md
```

**3. Push to GitHub:**

```bash
git add workflows/bugfix/
git commit -m "Improve bugfix workflow diagnosis phase"
git push origin feature/bugfix-improvements
```

**4. Test in ACP:**
1. Open the ACP UI
2. Create or open a session
3. Click the workflow dropdown
4. Select **"Custom Workflow..."**
5. Enter:
   - **Git URL:** `https://github.com/ambient-code/workflows.git`
   - **Branch:** `feature/bugfix-improvements`
   - **Path:** `workflows/bugfix`
6. Click **"Load Workflow"**

**5. Iterate:**

- Test the workflow by running commands
- Make adjustments locally
- Push changes: `git push origin feature/bugfix-improvements`
- Reload the workflow in ACP (select Custom Workflow again with same settings)
- Repeat until satisfied

**6. Create PR:**

```bash
# Open a pull request on GitHub
# https://github.com/ambient-code/workflows/compare/main...feature/bugfix-improvements
```

---

## Creating a New Workflow

### Option 1: Use the Workflow Creator Skill (with Claude Code)

The repository includes a **workflow-creator skill** at `.claude/skills/workflow-creator/` that guides you through workflow creation interactively. Open the workflows repository in Claude Code and use:

```text
Use the workflow-creator skill to create a new workflow for [your purpose].
Put all files in workflows/[workflow-name]/.
```

This will generate all the required files with proper structure through an interactive Q&A process.

> ⚠️ **Note:** Using Claude Code to author Claude Code skills can be confusing. See [Using Claude Code to Author Workflows](#using-claude-code-to-author-workflows) for tips on clear prompting.

### Option 2: Copy the Template

```bash
# Copy the template workflow
cp -r workflows/template-workflow workflows/my-new-workflow

# Edit the configuration
vim workflows/my-new-workflow/.ambient/ambient.json

# Customize commands and agents as needed
```

### Option 3: Create from Scratch

```bash
# Create directory structure
mkdir -p workflows/my-workflow/.ambient
mkdir -p workflows/my-workflow/.claude/commands
mkdir -p workflows/my-workflow/.claude/skills

# Create minimal ambient.json (REQUIRED for ACP)
cat > workflows/my-workflow/.ambient/ambient.json << 'EOF'
{
  "name": "My Workflow",
  "description": "A workflow that does X, Y, and Z",
  "systemPrompt": "You are a helpful assistant for...\n\n## Commands\n- /start - Begin the workflow\n\n## Output\nWrite artifacts to artifacts/my-workflow/",
  "startupPrompt": "Welcome! Use /start to begin."
}
EOF

# Create CLAUDE.md for persistent context (optional but recommended)
cat > workflows/my-workflow/CLAUDE.md << 'EOF'
# My Workflow Guidelines

## Conventions
- Always write outputs to `artifacts/my-workflow/`
- Use markdown for documentation
- Include timestamps in generated files
EOF

# Create your first command
cat > workflows/my-workflow/.claude/commands/start.md << 'EOF'
# /start - Begin the Workflow

## Purpose
Initialize the workflow and gather requirements.

## Process
1. Ask clarifying questions
2. Document requirements
3. Proceed to next phase

## Output
- `artifacts/my-workflow/requirements.md`
EOF
```

> 💡 **Tip:** Start simple with just `ambient.json` and commands. Add skills, hooks, and MCP as your workflow grows more complex.

---

## Using Claude Code to Author Workflows

The workflows repository includes a **workflow-creator skill** at `.claude/skills/workflow-creator/` that can help you create new workflows interactively. This means you can use Claude Code itself to author Claude Code skills—a powerful but potentially confusing approach.

### When This Works Well

Using Claude Code to author workflows is effective when you:
- Want interactive guidance through the workflow creation process
- Need help generating boilerplate files with correct structure
- Want to iterate quickly on `systemPrompt` and command designs
- Are learning the workflow format and want explanations as you go

### The Confusion Risk

When Claude Code is authoring workflows, there are two sets of Claude Code extensions in play:

| Type | Location | Purpose |
|------|----------|---------|
| **Authoring skills** | Root `.claude/` directory | Skills Claude is *using* to help you (e.g., workflow-creator) |
| **Authored skills** | `workflows/<name>/.claude/` | Skills Claude is *creating* for your new workflow |

Claude can sometimes mix these up, especially when:
- You ask it to "edit the skill" without specifying which one
- File paths are ambiguous
- You're discussing skill concepts while also creating skills

### Tips for Clear Prompting

**1. Use explicit paths:**

```text
❌ "Create a new command for the diagnose phase"
✅ "Create a new command at workflows/bugfix/.claude/commands/diagnose.md"
```

**2. Be explicit about context:**

```text
❌ "Update the CLAUDE.md file"
✅ "Update the CLAUDE.md file in the bugfix workflow at workflows/bugfix/CLAUDE.md"
```

**3. Clarify what you're authoring vs. using:**

```text
"I want to CREATE a new skill for my bugfix workflow (not use an existing skill).
The new skill should be at workflows/bugfix/.claude/skills/root-cause/SKILL.md"
```

**4. Start fresh sessions for different workflows:**

If you're creating multiple workflows, consider starting a new Claude Code session for each one to avoid context confusion.

**5. Reference the workflow-creator skill explicitly:**

```text
"Use the workflow-creator skill to help me build a new security audit workflow"
```

### Example: Creating a Workflow with Claude Code

```text
User: I want to create a new workflow called "code-review" for systematic code reviews.
      Use the workflow-creator skill to guide me through this. All files should go
      in workflows/code-review/.

Claude: [Uses workflow-creator skill, asks questions about phases, agents, etc.]
        [Creates files at workflows/code-review/.ambient/ambient.json, etc.]

User: Now create a command for the initial review phase.
      Put it at workflows/code-review/.claude/commands/review.md

Claude: [Creates the command file at the specified path]
```

### Alternative: Use vim/VS Code for Precision

If you find the meta-nature of "Claude authoring Claude skills" confusing, you can always:
1. Use the workflow-creator skill to generate initial structure
2. Switch to a traditional editor (vim, VS Code) for fine-tuning
3. Return to Claude Code for testing and iteration

Both approaches work—choose what feels most productive for your workflow.

---

## Best Practices

### Choosing the Right Extension Type

| If you need... | Use... | Why |
|----------------|--------|-----|
| Rules Claude should always follow | `CLAUDE.md` | Loaded every session automatically |
| A repeatable task users invoke | Command (`.claude/commands/`) | Simple, direct invocation with `/name` |
| Complex multi-step workflows | Skill (`.claude/skills/`) | Can include subagents, detailed instructions |
| Context isolation for heavy tasks | Subagent (in a skill) | Prevents context bloat in main session |
| Automated validation/linting | Hook (`.claude/hooks/`) | Runs deterministically, no LLM involved |
| External service access | MCP | Database, Slack, APIs, etc. |

### System Prompt Design (`ambient.json`)

1. **Define the role clearly**: "You are a [specific role] assistant..."
2. **List all commands**: Document every `/command` with its purpose
3. **Specify output locations**: Always tell Claude where to write artifacts
4. **Include workflow phases**: Step-by-step methodology
5. **Reference available skills/agents**: When to invoke specialized capabilities

### CLAUDE.md Design

1. **Keep it focused**: Under ~500 lines; move reference material to skills
2. **Use for conventions**: Coding standards, project structure, "always/never" rules
3. **Avoid duplication**: Don't repeat what's in `systemPrompt`
4. **Include practical commands**: Build commands, test commands, common operations

### Command Design

1. **Clear prerequisites**: What must exist before running this command?
2. **Specific process**: Numbered steps with expected outcomes
3. **Defined outputs**: Exact file paths for generated artifacts
4. **Success criteria**: How to know when the command is complete

### Skill Design

1. **Use frontmatter**: Include `name` and `description` in YAML frontmatter
2. **Consider context cost**: Skills load on-demand; use `disable-model-invocation: true` for user-only skills
3. **Document when to use**: Clear scenarios where this skill applies
4. **Include examples**: Show expected inputs and outputs

### Testing

1. **Test each command**: Verify outputs are created correctly
2. **Test the flow**: Run through the entire workflow start to finish
3. **Test edge cases**: What happens with incomplete inputs?
4. **Test with real scenarios**: Use actual bugs/features from your project
5. **Test context usage**: Ensure skills/CLAUDE.md don't bloat context unnecessarily

### Using Templates and Reference Files

Workflows can include **template files** that Claude uses as references when generating customized artifacts. This is useful when:

- You want Claude to generate scripts, reports, or other structured outputs
- The output format should be consistent but content varies per session
- You need executable artifacts that users run outside ACP

**Example structure (from the triage workflow):**

```text
workflows/triage/
├── .ambient/
│   └── ambient.json
├── templates/                    # Reference files for Claude
│   ├── report.html              # HTML template
│   └── triage-report.md         # Markdown template
├── scripts/                      # Script templates
│   └── bulk-operations.sh       # Reference implementation
└── artifacts/triage/             # Generated outputs (customized)
    ├── report.html              # Customized for this repo
    ├── triage-report.md         # With actual issue data
    └── bulk-operations.sh       # Ready to execute
```

**The pattern:**

1. **`templates/` and `scripts/`** contain reference files Claude reads
2. **`artifacts/`** contains customized outputs Claude generates
3. Users download artifacts and run them locally (with their own credentials)

**Why this works well:**

| Benefit | Explanation |
|---------|-------------|
| **Consistency** | Templates ensure outputs follow the expected format |
| **Security** | Sensitive tokens (GITHUB_TOKEN, etc.) stay on user's machine |
| **Human review** | User reviews generated scripts before executing |
| **Flexibility** | Works even without platform integrations configured |

**In your `systemPrompt`, reference templates like this:**

```text
Follow the template at templates/triage-report.md exactly.
Generate a customized version at artifacts/triage/triage-report.md.
```

This pattern is ideal for workflows that produce **executable artifacts** (scripts, config files) rather than just documentation.

---

## Troubleshooting

### Workflow doesn't appear in UI

- Verify `.ambient/ambient.json` exists and is valid JSON
- Check that `name` and `description` fields are present
- Ensure the workflow directory is under `workflows/`

### Commands aren't recognized

- Files must be in `.claude/commands/` directory
- Files must have `.md` extension
- Command file should start with `# /command-name`

### Custom Workflow won't load

- Verify Git URL is accessible (try cloning manually)
- Check branch name is correct (case-sensitive)
- Verify path exists in the repository
- For private repos, ensure GitHub authentication is configured in project settings

### Changes aren't reflected

- Push your changes to GitHub
- The platform caches workflow listings for ~5 minutes
- For Custom Workflow, re-select it to clone fresh

---

## Reference

### Key Files

| File | Purpose |
|------|---------|
| `AMBIENT_JSON_SCHEMA.md` | Complete ambient.json field documentation |
| `WORKSPACE_NAVIGATION_GUIDELINES.md` | Best practices for file organization |
| `.claude/skills/workflow-creator/SKILL.md` | Interactive workflow creation skill |
| `workflows/template-workflow/` | Starter template for new workflows |

### Environment Variables (Platform)

If running the platform locally, you can override the default workflow source:

```bash
# Point to a different workflows repository
export OOTB_WORKFLOWS_REPO=https://github.com/YOUR-ORG/workflows.git
export OOTB_WORKFLOWS_BRANCH=main
export OOTB_WORKFLOWS_PATH=workflows
```

### Links

- [Platform Repository](https://github.com/ambient-code/platform)
- [Workflows Repository](https://github.com/ambient-code/workflows)
- [ACP Documentation](https://ambient-code.github.io/vteam)
- [Claude Code Documentation](https://code.claude.com/docs/en/features-overview) — Full reference for extensions (skills, hooks, MCP, etc.)

---

## Quick Reference: Workflow Checklist

Before submitting a PR for a new or modified workflow:

**Required:**
- [ ] `.ambient/ambient.json` exists and is valid JSON
- [ ] All four required fields are present (`name`, `description`, `systemPrompt`, `startupPrompt`)

**Commands & Skills:**
- [ ] Commands are in `.claude/commands/` with `.md` extension
- [ ] Skills are in `.claude/skills/<name>/SKILL.md` with proper frontmatter
- [ ] Output paths in `systemPrompt` match `results` configuration

**Documentation:**
- [ ] README.md documents the workflow
- [ ] CLAUDE.md (if used) is under ~500 lines

**Testing:**
- [ ] Tested using "Custom Workflow" feature
- [ ] All workflow phases work end-to-end
- [ ] Commands produce expected artifacts

---

**Questions?** Open an issue in the [workflows repository](https://github.com/ambient-code/workflows/issues) or ask in the team channel.
