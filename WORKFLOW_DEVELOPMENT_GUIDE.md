# Workflow Development Guide

Quick reference for creating and contributing custom workflows to the Ambient Code Platform.

## Quick Start

**Goal:** Create a custom workflow for your development process

**Time:** 30-60 minutes

**Starting Point:** Use the [template-workflow](workflows/template-workflow) as your foundation

## Creating a Custom Workflow

### 1. Copy the Template

```bash
cp -r workflows/template-workflow workflows/my-workflow
cd workflows/my-workflow
```

### 2. Configure Your Workflow

Edit `.ambient/ambient.json` (remove comments for production):

```json
{
  "name": "My Workflow Name",
  "description": "Brief description of what this workflow does and when to use it.",
  "systemPrompt": "You are a [role] assistant. Follow these phases: [phase1 → phase2 → phase3]. Use /command1, /command2 commands. Create outputs in artifacts/my-workflow/",
  "startupPrompt": "Welcome! I'll help you with [purpose]. Available commands: /command1, /command2. Run /command1 to begin.",
  "results": {
    "Output Type": "artifacts/my-workflow/**/*.md"
  }
}
```

**Required Fields:** name, description, systemPrompt, startupPrompt
**Optional Fields:** results, version, tags, icon (see [FIELD_REFERENCE.md](workflows/template-workflow/FIELD_REFERENCE.md))

### 3. Create Slash Commands

Add commands in `.claude/commands/`:

```markdown
# /mycommand - Short description

## Purpose
What this command accomplishes

## Prerequisites
- Files or state needed before running

## Process
1. Step one
2. Step two
3. Step three

## Output
- Creates: artifacts/my-workflow/output.md
- Updates: existing files if applicable

## Usage
/mycommand [optional-argument]
```

**Command Naming:** Use descriptive names (e.g., `/analyze`, `/implement`, `/verify`)

### 4. Agent Usage (Optional)

**Platform Agents Available:**
- **Amber** - Codebase intelligence, pair programming
- **Parker** - Product management, business value
- **Stella** - Staff engineer, technical leadership
- **Ryan** - UX research, user insights
- **Steve** - UX design, visual design
- **Terry** - Technical writing, documentation

**When to Add Custom Agents:**
- Workflow needs domain-specific expertise not covered by platform agents
- Specialized role unique to your workflow

**How to Add:**
Create `.claude/agents/my-agent.md`:

```markdown
# Agent Name - Role

## Expertise
- Domain area 1
- Domain area 2

## Responsibilities
- What this agent does
- When to invoke

## Communication Style
- How this agent communicates
```

**Best Practice:** Use platform agents first, add custom agents only when necessary

### 5. Test Your Workflow

1. **Load in ACP Session:**
   - Navigate to session detail page
   - Select "Custom Workflow"
   - Enter Git URL, branch, path

2. **Test Commands:**
   - Run each slash command
   - Verify outputs in `artifacts/`
   - Check for errors

3. **Iterate:**
   - Refine prompts based on behavior
   - Update commands for clarity
   - Adjust output paths

## Contributing to OOTB Workflows

Want to contribute your workflow to the official collection?

### Prerequisites
- Workflow tested in real sessions
- Complete documentation (README.md)
- Clear use case and value proposition

### Submission Process

1. **Fork Repository:**
   ```bash
   gh repo fork ambient-code/workflows
   cd workflows
   ```

2. **Add Your Workflow:**
   ```bash
   cp -r your-workflow workflows/your-workflow-name
   git add workflows/your-workflow-name
   git commit -m "feat: add [workflow-name] workflow"
   git push
   ```

3. **Submit Pull Request:**
   - Include workflow description
   - Example usage scenarios
   - Test results from real sessions
   - Screenshots/demos (optional)

4. **PR Requirements:**
   - [ ] Complete ambient.json configuration
   - [ ] README.md with usage instructions
   - [ ] At least 3 slash commands
   - [ ] Tested in live ACP session
   - [ ] No hardcoded secrets or sensitive data
   - [ ] Clear artifact output locations

## Best Practices

### Configuration
- **Start minimal:** Only required fields initially
- **Clear prompts:** Specific instructions yield better results
- **Output organization:** Use consistent artifact paths

### Slash Commands
- **Single purpose:** Each command does one thing well
- **Sequential or standalone:** Design for both linear and flexible usage
- **Clear documentation:** Prerequisites, process, outputs

### Agent Usage
- **Leverage platform agents:** Don't recreate what exists
- **Proactive engagement:** Commands should invoke agents automatically when needed
- **Clear orchestration:** Document when/why agents are invoked

### Testing
- **Real sessions:** Test in actual ACP environment
- **Multiple scenarios:** Try different use cases
- **User perspective:** Have others test your workflow

## Common Patterns

### Feature Development Workflow
```
/specify → /plan → /implement → /verify
```
Focus: New functionality, specifications, planning

### Bug Fix Workflow
```
/reproduce → /diagnose → /fix → /test → /document
```
Focus: Issue resolution, root cause, verification

### Code Review Workflow
```
/analyze → /review → /suggest → /validate
```
Focus: Quality, standards, best practices

### Refactoring Workflow
```
/assess → /plan → /refactor → /verify
```
Focus: Code improvement, maintaining behavior

## Troubleshooting

**Workflow not loading?**
- Check `.ambient/ambient.json` exists and is valid JSON
- Remove all comment lines for production
- Verify Git URL is accessible

**Commands not working?**
- Ensure files are in `.claude/commands/`
- File names must match command names (`/mycommand` → `mycommand.md`)
- Check markdown formatting

**Outputs in wrong location?**
- Always use `artifacts/` for outputs
- Use absolute paths: `/workspace/artifacts/my-workflow/`
- Check systemPrompt specifies correct paths

**Agents not responding?**
- Platform agents load automatically from platform context
- Custom agents must be in `.claude/agents/`
- Check agent file format and structure

## Resources

- **Template Workflow:** [workflows/template-workflow](workflows/template-workflow)
- **Field Reference:** [FIELD_REFERENCE.md](workflows/template-workflow/FIELD_REFERENCE.md)
- **Example Workflows:** [workflows/spec-kit](workflows/spec-kit), [workflows/bugfix](workflows/bugfix)
- **Platform Agents:** [platform/agents](https://github.com/ambient-code/platform/tree/main/agents)
- **Issues:** [github.com/ambient-code/workflows/issues](https://github.com/ambient-code/workflows/issues)

## Quick Reference

### Minimal Workflow Structure
```
my-workflow/
├── .ambient/
│   └── ambient.json          # Required: workflow config
├── .claude/
│   └── commands/             # Required: slash commands
│       └── mycommand.md
└── README.md                 # Recommended: documentation
```

### Standard Workflow Structure
```
my-workflow/
├── .ambient/
│   └── ambient.json
├── .claude/
│   ├── agents/               # Optional: custom agents
│   │   └── specialist.md
│   └── commands/             # Required: slash commands
│       ├── init.md
│       ├── execute.md
│       └── verify.md
├── scripts/                  # Optional: automation
├── templates/                # Optional: document templates
└── README.md
```

### Essential ambient.json
```json
{
  "name": "Workflow Name",
  "description": "What it does and when to use it.",
  "systemPrompt": "You are a [role] assistant...",
  "startupPrompt": "Welcome! Run /command to begin.",
  "results": {
    "Outputs": "artifacts/**/*.md"
  }
}
```

---

**Ready to build?** Start with `workflows/template-workflow` and customize for your needs!

**Questions?** Open an issue: [github.com/ambient-code/workflows/issues](https://github.com/ambient-code/workflows/issues)
