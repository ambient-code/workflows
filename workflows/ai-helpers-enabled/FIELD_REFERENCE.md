# AI Helpers Enabled - Field Reference

This document provides detailed information about the configuration fields in `.ambient/ambient.json` and explains how to customize the workflow.

## Required Fields

### name
- **Type:** string
- **Purpose:** Display name shown in ACP UI
- **Current Value:** "AI Helpers Enabled"
- **Guidelines:** Keep concise (2-5 words), use title case

### description
- **Type:** string
- **Purpose:** Explains workflow purpose in UI
- **Current Value:** "A workflow with the odh-ai-helpers marketplace automatically enabled, providing AI automation tools, plugins, and assistants for enhanced productivity."
- **Guidelines:** 1-3 sentences, clear and specific about marketplace integration

### systemPrompt
- **Type:** string
- **Purpose:** Defines AI agent's role and behavior
- **Current Value:** See `.ambient/ambient.json`
- **Guidelines:**
  - Start with clear role definition emphasizing marketplace capabilities
  - List key responsibilities for guiding users
  - Reference available slash commands (/helpers.*)
  - Specify output locations (artifacts/ai-helpers/)
  - Include workspace navigation rules
  - Explain marketplace capabilities and best practices

**Key Sections in System Prompt:**
1. **KEY RESPONSIBILITIES** - What the AI assistant does
2. **WORKFLOW METHODOLOGY** - 5-phase approach (Understand → Plan → Execute → Verify → Document)
3. **AVAILABLE COMMANDS** - List of /helpers.* commands
4. **OUTPUT LOCATIONS** - Where artifacts are created
5. **WORKSPACE NAVIGATION** - File finding rules
6. **MARKETPLACE CAPABILITIES** - Available plugins and tools
7. **BEST PRACTICES** - Guidance for effective workflow usage

### startupPrompt
- **Type:** string
- **Purpose:** Initial message when workflow activates
- **Current Value:** See `.ambient/ambient.json`
- **Guidelines:**
  - Greet user warmly
  - Highlight marketplace integration as key differentiator
  - List workflow phases
  - Show available commands
  - Provide clear next steps for getting started

## Optional Fields

### results
- **Type:** object with string values (glob patterns)
- **Purpose:** Maps artifact types to file paths for ACP UI
- **Current Value:**
  ```json
  {
    "All Artifacts": "artifacts/ai-helpers/**/*",
    "Documentation": "artifacts/ai-helpers/docs/**/*.md",
    "Code": "artifacts/ai-helpers/code/**/*",
    "Reports": "artifacts/ai-helpers/reports/**/*.md"
  }
  ```
- **Guidelines:** Use glob patterns to match multiple files, organize by artifact type

### version
- **Type:** string
- **Example:** "1.0.0"
- **Purpose:** Track workflow configuration version
- **Not currently used but recommended for future releases**

### author
- **Type:** string or object
- **Example:** {"name": "Your Name", "email": "you@example.com"}
- **Purpose:** Identify workflow creator
- **Useful for multi-team environments**

### tags
- **Type:** array of strings
- **Example:** ["marketplace", "ai-helpers", "automation", "fips-compliance"]
- **Purpose:** Categorize workflow for discovery in ACP
- **Helpful for organizations with many workflows**

### icon
- **Type:** string (emoji)
- **Example:** "🔧" or "🤖"
- **Purpose:** Visual identifier in ACP UI
- **Makes workflow easier to recognize**

## Claude Settings Configuration

The marketplace is enabled via `.claude/claude-settings.json`:

### extraKnownMarketplaces
- **Type:** object
- **Purpose:** Registers additional marketplaces beyond defaults
- **Structure:**
  ```json
  {
    "marketplace-id": {
      "source": {
        "source": "directory",
        "path": "/path/to/marketplace"
      }
    }
  }
  ```
- **Current Value:**
  ```json
  {
    "odh-ai-helpers": {
      "source": {
        "source": "directory",
        "path": "/opt/ai-helpers"
      }
    }
  }
  ```

### enabledPlugins
- **Type:** object with boolean values
- **Purpose:** Controls which plugins are automatically enabled
- **Structure:**
  ```json
  {
    "marketplace-id@plugin-name": true
  }
  ```
- **Current Value:**
  ```json
  {
    "odh-ai-helpers@odh-ai-helpers": true
  }
  ```

## Customization Examples

### Adding a New Command

Create a new file in `.claude/commands/`:

```markdown
# /helpers.mycmd - My Custom Command

## Purpose
What this command does...

## Prerequisites
- What must exist first

## Process
1. Step one
2. Step two

## Output
- Where files are created

## Usage Examples
\`\`\`
/helpers.mycmd
\`\`\`
```

Then update `systemPrompt` in `.ambient/ambient.json`:

```
AVAILABLE COMMANDS:
- /helpers.list - List available marketplace plugins
- /helpers.validate - Validate marketplace configuration
- /helpers.scan-fips - Run FIPS compliance scan
- /helpers.mycmd - My custom command
```

### Changing Artifact Location

To change where outputs are saved:

1. Update `systemPrompt` OUTPUT LOCATIONS section:
   ```
   OUTPUT LOCATIONS:
   - Create all artifacts in: artifacts/my-new-path/
   ```

2. Update `results` section:
   ```json
   "results": {
     "All Artifacts": "artifacts/my-new-path/**/*",
     "Documentation": "artifacts/my-new-path/docs/**/*.md"
   }
   ```

3. Update all command files in `.claude/commands/` to reference new path

### Adding Environment-Specific Configuration

Add to `.ambient/ambient.json`:

```json
{
  "name": "AI Helpers Enabled",
  "environment": {
    "MARKETPLACE_PATH": "/opt/ai-helpers",
    "ARTIFACTS_ROOT": "artifacts/ai-helpers",
    "LOG_LEVEL": "info"
  }
}
```

### Customizing Marketplace Path

If your marketplace is at a different location:

1. Update `.claude/claude-settings.json`:
   ```json
   {
     "extraKnownMarketplaces": {
       "odh-ai-helpers": {
         "source": {
           "source": "directory",
           "path": "/custom/path/to/ai-helpers"
         }
       }
     }
   }
   ```

2. Update validation scripts to check new path

3. Update command documentation references

## Agent Files

Agent persona files are located in `.claude/agents/` and follow this structure:

```markdown
# Name - Role
## Role
## Expertise
## Responsibilities
## Communication Style
## When to Invoke
## Tools and Techniques
## Key Principles
## Example Artifacts
```

**Current Agents:**
- `helper-marketplace-specialist.md` - Expert in marketplace integration and plugin usage

**Adding New Agents:**

Create a new file `.claude/agents/myagent-myrole.md` following the template above. The agent will be automatically available for invocation when the workflow loads.

## Command Files

Slash command files are located in `.claude/commands/` and follow this structure:

```markdown
# /command.name - Description
## Purpose
## Prerequisites
## Process
## Output
## Usage Examples
## Success Criteria
## Next Steps
## Notes
```

**Current Commands:**
- `helpers.list.md` - List marketplace plugins
- `helpers.validate.md` - Validate marketplace configuration
- `helpers.scan-fips.md` - Run FIPS compliance scan

**Adding New Commands:**

Create files using the format `{prefix}.{action}.md`. Commands should align with the workflow's purpose (marketplace integration and AI-assisted development).

## File Naming Conventions

- **Workflow directory:** `workflows/ai-helpers-enabled/`
- **Agent files:** `{name}-{role}.md` (e.g., `helper-marketplace-specialist.md`)
- **Command files:** `{prefix}.{action}.md` (e.g., `helpers.validate.md`)
- **Artifacts:** `artifacts/ai-helpers/{category}/{files}`

**Guidelines:**
- Use lowercase for all file names
- Use hyphens for agent files
- Use dots for command files
- Be descriptive but concise

## Validation Checklist

Before deploying this workflow, verify:

- [ ] `.ambient/ambient.json` is valid JSON (no comments in production file)
- [ ] All required fields are present (name, description, systemPrompt, startupPrompt)
- [ ] `.claude/claude-settings.json` properly configures marketplace
- [ ] All agent files follow the template structure
- [ ] All command files have unique names and proper format
- [ ] Output paths in config match those in command files
- [ ] README.md accurately describes the workflow
- [ ] All file references use correct paths
- [ ] Marketplace path (`/opt/ai-helpers`) is appropriate for target environment

## Testing Checklist

After loading the workflow in an ACP session:

- [ ] Run `/helpers.validate` to verify marketplace configuration
- [ ] Run `/helpers.list` to confirm plugins are accessible
- [ ] Test `/helpers.scan-fips` on a sample codebase
- [ ] Verify artifacts are created in correct locations
- [ ] Check that agent can be invoked properly
- [ ] Confirm marketplace tools are accessible
- [ ] Review generated documentation and reports

## Marketplace Integration Details

### Plugin Discovery

The workflow discovers plugins by:
1. Reading `/opt/ai-helpers/.claude-plugin/marketplace.json`
2. Parsing plugin definitions from the metadata file
3. Checking plugin source paths (URL or local directory)
4. Verifying plugin accessibility

### Plugin Activation

Plugins are activated through:
1. Registration in `.claude/claude-settings.json` under `extraKnownMarketplaces`
2. Enablement in `enabledPlugins` section
3. Automatic loading when workflow starts
4. Availability for invocation via commands

### Common Marketplace Paths

- **Production ACP:** `/opt/ai-helpers`
- **Development:** `/workspace/repos/ai-helpers`
- **Custom Install:** Specify in `.claude/claude-settings.json`

## References

- [ACP Documentation](https://ambient-code.github.io/vteam)
- [Template Workflow](https://github.com/ambient-code/workflows/tree/main/workflows/template-workflow)
- [ai-helpers Repository](https://github.com/opendatahub-io/ai-helpers)
- [Workflow Best Practices](https://ambient-code.github.io/vteam/guides/workflows)
- [Claude Settings Schema](https://docs.anthropic.com/claude/docs/claude-settings)

## Troubleshooting Common Issues

**Issue:** JSON parse error in ambient.json
**Solution:** Ensure no trailing commas, comments, or syntax errors. Validate with `jq . .ambient/ambient.json`

**Issue:** Commands not appearing
**Solution:** Check file names follow `{prefix}.{action}.md` pattern, verify files are in `.claude/commands/`

**Issue:** Marketplace not loading
**Solution:** Verify path in `.claude/claude-settings.json` matches actual marketplace location

**Issue:** Plugins not found
**Solution:** Run `/helpers.validate` to diagnose, check `/opt/ai-helpers` exists and contains `.claude-plugin/marketplace.json`

---

For additional help, refer to the main README.md or ACP documentation.
