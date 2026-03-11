# Ambient.json Field Reference

Quick reference guide for all fields available in the `ambient.json` configuration file.

## Required Fields

### `name` (string)
**Display name of the workflow**

- Shown in ACP UI and CLI
- Should be short and descriptive (2-5 words)
- Use title case

**Examples:**
```json
"name": "Plan a feature"
"name": "Bug Triage Workflow"
"name": "Code Review Assistant"
```

---

### `description` (string)
**Detailed description of the workflow**

- Explains what the workflow does and when to use it
- Appears in workflow selection UI
- 1-3 sentences recommended

**Examples:**
```json
"description": "Spec driven development workflow for feature planning, task breakdown, and implementation."
"description": "Streamlined workflow for bug triage, root cause analysis, and fix implementation with automated testing."
```

---

### `systemPrompt` (string)
**Core instructions defining the agent's behavior**

- Defines the agent's role, capabilities, and methodology
- Loaded into agent context at session start
- Should include:
  - Role definition ("You are a...")
  - Key responsibilities
  - Available slash commands
  - Methodology or workflow phases
  - Output locations
  - Setup instructions

**Example:**
```json
"systemPrompt": "You are a spec-driven development assistant. Follow the spec-kit methodology: specification → planning → task breakdown → implementation. Use slash commands: /specify, /plan, /tasks, /implement. Create all documents in the specs/ directory."
```

---

### `startupPrompt` (string)
**Initial greeting and instructions**

- First message shown to users
- Should include:
  - Warm greeting
  - Role introduction
  - Available commands
  - How to get started
  - First-time setup instructions

**Example:**
```json
"startupPrompt": "Welcome! I'm your Feature Planning assistant. Available commands: /specify, /plan, /tasks, /implement. Run /specify [feature-description] to start."
```

---

## Optional Fields

### `results` (object)
**Output artifacts and their locations**

- Maps artifact names to file paths/glob patterns
- Helps users locate generated files
- Supports glob patterns (*, **)

**Structure:**
```json
"results": {
  "Artifact Name": "path/to/files/**/*.md",
  "Another Artifact": "path/to/file.json"
}
```

**Example:**
```json
"results": {
  "Feature Specification": "artifacts/specs/**/spec.md",
  "Implementation Plan": "artifacts/specs/**/plan.md",
  "Task Breakdown": "artifacts/specs/**/tasks.md",
  "Test Results": "artifacts/test-results/**/*.xml"
}
```

---

### `version` (string)
**Semantic version of the workflow**

- Useful for tracking changes
- Follows semver format (MAJOR.MINOR.PATCH)

**Example:**
```json
"version": "1.2.3"
```

---

### `author` (string or object)
**Workflow author information**

**String format:**
```json
"author": "Your Name"
```

**Object format:**
```json
"author": {
  "name": "Your Name",
  "email": "you@example.com",
  "organization": "Your Company"
}
```

---

### `repository` (string or object)
**Source repository for the workflow**

**String format:**
```json
"repository": "https://github.com/org/workflow-repo"
```

**Object format:**
```json
"repository": {
  "type": "git",
  "url": "https://github.com/org/workflow-repo",
  "branch": "main"
}
```

---

### `tags` (array of strings)
**Keywords or categories**

- Used for discovery and filtering
- Helps users find relevant workflows

**Example:**
```json
"tags": ["feature-development", "planning", "implementation"]
```

**Common tags:**
- `feature-development`
- `bug-fix`
- `code-review`
- `refactoring`
- `testing`
- `documentation`
- `deployment`
- `migration`

---

### `icon` (string)
**Emoji or icon identifier**

- Displayed in UI alongside workflow name
- Use single emoji

**Examples:**
```json
"icon": "🔧"
"icon": "🐛"
"icon": "📝"
"icon": "🚀"
```

**Common icons:**
- 🔧 - Tools/Configuration
- 🐛 - Bug Fix
- 📝 - Documentation
- 🚀 - Deployment
- ⚡ - Performance
- 🔒 - Security
- 🎨 - Design/UI
- 🧪 - Testing

---

### `displayName` (string)
**Alternative display name**

- Can include emojis or special formatting
- Used instead of `name` if provided

**Example:**
```json
"displayName": "📋 Template Workflow"
```

---

### `license` (string)
**License type**

- Indicates how the workflow can be used
- Use standard SPDX license identifiers

**Examples:**
```json
"license": "MIT"
"license": "Apache-2.0"
"license": "GPL-3.0"
"license": "Proprietary"
```

---

### `dependencies` (object or array)
**Required tools, libraries, or workflows**

**Object format (version constraints):**
```json
"dependencies": {
  "git": ">=2.0.0",
  "node": ">=18.0.0",
  "python": ">=3.9"
}
```

**Array format (simple list):**
```json
"dependencies": ["git", "docker", "kubectl"]
```

---

### `environment` (object)
**Environment variables or configuration values**

- Default values for environment variables
- Configuration used by workflow scripts

**Example:**
```json
"environment": {
  "ARTIFACTS_DIR": "artifacts",
  "DEFAULT_BRANCH": "main",
  "LOG_LEVEL": "info",
  "MAX_RETRIES": "3"
}
```

---

### `hooks` (object)
**Lifecycle hooks**

- Scripts executed at specific workflow points
- Each value is a path to a script

**Available hooks:**
- `pre-init` - Before initialization
- `post-init` - After initialization
- `pre-execute` - Before execution
- `post-execute` - After execution
- `on-error` - On error/failure

**Example:**
```json
"hooks": {
  "pre-init": "./scripts/hooks/pre-init.sh",
  "post-init": "./scripts/hooks/post-init.sh",
  "pre-execute": "./scripts/hooks/validate.sh",
  "post-execute": "./scripts/hooks/cleanup.sh",
  "on-error": "./scripts/hooks/on-error.sh"
}
```

---

### `settings` (object)
**Workflow-specific settings**

- Custom configuration for your workflow
- Can include any workflow-specific options

**Example:**
```json
"settings": {
  "autoSave": true,
  "verboseLogging": false,
  "createBackups": true,
  "templateDirectory": "./templates",
  "scriptDirectory": "./scripts",
  "maxConcurrentTasks": 5,
  "timeoutMinutes": 30
}
```

---

### `metadata` (object)
**Arbitrary metadata**

- Custom data for tracking or analytics
- Freeform structure

**Example:**
```json
"metadata": {
  "created": "2025-01-15",
  "lastUpdated": "2025-11-13",
  "category": "development",
  "maturity": "stable",
  "estimatedDuration": "30-60 minutes",
  "complexity": "intermediate",
  "maintainer": "Platform Team"
}
```

**Common metadata fields:**
- `created` - Creation date
- `lastUpdated` - Last update date
- `category` - Workflow category
- `maturity` - Stability level (experimental, beta, stable)
- `estimatedDuration` - Time estimate
- `complexity` - Difficulty level (beginner, intermediate, advanced)
- `maintainer` - Who maintains the workflow

---

## Complete Example

```json
{
  "name": "Feature Development Workflow",
  "description": "End-to-end workflow for planning, implementing, and deploying new features with comprehensive testing and documentation.",
  "version": "2.1.0",
  "icon": "🚀",
  "displayName": "🚀 Feature Development",

  "systemPrompt": "You are a feature development assistant specializing in spec-driven development. Follow these phases: 1) Specify requirements, 2) Design solution, 3) Implement with tests, 4) Review and deploy. Use /specify, /design, /implement, /review, /deploy commands. Create artifacts in artifacts/ directory.",

  "startupPrompt": "Welcome to Feature Development Workflow! I'll guide you through:\n1. Requirements specification\n2. Solution design\n3. Implementation with tests\n4. Code review\n5. Deployment\n\nRun /specify [feature-description] to begin.",

  "results": {
    "Requirements": "artifacts/specs/**/*.md",
    "Design Docs": "artifacts/design/**/*.md",
    "Implementation": "artifacts/implementation/**/*",
    "Tests": "artifacts/tests/**/*.test.ts",
    "Documentation": "artifacts/docs/**/*.md"
  },

  "author": {
    "name": "Platform Engineering Team",
    "email": "platform@company.com",
    "organization": "ACME Corp"
  },

  "repository": {
    "type": "git",
    "url": "https://github.com/acme/feature-workflow",
    "branch": "main"
  },

  "tags": [
    "feature-development",
    "planning",
    "implementation",
    "testing",
    "deployment"
  ],

  "license": "MIT",

  "dependencies": {
    "git": ">=2.0.0",
    "node": ">=18.0.0"
  },

  "environment": {
    "ARTIFACTS_DIR": "artifacts",
    "LOG_LEVEL": "info",
    "DEFAULT_BRANCH": "main"
  },

  "hooks": {
    "post-init": "./scripts/setup-workspace.sh",
    "pre-execute": "./scripts/validate-plan.sh",
    "post-execute": "./scripts/run-tests.sh"
  },

  "settings": {
    "autoSave": true,
    "verboseLogging": false,
    "createBackups": true
  },

  "metadata": {
    "created": "2024-06-15",
    "lastUpdated": "2025-11-13",
    "category": "development",
    "maturity": "stable",
    "estimatedDuration": "2-4 hours",
    "complexity": "intermediate"
  }
}
```

---

## Field Usage Patterns

### Minimal Configuration
Just the essentials:
```json
{
  "name": "My Workflow",
  "description": "What it does",
  "systemPrompt": "You are...",
  "startupPrompt": "Welcome..."
}
```

### Standard Configuration
Most common fields:
```json
{
  "name": "My Workflow",
  "description": "What it does",
  "systemPrompt": "You are...",
  "startupPrompt": "Welcome...",
  "results": {
    "Output": "artifacts/**/*.md"
  }
}
```

### Full Configuration
All available fields:
```json
{
  "name": "...",
  "description": "...",
  "version": "1.0.0",
  "icon": "🔧",
  "displayName": "...",
  "systemPrompt": "...",
  "startupPrompt": "...",
  "results": {...},
  "author": {...},
  "repository": {...},
  "tags": [...],
  "license": "MIT",
  "dependencies": {...},
  "environment": {...},
  "hooks": {...},
  "settings": {...},
  "metadata": {...}
}
```

---

## Validation Checklist

Before deploying your `ambient.json`:

- [ ] All required fields present (`name`, `description`, `systemPrompt`, `startupPrompt`)
- [ ] Valid JSON syntax (no trailing commas, proper quotes)
- [ ] No comment lines (if using standard JSON parser)
- [ ] Prompts are clear and actionable
- [ ] Results paths use proper glob patterns
- [ ] Version follows semver if specified
- [ ] All file paths referenced actually exist
- [ ] Environment variables make sense
- [ ] Hook scripts are executable and exist
- [ ] Tested in actual ACP session

---

## Common Mistakes

### ❌ Comments in JSON
```json
{
  // This will cause parsing errors
  "name": "My Workflow"
}
```

### ✅ Use JSON5 or remove comments
```json
{
  "name": "My Workflow"
}
```

---

### ❌ Trailing commas
```json
{
  "name": "My Workflow",
  "description": "...",  ← Remove this comma
}
```

### ✅ No trailing comma
```json
{
  "name": "My Workflow",
  "description": "..."
}
```

---

### ❌ Unclear prompts
```json
{
  "systemPrompt": "You help with stuff"
}
```

### ✅ Clear and specific
```json
{
  "systemPrompt": "You are a code review assistant. Analyze code for quality, security, and best practices. Use /review command. Output to artifacts/reviews/"
}
```

---

## Tips

1. **Start minimal**: Begin with required fields, add optional ones as needed
2. **Test iteratively**: Validate changes in real sessions
3. **Document prompts well**: Clear prompts = better agent behavior
4. **Use glob patterns wisely**: Make results easy to find
5. **Version your workflows**: Track changes with semantic versioning
6. **Keep metadata updated**: Helps with maintenance and discovery
