# Template Workflow for Ambient Code Platform

A comprehensive, self-contained template workflow demonstrating all available configuration options for the Ambient Code Platform (ACP). Use this as a starting point for creating custom workflows.

## Overview

This template provides a complete example of an ACP workflow, including:
- **Configuration**: Fully documented `ambient.json` with all available fields
- **Slash Commands**: Example commands demonstrating workflow phases
- **Agent Personas**: Sample agent files showing different roles and expertise
- **Documentation**: Complete inline comments and usage examples

## What's Included

### Directory Structure

```
template-workflow/
├── .ambient/
│   └── ambient.json         # Workflow configuration with inline documentation
├── .claude/
│   ├── agents/              # Example agent personas
│   │   ├── example-architect.md
│   │   ├── example-engineer.md
│   │   └── example-product-manager.md
│   └── commands/            # Example slash commands
│       ├── init.md          # Initialize workspace
│       ├── analyze.md       # Analyze requirements
│       ├── plan.md          # Create implementation plan
│       ├── execute.md       # Execute implementation
│       └── verify.md        # Verify and validate
└── README.md                # This file
```

### Configuration File: `.ambient/ambient.json`

The `ambient.json` file is the heart of your workflow configuration. It defines:

- **name**: Display name of the workflow
- **description**: What the workflow does and when to use it
- **systemPrompt**: Core instructions defining the agent's role and behavior
- **startupPrompt**: Initial greeting and instructions shown to users
- **results**: Output artifacts and where to find them

The template includes extensive inline comments documenting:
- All required and optional fields
- Best practices for each field
- Multiple examples and use cases
- Common patterns and anti-patterns

**Important**: JSON doesn't natively support comments, so you'll need to remove the comment lines (`// ...`) before using the file in production, or use a JSON5/JSONC parser.

### Slash Commands: `.claude/commands/`

Five example commands demonstrating a complete workflow:

1. **`/init`** - Initialize the workflow workspace
   - Creates directory structure
   - Sets up configuration
   - Prepares the environment

2. **`/analyze`** - Analyze requirements and context
   - Gathers information from the codebase
   - Documents findings
   - Identifies gaps and challenges

3. **`/plan`** - Create implementation plan or specification
   - Designs the solution
   - Breaks down the work
   - Documents technical decisions

4. **`/execute`** - Execute implementation
   - Writes code following the plan
   - Creates tests
   - Generates documentation

5. **`/verify`** - Verify and validate implementation
   - Runs all tests
   - Performs quality checks
   - Generates verification report

Each command file includes:
- Purpose and prerequisites
- Detailed process steps
- Output artifacts and locations
- Usage examples
- Notes and best practices

### Agent Personas: `.claude/agents/`

The template includes three **example agents** demonstrating different roles. These are for illustration purposes only.

**For Production Use:**

1. **Platform Agents** - If your workflow runs in the Ambient Code Platform, agents from `platform/agents/` will be automatically loaded:
   - **Amber** - Codebase intelligence, pair programming, proactive maintenance
   - **Parker** (Product Manager) - Market strategy, customer feedback, business value
   - **Ryan** (UX Researcher) - User insights, data analysis, evidence-based decisions
   - **Stella** (Staff Engineer) - Technical leadership, implementation excellence, mentoring
   - **Steve** (UX Designer) - Visual design, prototyping, user interface creation
   - **Terry** (Technical Writer) - User-centered documentation, technical accuracy

2. **Custom Agents** - Replace the example agents with your own workflow-specific personas as needed

**Note:** Workflows are self-contained. If you want to use agents, either:
- Rely on platform agents being loaded from context
- Include your own agent definitions in `.claude/agents/`
- Or both - custom agents can complement platform agents

Each agent file includes:
- Role and expertise
- Responsibilities
- Communication style
- When to invoke the agent
- Tools and techniques
- Key principles
- Example artifacts

## How to Use This Template

### Option 1: Use As-Is for Learning

1. Load this workflow in your ACP session
2. Explore the configuration and examples
3. Try out the slash commands
4. Understand how workflows are structured

### Option 2: Customize for Your Needs

1. **Copy the template**
   ```bash
   cp -r template-workflow/ my-custom-workflow/
   cd my-custom-workflow/
   ```

2. **Edit `.ambient/ambient.json`**
   - Remove the comment lines (or use a JSON5 parser)
   - Update `name` and `description` for your workflow
   - Customize `systemPrompt` to define your agent's role
   - Modify `startupPrompt` for your greeting
   - Adjust `results` to match your outputs
   - Remove optional fields you don't need

3. **Customize slash commands**
   - Modify existing commands in `.claude/commands/`
   - Add new commands as needed
   - Remove commands you don't need
   - Follow the structure in the examples

4. **Adapt agent personas (optional)**
   - Platform agents (Amber, Parker, Stella, etc.) are automatically available
   - Remove the example agents - they're just for illustration
   - Add workflow-specific agents only if needed for unique expertise
   - Platform agents handle most common roles

5. **Test your workflow**
   - Load it in an ACP session
   - Run through the commands
   - Verify outputs are correct
   - Iterate and refine

### Option 3: Create a Minimal Workflow

Start with just the essentials:

1. **Create minimal structure**
   ```bash
   mkdir -p my-workflow/.ambient
   mkdir -p my-workflow/.claude/commands
   ```

2. **Create basic `ambient.json`**
   ```json
   {
     "name": "My Workflow",
     "description": "A custom workflow for [purpose]",
     "systemPrompt": "You are a [role] assistant...",
     "startupPrompt": "Welcome! I'll help you with..."
   }
   ```

3. **Add one or two commands**
   - Start with the commands you actually need
   - Expand over time

4. **Skip custom agents initially**
   - Platform agents (Amber, Stella, Parker, etc.) are already available
   - Add workflow-specific agents only if truly needed

## Best Practices

### Configuration

1. **Keep it focused**: One workflow per process type
2. **Clear naming**: Use descriptive names that indicate purpose
3. **Document prompts**: Explain what the agent should do
4. **Define outputs**: Specify where artifacts are created
5. **Test thoroughly**: Validate in real sessions

### Slash Commands

1. **Single responsibility**: Each command does one thing well
2. **Clear structure**: Use consistent format across commands
3. **Prerequisites**: State what's needed before running
4. **Expected outputs**: Document what files are created
5. **Usage examples**: Show how to use the command

### Agent Personas

1. **Leverage platform agents**: Use Amber, Parker, Stella, Ryan, Steve, Terry from the platform
2. **Add custom agents sparingly**: Only create workflow-specific agents for unique expertise
3. **Clear expertise**: Define what each agent knows
4. **Communication style**: Give each agent a personality
5. **When to invoke**: Explain when to use each agent

### Directory Organization

1. **Artifacts separate**: Keep workflow logic and outputs separate
   - Workflow: `workflows/my-workflow/`
   - Outputs: `artifacts/`

2. **Follow conventions**:
   ```
   .ambient/          # Workflow configuration
   .claude/
     agents/          # Agent persona files
     commands/        # Slash command files
   scripts/           # Automation scripts (optional)
   templates/         # Document templates (optional)
   README.md          # Workflow documentation
   ```

## Field Reference

### Required Fields in `ambient.json`

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Display name of the workflow |
| `description` | string | What the workflow does |
| `systemPrompt` | string | Agent's core instructions |
| `startupPrompt` | string | Initial greeting to users |

### Optional Fields in `ambient.json`

| Field | Type | Description |
|-------|------|-------------|
| `results` | object | Output artifacts and locations |
| `version` | string | Semantic version of workflow |
| `author` | string/object | Workflow author information |
| `repository` | string/object | Source repository URL |
| `tags` | array | Keywords for discovery |
| `icon` | string | Emoji or icon identifier |
| `displayName` | string | Alternative display name |
| `license` | string | License type |
| `dependencies` | object/array | Required tools or workflows |
| `environment` | object | Environment variables |
| `hooks` | object | Lifecycle hooks |
| `settings` | object | Workflow-specific settings |
| `metadata` | object | Custom metadata |

See `.ambient/ambient.json` for detailed documentation on each field with examples.

## Workflow Phases

This template demonstrates a typical workflow structure:

1. **Initialize**: Set up workspace and environment
2. **Analyze**: Understand the problem and gather context
3. **Plan**: Design the solution and create specifications
4. **Execute**: Implement the solution
5. **Verify**: Validate and document the results

You can adapt these phases to match your specific workflow needs.

## Common Workflow Patterns

### Feature Development Workflow
- Specify → Plan → Tasks → Implement → Review
- Focus on new functionality
- Emphasis on specifications and planning

### Bug Fix Workflow
- Reproduce → Analyze → Fix → Verify → Document
- Focus on issue resolution
- Emphasis on root cause analysis

### Code Review Workflow
- Review → Feedback → Iterate → Approve
- Focus on quality and standards
- Emphasis on collaboration

### Refactoring Workflow
- Analyze → Plan → Refactor → Test → Document
- Focus on improving existing code
- Emphasis on maintaining behavior

### Migration Workflow
- Assess → Plan → Execute → Validate → Cutover
- Focus on moving from old to new
- Emphasis on risk mitigation

## Integration with ACP

### Loading the Workflow

**Via UI:**
1. Navigate to your session detail page
2. Open the **Workflows** accordion
3. Select **Custom Workflow...**
4. Enter repository URL, branch, and path
5. Click **Load Workflow**

**Via API:**
```bash
POST /api/projects/{project}/agentic-sessions/{session}/workflow

{
  "gitUrl": "https://github.com/your-org/my-workflow.git",
  "branch": "main",
  "path": "workflows/template-workflow"
}
```

### Workspace Structure

When loaded, your workflow appears at:
```
/workspace/sessions/{session-name}/workflows/template-workflow/
```

Outputs are written to:
```
/workspace/sessions/{session-name}/artifacts/
```

### Using Slash Commands

In your ACP session:
```
/init                           # Run initialization
/analyze user authentication    # Analyze a topic
/plan OAuth2 implementation     # Create a plan
/execute authentication system  # Implement
/verify authentication          # Validate
```

## Troubleshooting

### Workflow Not Loading

**Problem**: Workflow doesn't appear in session
**Solutions**:
- Verify Git URL is accessible
- Check branch exists
- Validate path within repository
- Ensure .ambient/ambient.json exists

### Commands Not Working

**Problem**: Slash commands don't execute
**Solutions**:
- Verify files are in `.claude/commands/`
- Check file names match command names
- Ensure files are markdown format
- Confirm workflow is loaded in session

### Invalid Configuration

**Problem**: ambient.json causes errors
**Solutions**:
- Remove all comment lines (`// ...`)
- Validate JSON syntax
- Check all required fields present
- Use JSON validator/linter

### Outputs in Wrong Location

**Problem**: Files created in wrong directory
**Solutions**:
- Always use `artifacts/` for outputs
- Use absolute paths in scripts
- Check systemPrompt specifies correct paths
- Review command documentation

## Examples and Inspiration

### Example Workflows

Look at these real-world workflows for inspiration:
- **Spec Kit**: Feature planning and implementation
- **Bug Fix**: Issue triage and resolution
- **Code Review**: Quality assurance and feedback

### Community Resources

- **Documentation**: [ACP User Guide](https://ambient-code.github.io/vteam)
- **Discussions**: [GitHub Discussions](https://github.com/ambient-code/ootb-ambient-workflows/discussions)
- **Issues**: [GitHub Issues](https://github.com/ambient-code/ootb-ambient-workflows/issues)

## Contributing

To improve this template:

1. Fork the repository
2. Make your improvements
3. Test thoroughly
4. Submit a pull request

## License

This template workflow is provided under the MIT License. You are free to use, modify, and distribute it as needed.

## Support

- **Questions**: Open a discussion on GitHub
- **Issues**: Report bugs via GitHub Issues
- **Documentation**: Check the ACP user guide

---

**Template Version**: 1.0.0
**Last Updated**: 2025-11-13
**Maintained By**: Ambient Code Platform Team
