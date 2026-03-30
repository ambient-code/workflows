# Complete ambient.json Schema

**Source**: ambient-code/platform repository analysis
**Date**: 2026-03-29

## Overview

The `ambient.json` file is the configuration file for Ambient Code Platform workflows. It must be located at `.ambient/ambient.json` in the workflow directory root.

## Complete Schema

```typescript
interface AmbientConfig {
  name: string;              // Required
  description: string;       // Required
  systemPrompt: string;      // Required
  startupPrompt: string;     // Required
  results?: {                // Optional (informational only -- not read by platform)
    [artifactName: string]: string;  // Glob pattern for artifact location
  };
}
```

## Field Specifications

### `name` (string, required)

**Purpose**: Workflow display name shown in UI and CLI

**Guidelines**:

- Short and descriptive (2-5 words)
- Used in greeting messages and workflow selection
- Title case or kebab-case

**Examples**:

```json
"name": "Specsmith Workflow"
"name": "specsmith-workflow"
"name": "Fix a bug"
"name": "Triage Backlog"
```

---

### `description` (string, required)

**Purpose**: Brief explanation of what the workflow does

**Guidelines**:

- 1-3 sentences
- Appears in workflow selector UI
- Focus on value proposition and use cases

**Examples**:

```json
"description": "Transform feature ideas into implementation-ready plans through structured interviews with multi-agent collaboration"

"description": "Streamlined workflow for bug triage, root cause analysis, and fix implementation with automated testing"

"description": "Collect user feedback through structured interviews with configurable destination (Jira/GitHub)"
```

---

### `systemPrompt` (string, required)

**Purpose**: Core instructions defining the agent's behavior when workflow is active

**Guidelines**:

- Can be extensive (thousands of characters)
- Loaded into Claude's context at workflow activation
- Defines the agent's personality, capabilities, and methodology
- Supports full markdown formatting

**Should Include**:

1. **Role definition**: "You are a [role]..."
2. **Available slash commands**: `/command` with descriptions
3. **Workflow phases**: Step-by-step methodology
4. **Output locations**: Where to write artifacts (e.g., `artifacts/specsmith/`)
5. **Agent orchestration**: Which specialized agents to invoke and when
6. **API integrations**: Instructions for Jira/GitHub/etc.
7. **Best practices**: Conventions and quality standards
8. **Error handling**: How to handle failures

**Example Structure**:

```json
"systemPrompt": "You are Specsmith, a spec-driven development assistant.

## Available Commands

- `/spec.interview` - Start interactive feature interview
- `/spec.speedrun` - Quick planning mode
- `/validate` - Validate implementation plan

## Workflow Phases

### Phase 1: Interview
Conduct structured interview with user...

### Phase 2: Planning
Generate implementation plan...

## Specialized Agents

Invoke these agents as needed:
- **Quinn (Architect)**: System design and architecture
- **Maya (Engineer)**: Implementation details
- **Alex (QA)**: Testing strategy

## Output Structure

All artifacts go in `artifacts/specsmith/`:
- `interview-notes.md` - Interview Q&A
- `PLAN.md` - Implementation plan
- `validation-report.md` - Validation results

## Best Practices

1. Always validate user requirements
2. Consider edge cases early
3. Generate testable acceptance criteria
..."
```

**Real-World Example** (from Specsmith):

- 5 workflow phases defined
- 5 specialized agent personas (Quinn, Maya, Alex, Casey, Dana)
- Multiple slash commands
- Detailed artifact structure
- ~3000+ characters

---

### `startupPrompt` (string, required)

**Purpose**: Sent to the agent as a hidden user message at session start. The user never sees this text -- they only see the agent's response. Write it as a directive telling the agent how to begin the session, not as a canned greeting.

**Guidelines**:

- Write as an instruction to the agent (e.g., "Greet the user and introduce yourself as...")
- Tell the agent what information to include in its greeting (available commands, purpose, etc.)
- Keep it concise -- 1-3 sentences directing the agent's behavior
- Do NOT write it as a greeting the user would see directly

**Examples**:

```json
"startupPrompt": "Greet the user and introduce yourself as a spec-driven development assistant. Mention the available commands (/spec.interview, /spec.speedrun, /validate) and suggest starting with /spec.interview."

"startupPrompt": "Introduce yourself as a bug fix assistant. Briefly explain that you help triage, analyze, and fix bugs systematically. Mention the /fix command and ask the user to describe their bug."

"startupPrompt": "Greet the user and explain that you help collect user feedback through structured interviews. Mention Jira and GitHub integration and suggest using /interview to start."
```

---

### `results` (object, optional)

**Purpose**: Map artifact names to output file paths/patterns for documentation purposes

**Note**: This field is **not read by the platform**. It serves as human-readable documentation of what a workflow produces and where. The platform discovers artifacts via the hardcoded `artifacts/` directory.

**Guidelines**:

- Purely informational -- not used by the platform at runtime
- Useful as documentation for workflow authors and users
- Uses glob patterns for multiple files
- Keys are human-readable artifact names
- Values are paths relative to workspace root

**Structure**:

```json
"results": {
  "Artifact Display Name": "path/to/files/**/*.extension",
  "Another Artifact": "path/to/specific-file.md"
}
```

**Examples**:

```json
"results": {
  "Interview Notes": "artifacts/specsmith/interview-notes.md",
  "Implementation Plan": "artifacts/specsmith/PLAN.md",
  "Validation Report": "artifacts/specsmith/validation-report.md",
  "Speedrun Summary": "artifacts/specsmith/speedrun-summary.md",
  "All Artifacts": "artifacts/specsmith/**/*"
}
```

```json
"results": {
  "Bug Analysis": "artifacts/bugfix/**/analysis.md",
  "Fix Implementation": "artifacts/bugfix/**/implementation.md",
  "Test Results": "artifacts/bugfix/**/test-results.xml",
  "Root Cause": "artifacts/bugfix/**/root-cause.md"
}
```

---

## Platform Integration

### File Location

```text
workflow-repository/
├── .ambient/
│   └── ambient.json          ← Must be here
├── README.md
└── [other workflow files]
```

### Loading Code

The platform loads ambient.json at startup:

**File**: `platform/components/runners/ambient-runner/ambient_runner/platform/config.py`

```python
def load_ambient_config(cwd_path: str) -> dict:
    """Load ambient.json configuration from workflow directory."""
    config_path = Path(cwd_path) / ".ambient" / "ambient.json"
    if not config_path.exists():
        return {}
    with open(config_path, 'r') as f:
        config = json.load(f)
        logger.info(f"Loaded ambient.json: name={config.get('name')}")
        return config
```

### Usage

1. **System prompt injection** (`prompts.py`): `systemPrompt` is appended to the workspace context prompt
2. **Startup directive** (`app.py`): `startupPrompt` sent to agent as hidden user message at session start
3. **Workflow metadata API** (`content.py`): `name`, `description`, and other fields returned via `/content/workflow-metadata` endpoint

---

## Validation Rules

**Required Fields**:

- ✅ `name` must be present
- ✅ `description` must be present
- ✅ `systemPrompt` must be present
- ✅ `startupPrompt` must be present

**Optional Fields**:

- `results` can be omitted (informational only -- not read by the platform)

**No Strict Validation**:

- Platform is lenient with missing fields
- Extra fields are ignored
- No field length limits enforced
- JSON syntax must be valid

---

## Real-World Examples

### Minimal Example

```json
{
  "name": "Simple Workflow",
  "description": "A minimal workflow configuration",
  "systemPrompt": "You are a helpful assistant. Help users with their tasks.",
  "startupPrompt": "Greet the user and ask how you can help them today."
}
```

### Standard Example

```json
{
  "name": "Feature Planning Workflow",
  "description": "Plan features through structured interviews and generate implementation specs",
  "systemPrompt": "You are a feature planning assistant.\n\n## Commands\n- /interview - Start interview\n- /plan - Generate plan\n\n## Output\nWrite all artifacts to artifacts/planning/",
  "startupPrompt": "Greet the user and introduce yourself as a feature planning assistant. Mention the /interview and /plan commands and suggest starting with /interview.",
  "results": {
    "Interview Notes": "artifacts/planning/interview.md",
    "Implementation Plan": "artifacts/planning/plan.md"
  }
}
```

### Comprehensive Example (Specsmith-style)

```json
{
  "name": "Specsmith Workflow",
  "description": "Transform feature ideas into implementation-ready plans through structured interviews with multi-agent collaboration",
  "systemPrompt": "You are Specsmith, a spec-driven development assistant...\n\n[Extensive system prompt with phases, agents, commands, output structure]\n\n## Phase 1: Interview\n...\n\n## Specialized Agents\n- Quinn (Architect)\n- Maya (Engineer)\n- Alex (QA)\n...",
  "startupPrompt": "Greet the user as Specsmith. Explain that you transform feature ideas into implementation-ready plans. List the commands: /spec.interview, /spec.speedrun, /validate. Suggest starting with /spec.interview.",
  "results": {
    "Interview Notes": "artifacts/specsmith/interview-notes.md",
    "Implementation Plan": "artifacts/specsmith/PLAN.md",
    "Validation Report": "artifacts/specsmith/validation-report.md",
    "Speedrun Summary": "artifacts/specsmith/speedrun-summary.md",
    "All Artifacts": "artifacts/specsmith/**/*"
  }
}
```

---

## Best Practices

### System Prompt Design

1. **Be specific about role**: Define exact persona and expertise
2. **Document all commands**: List every `/command` with purpose
3. **Define workflow phases**: Clear step-by-step methodology
4. **Specify output locations**: Absolute paths for artifacts
5. **Include agent orchestration**: When to invoke specialized agents
6. **Add error handling**: How to recover from failures
7. **Use markdown formatting**: Headers, lists, code blocks for readability
8. **Add workspace navigation guidance**: Help Claude find files efficiently (see [WORKSPACE_NAVIGATION_GUIDELINES.md](WORKSPACE_NAVIGATION_GUIDELINES.md))

### Startup Prompt Design

1. **Write as a directive**: Tell the agent what to do, not what to say verbatim
2. **Specify content**: What information should the agent include in its greeting
3. **Keep it brief**: 1-3 sentences directing the agent's behavior

### Results Configuration

1. **Use glob patterns**: `**/*.md` for multiple files
2. **Organize by type**: Group related artifacts
3. **Include "All Artifacts"**: Catch-all pattern for discovery
4. **Use descriptive names**: "Implementation Plan" not "plan.md"

### File Organization

```text
workflow-repo/
├── .ambient/
│   └── ambient.json          ← Configuration here
├── artifacts/                ← Output location (in systemPrompt)
│   └── workflow-name/
│       ├── interview.md
│       └── plan.md
├── README.md
└── scripts/                  ← Optional helper scripts
```

---

## Common Mistakes

### ❌ Missing Required Fields

```json
{
  "name": "My Workflow"
  // Missing description, systemPrompt, startupPrompt
}
```

### ❌ Invalid JSON Syntax

```json
{
  "name": "My Workflow",
  "description": "...",  ← Trailing comma causes error
}
```

### ❌ Vague System Prompt

```json
{
  "systemPrompt": "You help with development"
  // Too generic - needs phases, commands, outputs
}
```

### ✅ Correct Structure

```json
{
  "name": "My Workflow",
  "description": "Detailed description of purpose",
  "systemPrompt": "You are [role].\n\n## Commands\n- /cmd\n\n## Phases\n1. Step one\n\n## Output\nartifacts/my-workflow/",
  "startupPrompt": "Greet the user, briefly describe your purpose, and suggest using /cmd to start.",
  "results": {
    "Output": "artifacts/my-workflow/**/*.md"
  }
}
```

---

## References

**Platform Code Locations**:

- Config loading: `platform/components/runners/ambient-runner/ambient_runner/platform/config.py`
- System prompt injection: `platform/components/runners/ambient-runner/ambient_runner/platform/prompts.py`
- Startup prompt execution: `platform/components/runners/ambient-runner/ambient_runner/app.py`
- Workflow metadata API: `platform/components/runners/ambient-runner/ambient_runner/endpoints/content.py`

**Example Workflows**:

- `/Users/jeder/repos/workflows/workflows/specsmith-workflow/.ambient/ambient.json`
- `/Users/jeder/repos/workflows/workflows/amber-interview/.ambient/ambient.json`
- `/Users/jeder/repos/workflows/workflows/template-workflow/.ambient/ambient.json`
- `/Users/jeder/repos/workflows/workflows/bugfix/.ambient/ambient.json`
- `/Users/jeder/repos/workflows/workflows/triage/.ambient/ambient.json`

**Documentation**:

- Field reference: `workflows/template-workflow/FIELD_REFERENCE.md`
- Platform docs: `github.com/ambient-code/platform`

---

## Summary

The `ambient.json` schema has 4 required fields and 1 optional field, keeping the format lightweight and portable. The `systemPrompt` field is where workflows become powerful -- a well-crafted systemPrompt can define complex multi-phase workflows with specialized agents, API integrations, and sophisticated output structures.

**Minimum viable ambient.json**: 4 required string fields (`name`, `description`, `systemPrompt`, `startupPrompt`)
**Optional**: `results` for documenting artifact locations (informational only)

The platform is lenient -- missing optional fields default gracefully, and extra fields are ignored.
