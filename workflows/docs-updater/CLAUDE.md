# Docs Updater Workflow

Keep documentation in sync with code changes through these phases:

1. **Review** — Discover which doc files need updates and preview changes
2. **Update** — Apply accepted changes to documentation files
3. **Open PR** — Submit a documentation pull request

The `/index` command is available separately for building semantic indexes.

All phases are implemented as skills. The controller skill manages phase
transitions and recommendations. Artifacts go in `artifacts/docs-updater/`.

## Principles

- **Targeted**: Only update docs that would become incorrect because of the code change
- **Format-aware**: Respect the existing format of each file without mixing syntax
- **Minimal changes**: Add only what the diff justifies. Do not restructure, rewrite, or "improve"
- **Show evidence**: When selecting a file, explain exactly what would become incorrect
- **When in doubt, do NOT update**: Prefer skipping a file over making an unnecessary change

## Hard Limits

- No creating new documentation files — only update existing ones
- No modifying code files — this workflow operates on docs only
- No writing content that is not directly justified by the diff
- No force-push or destructive git operations
- No logging tokens or secrets

## Safety

- Present file selections to the user before generating content
- Always use `AskUserQuestion` between phases — never auto-advance
- Flag uncertainty: if unsure whether a file needs updating, do NOT include it

## Working With Code and Docs Locations

- The code and docs may live in separate repos or in the same repo (e.g., a `docs/` subfolder)
- The code location is the source of the diff
- The docs location is the target of changes
- Keep track of which directory you are in at all times
- All git operations for the PR happen in the docs location
