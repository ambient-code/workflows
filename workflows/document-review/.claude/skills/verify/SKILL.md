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
  If `artifacts/inventory.md` does not exist, inform the user
  and recommend running `/scan` first.
- **Read, don't run.** This is static analysis. You read source code to verify
  claims — you don't execute it.
- **Be precise.** Cite the exact documentation claim and the exact code that
  confirms or contradicts it. Every finding must include both: a direct
  quote from the documentation and an actual code snippet (not a summary of
  what the code does). Use fenced code blocks with language tags.
- **Flag undocumented features.** If you discover functionality in code that
  has no documentation, report it as a High finding. When checking a code
  area (e.g., a struct or route group), scan *all* fields/routes — not just
  the ones the documentation mentions. The goal is to catch fields, flags,
  endpoints, or behaviors that exist in code but are missing from docs.

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

Read the inventory (`artifacts/inventory.md`).

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
   - **Mismatch**: Doc contradicts code → severity: **Critical**
   - **Partial**: Doc is incomplete or imprecise → severity: **Low**
   - **Undocumented**: Code has features not in docs → severity: **High**

### Step 5: Record Findings

Follow the template at `templates/findings-verify.md` exactly. Write findings to
`artifacts/findings-verify.md`.

Each verification finding should include:

- **Dimension**: Accuracy or Completeness
- **File**: Documentation file path and line in backticks (e.g., `README.md:85`)
- **Code location**: Source file and line
- **Documented claim**: What the docs say
- **Actual behavior**: What the code does
- **Evidence**: Relevant code snippet

## Output

- `artifacts/findings-verify.md`
