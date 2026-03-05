# Doc Checker

Documentation completeness review of pull requests -- determines whether a PR
includes all necessary documentation updates when code changes affect
user-facing behavior.

## Overview

Doc Checker is a focused, single-purpose workflow. Given a pull request, it
analyzes whether code changes with user-facing impact have corresponding
documentation updates. It does NOT review code quality, style, performance,
security, testing, or architecture.

## Usage

1. Load the workflow in an ACP session
2. Provide a pull request (URL, number, or diff)
3. Run `/review-pr`

The review follows a five-phase process:

| Phase | What happens |
|-------|-------------|
| 1. Gather Context | Examine PR metadata, build file inventory, identify doc ecosystem |
| 2. Classify Changes | Categorize each change by user-facing impact |
| 3. Discover Docs | Search the repo for existing documentation of affected behavior |
| 4. Evaluate Coverage | Determine if PR includes necessary doc updates |
| 5. Render Verdict | PASS, PASS WITH SUGGESTIONS, or FAIL with findings |

## Verdicts

- **PASS** -- All changes are internal or documentation updates are sufficient
- **PASS WITH SUGGESTIONS** -- Only minor documentation gaps found
- **FAIL** -- At least one critical or major documentation gap

## Finding Severities

- **CRITICAL** -- Incorrect information or missing essential knowledge (e.g., breaking change without migration path)
- **MAJOR** -- Materially incomplete docs for a meaningful use case (e.g., new feature undocumented)
- **MINOR** -- Edge case or advanced usage gap unlikely to surprise users

## Documentation In Scope

- README and related files (CONTRIBUTING.md, GETTING_STARTED.md)
- API reference (OpenAPI/Swagger, inline API doc comments)
- CLI help text (--help output, man pages, command reference)
- Configuration guides (schemas, env var docs, .env examples)
- Tutorials, guides, and how-to documents
- Inline user-facing help (UI strings, error messages, tooltips)
- Architecture/design docs describing user-facing behavior
- Schema files serving as documentation (JSON Schema, GraphQL)

## Out of Scope

- CHANGELOG, release notes, commit messages
- Internal code comments not rendered to users
- Internal design documents
- Test descriptions
- License files

## Workflow Structure

```
workflows/doc-checker/
├── .ambient/
│   └── ambient.json              # Workflow configuration
├── .claude/
│   ├── commands/
│   │   └── review-pr.md          # /review-pr command
│   └── skills/
│       └── review-pr/
│           └── SKILL.md          # Full review methodology
├── CLAUDE.md                     # Behavioral guidelines
└── README.md                     # This file
```
