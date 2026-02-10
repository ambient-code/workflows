# AI Helpers Enabled

A workflow with the odh-ai-helpers marketplace automatically enabled, providing AI automation tools, plugins, and assistants for enhanced productivity.

## Overview

This workflow provides a development environment with the odh-ai-helpers marketplace pre-configured and enabled. The marketplace gives you immediate access to specialized AI automation tools, plugins, and productivity assistants without any additional setup.

The workflow guides you through a structured 5-phase approach for any development task:

### 1. Understand
Analyze the user's request and requirements. Ask clarifying questions, identify which marketplace tools might be helpful, and assess the scope and complexity of the task.

### 2. Plan
Create a structured approach to the task. Break down complex work into manageable steps, determine which AI helpers and plugins to use, and identify potential challenges and dependencies.

### 3. Execute
Implement the solution while leveraging marketplace capabilities. Write clean, well-documented code and use automation tools to streamline repetitive tasks.

### 4. Verify
Validate results and ensure quality. Test implementations thoroughly, review code for best practices and standards, and ensure all requirements are met.

### 5. Document
Provide clear documentation of what was accomplished, explain key decisions and approaches, and provide usage instructions and examples.

## Getting Started

### Prerequisites
- Ambient Code Platform session with workflow support
- Access to the odh-ai-helpers marketplace at `/opt/ai-helpers`
- Claude Code runner with marketplace support

### Installation
1. Load this workflow in your ACP session
2. The marketplace is automatically enabled - no setup required
3. Run `/helpers.validate` to confirm marketplace is operational

## Workflow Phases

### Phase 1: Understand
**No specific command - interactive discussion**

Begin by describing what you'd like to work on. The AI assistant will ask clarifying questions to understand your requirements and identify which marketplace tools might be helpful.

**Output:**
- Clear understanding of task requirements and goals

### Phase 2: Plan
**No specific command - interactive planning**

The assistant will create a structured approach to your task, breaking down complex work and determining which AI helpers and plugins to use.

**Output:**
- `artifacts/ai-helpers/docs/task-plan.md` - Structured plan for the task

### Phase 3: Execute
**Command:** `/helpers.scan-fips` (if applicable) or standard development workflow

Implement the solution while leveraging marketplace capabilities and automation tools.

**Output:**
- `artifacts/ai-helpers/code/` - Generated or modified code
- `artifacts/ai-helpers/reports/` - Analysis and scan results

### Phase 4: Verify
**Command:** `/helpers.validate` (for marketplace verification)

Validate that implementations meet requirements, test thoroughly, and review for best practices.

**Output:**
- `artifacts/ai-helpers/reports/validation-results.md` - Test and validation results

### Phase 5: Document
**No specific command - documentation generation**

Generate documentation explaining what was accomplished, key decisions, and usage instructions.

**Output:**
- `artifacts/ai-helpers/docs/` - Documentation and guides

## Available Agents

This workflow includes specialized expert agents:

### Helper - Marketplace Specialist
Expert in leveraging the odh-ai-helpers marketplace for enhanced development workflows.
**Expertise:** Marketplace integration, Plugin configuration, FIPS compliance, Automation tools, Troubleshooting

## Available Commands

### /helpers.list - List Available Plugins
Enumerates all available plugins and tools from the odh-ai-helpers marketplace, displaying their capabilities and current status.

**Usage:**
```
/helpers.list
```

### /helpers.validate - Validate Marketplace Configuration
Performs comprehensive validation of marketplace setup to ensure it is properly configured and accessible.

**Usage:**
```
/helpers.validate
```

### /helpers.scan-fips - Run FIPS Compliance Scan
Executes a FIPS compliance scan on the codebase using the fips-compliance-checker plugin.

**Usage:**
```
/helpers.scan-fips
```

Or scan a specific directory:
```
/helpers.scan-fips path/to/code
```

## Output Artifacts

All workflow outputs are saved in the `artifacts/ai-helpers/` directory:

```
artifacts/ai-helpers/
├── code/                    # Generated or modified code
├── docs/                    # Documentation and guides
│   ├── task-plan.md
│   ├── tool-recommendations.md
│   └── plugin-setup.md
└── reports/                 # Analysis and validation results
    ├── marketplace-validation.md
    ├── plugin-inventory.md
    ├── fips-compliance.md
    └── validation-results.md
```

## Example Usage

```bash
# Step 1: Validate marketplace is configured
/helpers.validate

# Step 2: See what plugins are available
/helpers.list

# Step 3: Work on your task
# Simply describe what you want to accomplish, and the assistant
# will leverage marketplace tools as appropriate

# Step 4: Run compliance scans if needed
/helpers.scan-fips

# Review outputs in artifacts/ai-helpers/
```

## Configuration

This workflow is configured via `.ambient/ambient.json`. Key settings:

- **Name:** AI Helpers Enabled
- **Description:** Marketplace-enabled workflow with AI automation tools
- **Artifact Path:** `artifacts/ai-helpers/`
- **Marketplace:** odh-ai-helpers at `/opt/ai-helpers`

### Claude Settings

The marketplace is enabled via `.claude/claude-settings.json`:

```json
{
  "extraKnownMarketplaces": {
    "odh-ai-helpers": {
      "source": {
        "source": "directory",
        "path": "/opt/ai-helpers"
      }
    }
  },
  "enabledPlugins": {
    "odh-ai-helpers@odh-ai-helpers": true
  }
}
```

## Marketplace Plugins

The odh-ai-helpers marketplace includes:

### fips-compliance-checker
Scans codebase for FIPS 140-2/140-3 compliance issues.
- Detects non-approved cryptographic algorithms
- Identifies weak key lengths
- Finds deprecated cryptographic functions
- Provides remediation recommendations

### odh-ai-helpers
AI automation tools and productivity assistants.
- Enhanced development capabilities
- Automated workflow tools
- Productivity plugins

## Customization

You can extend this workflow by:

1. **Adding Custom Agents**: Create new agent personas in `.claude/agents/`
2. **Creating Commands**: Add workflow-specific commands in `.claude/commands/`
3. **Modifying System Prompt**: Edit `.ambient/ambient.json` to customize AI behavior
4. **Adding Templates**: Create template files for common tasks in a `templates/` directory

## Best Practices

1. **Validate First**: Always run `/helpers.validate` when starting a session to ensure marketplace is available
2. **Explore Plugins**: Use `/helpers.list` to discover what tools are available before starting work
3. **Leverage Automation**: Take advantage of marketplace plugins to automate repetitive tasks
4. **Document Results**: Maintain clear documentation of work performed and tools used
5. **Review Scan Results**: Carefully review automated scan results - some findings may be false positives

## Troubleshooting

**Problem:** Marketplace not available / validation fails
**Solution:**
- Verify you're in an ACP session with marketplace support
- Check that `/opt/ai-helpers` directory exists and is accessible
- Review `.claude/claude-settings.json` configuration
- Contact support if issues persist

**Problem:** fips-compliance-checker plugin not found
**Solution:**
- Run `/helpers.list` to see available plugins
- Verify marketplace is properly configured
- Check that plugin is installed in `/opt/ai-helpers`

**Problem:** Scan results seem incorrect
**Solution:**
- Review scan configuration and target directory
- Some findings may be false positives - investigate each
- Consult security team for compliance interpretation
- Re-run scan after making changes to verify fixes

## Contributing

To improve this workflow:
1. Fork the repository
2. Make your changes
3. Test thoroughly in an ACP session
4. Submit a pull request with description

## License

MIT License

## Support

For issues or questions:
- Run `/helpers.validate` to diagnose configuration issues
- Review generated reports in `artifacts/ai-helpers/reports/`
- Refer to the [ACP documentation](https://ambient-code.github.io/vteam)
- Check the [ai-helpers repository](https://github.com/opendatahub-io/ai-helpers)

---

**Created with:** ACP Workflow Creator
**Workflow Type:** Custom (Marketplace Integration)
**Version:** 1.0.0
