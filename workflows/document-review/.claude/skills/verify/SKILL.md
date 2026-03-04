---
name: verify
description: Cross-reference documentation claims against actual source code.
---

# Verify Documentation Skill

You are cross-referencing a project's documentation against its actual source
code to verify accuracy. This is a deeper accuracy check than the `/review`
phase, which only evaluates documentation in isolation.

## Your Role

Read documentation claims about code behavior, APIs, configuration, and CLI
usage, then check the source code to verify those claims are accurate. Report
discrepancies as findings and flag undocumented features.

## Critical Rules

- **Read the inventory first.** This phase requires `/scan` to have been run.
  If `artifacts/document-review/inventory.md` does not exist, inform the user
  and recommend running `/scan` first.
- **Read, don't run.** This is static analysis. You read source code to verify
  claims — you don't execute it. Use `/test` for runtime verification.
- **Be precise.** Cite the exact documentation claim and the exact code that
  confirms or contradicts it.
- **Flag undocumented features.** If you discover functionality in code that
  has no documentation, report it as a Gap finding.

## What to Verify

Focus on documentation claims that can be checked against source code:

### CLI Flags and Options

- Documented flags → check argument parsing code (argparse, cobra, clap, etc.)
- Default values → check where defaults are defined
- Flag descriptions → check if behavior matches

### API Endpoints and Methods

- Documented endpoints → check route definitions and handlers
- Request/response formats → check schemas, serialization code
- Authentication requirements → check middleware and guards

### Configuration Options

- Documented config keys → check config loading/parsing code
- Default values → check source code defaults
- Required vs optional → check validation logic
- Environment variables → check where they're read

### Installation and Dependencies

- Documented dependencies → check package.json, requirements.txt, go.mod, etc.
- Version requirements → check version constraints
- System requirements → check Dockerfiles, CI configs

### Behavior Descriptions

- Documented behavior → check implementation logic
- Error handling → check what errors are actually raised
- Supported formats/protocols → check what's implemented

## Process

### Step 1: Load Context

Read the inventory (`artifacts/document-review/inventory.md`) and existing
findings (`artifacts/document-review/findings.md`) if available.

### Step 2: Identify Verifiable Claims

Scan each document for claims that can be checked against code:

- Commands and their flags
- API endpoint definitions
- Configuration option listings
- Default value statements
- Supported feature lists
- Architecture descriptions

### Step 3: Locate Relevant Source Code

For each category of claims, find the corresponding source:

- CLI: Look for argument parsers, command definitions
- API: Look for route registrations, handler functions
- Config: Look for config structs, env var readers, defaults
- Features: Look for implementation code

Use Grep and Glob to find relevant source files efficiently.

### Step 4: Cross-Reference

For each verifiable claim:

1. Read the documentation claim
2. Find the corresponding source code
3. Compare: does the code match what the docs say?
4. Record the result:
   - **Match**: Doc accurately reflects code (no finding needed)
   - **Mismatch**: Doc contradicts code → severity: **Error**
   - **Partial**: Doc is incomplete or imprecise → severity: **Improvement**
   - **Undocumented**: Code has features not in docs → severity: **Gap**

### Step 5: Record Findings

Add findings to `artifacts/document-review/findings.md`. If the file exists
from a prior `/review`, append a new section. If not, create it.

Each verification finding should include:

- **Severity**: Error, Gap, or Improvement
- **Dimension**: Accuracy or Completeness
- **Documentation location**: File, section, and line
- **Code location**: Source file and line
- **Documented claim**: What the docs say
- **Actual behavior**: What the code does
- **Evidence**: Relevant code snippet

Format for appending to existing findings:

```markdown
## Code Verification Findings

**Verified:** [date]
**Source files checked:** N

### [path/to/document.md]

#### Verification Finding 1

- **Severity:** Error
- **Dimension:** Accuracy
- **Doc location:** README.md, "Configuration" section, line 85
- **Code location:** src/config.py:42
- **Documented claim:** "Set `MAX_RETRIES` to configure retry count (default: 3)"
- **Actual behavior:** Default is 5, not 3. See `DEFAULT_MAX_RETRIES = 5`
- **Evidence:**
  ```python
  DEFAULT_MAX_RETRIES = 5  # src/config.py:42
  ```

### Undocumented Features

#### Feature 1

- **Severity:** Gap
- **Dimension:** Completeness
- **Code location:** src/cli.py:120
- **Description:** The `--dry-run` flag exists in code but is not documented
- **Evidence:**
  ```python
  parser.add_argument('--dry-run', help='Preview changes without applying')
  ```
```

## Output

- Enriches `artifacts/document-review/findings.md` with code-verified findings

## When This Phase Is Done

Report your findings:

- Number of claims verified
- Number of mismatches found (Errors)
- Number of undocumented features found (Gaps)
- Key discrepancies between docs and code
- Whether executable instructions were found that could be tested with `/test`

Then **re-read the controller** (`.claude/skills/controller/SKILL.md`) for
next-step guidance.
