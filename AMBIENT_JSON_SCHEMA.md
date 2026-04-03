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
2. **Workspace navigation**: Standard file locations and tool selection rules
3. **Workflow entry point**: Point to the skill(s) that contain the methodology (e.g., "Read and execute `.claude/skills/my-skill/SKILL.md`")
4. **Output locations**: Where to write artifacts (e.g., `artifacts/my-workflow/`)
5. **Error handling**: How to handle failures

**Note**: Keep the systemPrompt focused on role, navigation, and entry points. Move detailed methodology into `.claude/skills/` files. This keeps the ambient.json readable and makes the methodology easier to maintain. The agent already knows how to use tools, read files, and follow instructions — the systemPrompt just needs to tell it *what* to do and *where* things are.

**Example**:

```json
"systemPrompt": "You are a Sprint Health Analyst.\n\nStandard file locations:\n- Skill: .claude/skills/sprint-report/SKILL.md\n- Template: templates/report.html\n- Outputs: artifacts/sprint-report/\n\nOnce the user provides context, read and execute the sprint-report skill."
```

---

### `startupPrompt` (string, required)

**Purpose**: Sent to the agent as a hidden user message at session start. The user never sees this text -- they only see the agent's response. Write it as a directive telling the agent how to begin the session, not as a canned greeting.

**Guidelines**:

- Write as an instruction to the agent (e.g., "Greet the user and introduce yourself as...")
- Tell the agent what information to include in its greeting
- Keep it concise -- 1-3 sentences directing the agent's behavior
- Do NOT write it as a greeting the user would see directly

**Examples**:

```json
"startupPrompt": "Greet the user as a Sprint Health Analyst. Ask for their data source, team name, sprint details, audience, and preferred output format."

"startupPrompt": "Introduce yourself as a bug fix assistant. Ask the user to describe the bug or provide an issue URL."

"startupPrompt": "Greet the user and explain that you help collect user feedback through structured interviews. Ask what product area they want to cover."
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

### How the Platform Uses ambient.json

1. **System prompt injection**: `systemPrompt` is appended to the workspace context prompt
2. **Startup directive**: `startupPrompt` is sent to the agent as a hidden user message at session start
3. **Workflow metadata API**: `name`, `description`, and other fields are returned via the `/content/workflow-metadata` endpoint

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
  "name": "Sprint Health Report",
  "description": "Generates sprint health reports from Jira data with risk ratings, anti-pattern detection, and coaching recommendations.",
  "systemPrompt": "You are a Sprint Health Analyst...\n\nWORKSPACE NAVIGATION:\n- Skill: .claude/skills/sprint-report/SKILL.md\n- Template: templates/report.html\n- Outputs: artifacts/sprint-report/\n\nWORKFLOW:\nOnce the user answers the startup questions, read and execute the sprint-report skill.",
  "startupPrompt": "Greet the user as a Sprint Health Analyst. Ask the intake questions: data source, team/sprint name, audience, output format, and whether they have historical data for comparison. List the default assumptions and ask the user to confirm or correct them.",
  "results": {
    "Health Reports (Markdown)": "artifacts/sprint-report/**/*.md",
    "Health Reports (HTML)": "artifacts/sprint-report/**/*.html"
  }
}
```

---

## Best Practices

### System Prompt Design

1. **Be specific about role**: Define exact persona and expertise
2. **Add workspace navigation guidance**: Standard file locations and tool selection rules (see [WORKSPACE_NAVIGATION_GUIDELINES.md](WORKSPACE_NAVIGATION_GUIDELINES.md))
3. **Point to skills**: For complex workflows, reference the skill file(s) that contain the methodology
4. **Specify output locations**: Where artifacts are written (e.g., `artifacts/my-workflow/`)
5. **Add error handling**: How to recover from failures
6. **Use markdown formatting**: Headers, lists, code blocks for readability
7. **Keep it focused**: Delegate detailed methodology to skills rather than cramming everything into the systemPrompt

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
├── .claude/
│   └── skills/               ← Skill definitions (preferred)
│       └── my-skill/
│           └── SKILL.md
├── templates/                ← Optional templates
├── README.md
└── scripts/                  ← Optional helper scripts
```

At runtime, artifacts are written relative to the workspace root, not inside
the workflow directory:

```text
/workspace/sessions/{session}/
├── workflows/my-workflow/    ← Workflow files loaded here
└── artifacts/my-workflow/    ← Output goes here (sibling, not nested)
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
  // Too generic - needs role, file locations, entry point
}
```

### ✅ Correct Structure

```json
{
  "name": "My Workflow",
  "description": "Detailed description of purpose",
  "systemPrompt": "You are [role].\n\nFile locations:\n- Skill: .claude/skills/my-skill/SKILL.md\n- Outputs: artifacts/my-workflow/\n\nRead and execute the skill when the user provides context.",
  "startupPrompt": "Greet the user, briefly describe your purpose, and ask what they need help with.",
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

**Example Workflows** (in this repository):

- `workflows/bugfix/.ambient/ambient.json` — skill-based, multi-phase workflow
- `workflows/sprint-report/.ambient/ambient.json` — skill-based, 1–2 turn workflow
- `workflows/triage/.ambient/ambient.json` — command-based triage workflow
- `workflows/template-workflow/.ambient/ambient.json` — minimal starter template

**Documentation**:

- Workflow development guide: [WORKFLOW_DEVELOPMENT_GUIDE.md](WORKFLOW_DEVELOPMENT_GUIDE.md)
- Agent guidelines: [AGENTS.md](AGENTS.md)

---

## Summary

The `ambient.json` schema has 4 required fields and 1 optional field, keeping the format lightweight and portable. For simple workflows, the `systemPrompt` can contain the full methodology inline. For complex workflows, keep the `systemPrompt` focused on role and navigation, and move detailed methodology into `.claude/skills/` files that the agent reads on demand.

**Minimum viable ambient.json**: 4 required string fields (`name`, `description`, `systemPrompt`, `startupPrompt`)
**Optional**: `results` for documenting artifact locations (informational only)

The platform is lenient -- missing optional fields default gracefully, and extra fields are ignored.
