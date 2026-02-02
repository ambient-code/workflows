# Agent Guidelines for ACP Workflows Repository

This document provides rules and guidance for AI agents making changes to this repository.

## Repository Overview

This repository contains workflow definitions for the Ambient Code Platform (ACP). Workflows are automatically discovered by the platform from the `workflows/` directory.

**Key directories:**

```text
workflows/
├── workflows/              # All workflow definitions
│   ├── bugfix/            # Bug fix workflow
│   ├── triage/            # Issue triage workflow
│   ├── spec-kit/          # Specification workflow
│   ├── prd-rfe-workflow/  # PRD/RFE workflow
│   ├── template-workflow/ # Starter template
│   └── [your-workflow]/   # New workflows go here
├── .claude/
│   └── skills/            # Repository-level skills (workflow-creator, workflow-editor)
├── WORKFLOW_DEVELOPMENT_GUIDE.md
├── AMBIENT_JSON_SCHEMA.md
├── WORKSPACE_NAVIGATION_GUIDELINES.md
└── README.md
```

---

## Critical Rules

### 1. Never Modify Multiple Workflows Without Explicit Request

Each workflow is independent. When asked to make changes, clarify which specific workflow(s) should be modified. Do not assume changes to one workflow should propagate to others.

### 2. Always Validate JSON Syntax

The `.ambient/ambient.json` file must be valid JSON. After any edit:

- Ensure no trailing commas
- Ensure all strings are properly quoted
- Ensure the file parses correctly

### 3. Preserve Existing Functionality

When modifying workflows:

- Keep all existing commands unless explicitly asked to remove them
- Maintain backward compatibility with existing artifact paths
- Do not remove agents or skills without explicit instruction

### 4. Follow Markdown Linting Standards

All Markdown files must follow standard linting practices. Common rules:

- **Blank lines around headings**: Add a blank line before and after every heading
- **Blank lines around lists**: Add a blank line before and after bullet/numbered lists
- **Blank lines around code blocks**: Add a blank line before and after fenced code blocks
- **No trailing whitespace**: Remove spaces at the end of lines
- **Single trailing newline**: Files should end with exactly one blank line
- **Consistent list markers**: Use `-` for unordered lists throughout
- **Fenced code blocks should have a language**

Example:

```markdown
## Heading

Some paragraph text.

- List item one
- List item two

More text after the list.
```

### 5. Use the Correct Skill for the Task

This repository has two specialized skills:

| Task | Skill to Use |
|------|--------------|
| Create a new workflow from scratch | `workflow-creator` |
| Modify an existing workflow | `workflow-editor` |

Invoke these skills when appropriate rather than making ad-hoc changes.

---

## Workflow Structure Requirements

Every workflow **must** have:

```text
workflows/{workflow-name}/
├── .ambient/
│   └── ambient.json       # REQUIRED - must have name, description, systemPrompt, startupPrompt
└── README.md              # Recommended - document the workflow
```

Optional but common:

```text
├── .claude/
│   ├── commands/          # Slash commands (*.md files)
│   ├── skills/            # Reusable skills
│   └── agents/            # Agent personas (legacy, prefer skills)
├── templates/             # Reference templates for artifact generation
├── scripts/               # Script templates
└── CLAUDE.md              # Persistent context (behavioral guidelines)
```

### Required Fields in ambient.json

| Field | Required | Purpose |
|-------|----------|---------|
| `name` | Yes | Display name in UI (2-5 words) |
| `description` | Yes | Brief explanation (1-3 sentences) |
| `systemPrompt` | Yes | Core instructions defining agent behavior |
| `startupPrompt` | Yes | Initial greeting when workflow activates |
| `results` | No | Maps artifact names to output paths |

---

## Writing SystemPrompts

The `systemPrompt` is the most important part of a workflow. Follow these guidelines:

### Must Include

1. **Role definition**: "You are a [specific role]..."
2. **Available commands**: List every `/command` with its purpose
3. **Workflow phases**: Step-by-step methodology
4. **Output locations**: Where to write artifacts (e.g., `artifacts/{workflow-name}/`)
5. **Workspace navigation block**: Help Claude find files efficiently

### Workspace Navigation Block

Include this pattern in every systemPrompt (customize paths as needed):

```text
WORKSPACE NAVIGATION:
**CRITICAL: Follow these rules to avoid fumbling when looking for files.**

Standard file locations (from workflow root):
- Config: .ambient/ambient.json (ALWAYS at this path)
- Commands: .claude/commands/*.md
- Outputs: artifacts/{workflow-name}/

Tool selection rules:
- Use Read for: Known paths, standard files, files you just created
- Use Glob for: Discovery (finding multiple files by pattern)
- Use Grep for: Content search

Never glob for standard files:
✅ DO: Read .ambient/ambient.json
❌ DON'T: Glob **/ambient.json
```

### Style Guidelines

- Use markdown formatting (headers, lists, code blocks)
- Be specific about agent behavior, not vague
- Include error handling guidance
- Keep under ~5000 characters for readability

---

## Writing Commands

Commands go in `.claude/commands/{command-name}.md`.

### Command File Structure

```markdown
# /{command-name} - Short Description

## Purpose
What this command accomplishes.

## Prerequisites
- What must exist before running this command

## Process
1. Step one
2. Step two
3. Step three

## Output
- `artifacts/{workflow-name}/{output-file}.md`
```

### Naming Conventions

- Use kebab-case for filenames: `diagnose.md`, `root-cause.md`
- Use dot notation for related commands: `prd.create.md`, `prd.review.md`
- Command name in file should match filename (without extension)

---

## Writing Skills

Skills go in `.claude/skills/{skill-name}/SKILL.md`.

### Skill File Structure

```markdown
---
name: skill-name
description: Brief description of what this skill does
---

# Skill Name

[Detailed instructions for Claude when this skill is invoked]

## Your Role
...

## Process
...
```

### When to Use Skills vs Commands

| Use Commands for | Use Skills for |
|------------------|----------------|
| Single-phase tasks | Complex multi-step workflows |
| Workflow entry points | Reusable knowledge packages |
| User-invoked actions | Context that loads on-demand |

---

## Creating New Workflows

### Option 1: Use the workflow-creator skill

```text
Use the workflow-creator skill to create a new workflow for [purpose].
Put all files in workflows/{workflow-name}/.
```

### Option 2: Copy the template

```bash
cp -r workflows/template-workflow workflows/{new-workflow-name}
# Then customize .ambient/ambient.json
```

### Option 3: Create from scratch

1. Create the directory: `workflows/{name}/`
2. Create `.ambient/ambient.json` with all required fields
3. Add commands in `.claude/commands/`
4. Add README.md

### Checklist for New Workflows

- [ ] `.ambient/ambient.json` exists with all 4 required fields
- [ ] `systemPrompt` includes workspace navigation guidelines
- [ ] `systemPrompt` lists all available commands
- [ ] `systemPrompt` specifies output location (`artifacts/{name}/`)
- [ ] All commands have clear prerequisites and outputs
- [ ] README.md documents the workflow

---

## Modifying Existing Workflows

### Before Making Changes

1. Read the existing `ambient.json` to understand current behavior
2. Read existing commands to understand the workflow phases
3. Identify what specifically needs to change

### Safe Modification Patterns

**Adding a command:**

- Create new file in `.claude/commands/`
- Add the command to the `systemPrompt` command list
- Update `results` in ambient.json if new artifacts are created

**Modifying systemPrompt:**

- Preserve all existing commands unless removing them
- Keep workspace navigation guidelines
- Maintain the general structure (role, commands, phases, outputs)

**Changing artifact paths:**

- Update both `systemPrompt` and `results` field
- Consider backward compatibility

### Use workflow-editor for Complex Changes

For significant modifications, invoke the workflow-editor skill which validates changes and maintains consistency.

---

## Testing Changes

Before committing changes:

1. **Validate JSON**: Ensure `.ambient/ambient.json` is valid
2. **Check references**: Commands listed in systemPrompt exist as files
3. **Verify paths**: Output paths in systemPrompt match `results` patterns

### Testing in ACP

Use the "Custom Workflow" feature to test without merging to main:

1. Push your branch to GitHub
2. In ACP, select "Custom Workflow..."
3. Enter the repo URL, your branch name, and path
4. Test the workflow end-to-end

---

## Common Mistakes to Avoid

### JSON Errors

```json
// ❌ Trailing comma
{
  "name": "My Workflow",
}

// ✅ No trailing comma
{
  "name": "My Workflow"
}
```

### Vague SystemPrompts

```json
// ❌ Too vague
"systemPrompt": "You help with development"

// ✅ Specific and actionable
"systemPrompt": "You are a bug fix specialist.\n\n## Commands\n- /diagnose - Analyze root cause\n- /fix - Implement the fix\n\n## Output\nWrite all artifacts to artifacts/bugfix/"
```

### Missing Command References

```json
// ❌ Commands exist as files but not listed in systemPrompt
"systemPrompt": "You are a helper."  // But /diagnose.md exists

// ✅ All commands documented
"systemPrompt": "You are a helper.\n\n## Commands\n- /diagnose - Run diagnosis"
```

### Inconsistent Paths

```json
// ❌ systemPrompt says one thing, results say another
"systemPrompt": "Write to artifacts/bugs/",
"results": { "Reports": "output/reports/*.md" }

// ✅ Consistent paths
"systemPrompt": "Write to artifacts/bugfix/",
"results": { "Reports": "artifacts/bugfix/*.md" }
```

---

## Reference Documentation

| Document | Purpose |
|----------|---------|
| [WORKFLOW_DEVELOPMENT_GUIDE.md](WORKFLOW_DEVELOPMENT_GUIDE.md) | Complete development guide |
| [AMBIENT_JSON_SCHEMA.md](AMBIENT_JSON_SCHEMA.md) | ambient.json field reference |
| [WORKSPACE_NAVIGATION_GUIDELINES.md](WORKSPACE_NAVIGATION_GUIDELINES.md) | File navigation best practices |
| [README.md](README.md) | Repository overview |

---

## Quick Reference

### File Locations

| What | Where |
|------|-------|
| Workflow config | `workflows/{name}/.ambient/ambient.json` |
| Commands | `workflows/{name}/.claude/commands/*.md` |
| Skills | `workflows/{name}/.claude/skills/{skill}/SKILL.md` |
| Templates | `workflows/{name}/templates/` |
| Artifacts (runtime) | `artifacts/{name}/` |

### Required ambient.json Fields

```json
{
  "name": "Workflow Name",
  "description": "Brief description",
  "systemPrompt": "You are...\n\n## Commands\n...\n\n## Output\nartifacts/...",
  "startupPrompt": "Welcome! Use /command to start."
}
```

### Command File Template

```markdown
# /command-name - Description

## Purpose
What this does.

## Process
1. Step one
2. Step two

## Output
- `artifacts/{workflow}/output.md`
```
