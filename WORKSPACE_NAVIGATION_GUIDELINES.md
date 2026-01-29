# Workspace Navigation Guidelines for Workflow SystemPrompts

**Purpose**: Reduce Claude's file-finding fumbles and unnecessary tool use by providing clear workspace structure knowledge in systemPrompts.

## The Problem

Claude often struggles to find files in the workspace, leading to inefficient patterns like:

1. Tries to read file at wrong path → fails
2. Uses Glob to search → finds file
3. Finally reads it successfully

This wastes time, tokens, and creates a poor user experience.

## The Solution

Add workspace structure guidelines to your workflow's `systemPrompt` in `ambient.json`.

---

## Workspace Navigation Guidelines (Copy into systemPrompt)

```markdown
## Workspace Structure & File Navigation

**IMPORTANT: Follow these rules to avoid fumbling when looking for files.**

### Standard Workspace Structure

```

/workspace/sessions/{session-name}/
├── workflows/
│   └── {workflow-name}/          ← Your working directory
│       ├── .ambient/
│       │   └── ambient.json      ← ALWAYS at this path
│       ├── .claude/
│       │   ├── agents/           ← Agent definitions
│       │   └── commands/         ← Slash commands
│       ├── .specify/             ← (Optional) Specify framework
│       └── README.md
└── artifacts/                     ← All outputs go here
    └── {workflow-name}/

```

### File Location Rules

**Always at these exact paths:**
- Workflow config: `.ambient/ambient.json` (from workflow root)
- Agent files: `.claude/agents/*.md`
- Commands: `.claude/commands/*.md`
- Templates: `.specify/templates/*.md` (if using Specify)

**Never search for these - use direct paths:**
```bash
# ✅ DO: Use known paths directly
Read .ambient/ambient.json

# ❌ DON'T: Search for well-known files
Glob **/ambient.json
```

### Tool Selection Rules

**Use Read when:**

- You know the exact file path
- File is at a standard location (ambient.json, README.md, etc.)
- You just created the file and know where it is

**Use Glob when:**

- You genuinely don't know the file location
- Searching for files by pattern (*.md,*.json)
- Discovering what files exist

**Use Grep when:**

- Searching for content within files
- Finding files containing specific text
- Code search

### Path Resolution

**Relative to workflow root:**

```bash
.ambient/ambient.json              ← Config
.claude/agents/quinn-architect.md  ← Agent
artifacts/workflow-name/plan.md    ← Output
```

**Absolute paths in outputs:**

- Always write artifacts to absolute path: `/workspace/artifacts/{workflow-name}/`
- Ensures outputs survive workflow switching

### Common Mistakes to Avoid

❌ **DON'T glob for files you just created:**

```bash
Write artifacts/plan.md
Glob **/plan.md                    ← You just created it!
```

✅ **DO use the path you just wrote to:**

```bash
Write artifacts/plan.md
Read artifacts/plan.md             ← Direct path
```

❌ **DON'T search for standard files:**

```bash
Glob **/ambient.json               ← Always at .ambient/ambient.json
```

✅ **DO use known locations:**

```bash
Read .ambient/ambient.json         ← Standard location
```

### File Creation Memory

**Keep track of files you create in this session:**

- Note the exact path when you write a file
- Reference that path directly later
- Don't re-search for files you just created

### Quick Reference

| File Type | Location | Use Read or Glob? |
|-----------|----------|-------------------|
| ambient.json | `.ambient/ambient.json` | Read |
| Agents | `.claude/agents/*.md` | Glob (multiple files) |
| Commands | `.claude/commands/*.md` | Glob (multiple files) |
| Templates | `.specify/templates/*.md` | Glob (multiple files) |
| README | `README.md` | Read |
| Artifacts (created by you) | Path you just wrote to | Read |
| User's project files | Unknown | Grep/Glob |

```

---

## Integration Examples

### Example 1: Template Workflow

```json
{
  "name": "Template Workflow",
  "systemPrompt": "You are a workflow assistant for the Ambient Code Platform.

## Workspace Structure & File Navigation

**Standard paths from workflow root:**
- Config: `.ambient/ambient.json`
- Agents: `.claude/agents/*.md`
- Commands: `.claude/commands/*.md`
- Outputs: `artifacts/template/`

**File location rules:**
- Use Read for known paths (ambient.json, README.md, files you just created)
- Use Glob for discovery (finding multiple files by pattern)
- Use Grep for content search

**Never glob for standard files - use direct paths:**
✅ Read .ambient/ambient.json
❌ Glob **/ambient.json

... [rest of systemPrompt]"
}
```

### Example 2: Specsmith Workflow

```json
{
  "name": "Specsmith Workflow",
  "systemPrompt": "You are Specsmith, a spec-driven development assistant.

## Workspace Navigation

**Your working directory:** workflows/specsmith-workflow/
**Output directory:** artifacts/specsmith/

**Known file locations:**
- Config: `.ambient/ambient.json`
- Agents: `.claude/agents/quinn-architect.md`, `.claude/agents/maya-engineer.md`
- Interview template: `.specify/templates/interview-template.md`

**Tool selection:**
- Read: For known paths and files you created
- Glob: For discovering user's project files
- Grep: For searching code content

**Files you create during workflow:**
- artifacts/specsmith/interview-notes.md (use Read after Write)
- artifacts/specsmith/PLAN.md (use Read after Write)
- artifacts/specsmith/validation-report.md (use Read after Write)

... [rest of systemPrompt]"
}
```

---

## Benefits

**Efficiency gains:**

- ✅ Reduce tool calls by 30-50% for file operations
- ✅ Faster response times (fewer round-trips)
- ✅ Lower token usage
- ✅ Better user experience (less fumbling)

**Example reduction:**

```
Before guidelines:
1. Read /workspace/workflows/workflow/ambient.json (fail)
2. Glob **/ambient.json (success)
3. Read .ambient/ambient.json (success)
Total: 3 tool calls

After guidelines:
1. Read .ambient/ambient.json (success)
Total: 1 tool call

Reduction: 67% fewer tools calls
```

---

## Checklist for Workflow Authors

When creating a workflow's systemPrompt, include:

- [ ] Standard workspace structure diagram
- [ ] Known file location paths specific to your workflow
- [ ] Tool selection rules (Read vs Glob vs Grep)
- [ ] List of files your workflow creates and their paths
- [ ] Reminder to use direct paths for known files
- [ ] Warning against globbing for standard files

---

## See Also

- [AMBIENT_JSON_SCHEMA.md](AMBIENT_JSON_SCHEMA.md) - Complete ambient.json reference
- [README.md](README.md) - Workflow development guide
- Template workflow: `workflows/template-workflow/.ambient/ambient.json`
