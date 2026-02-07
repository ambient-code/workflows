# CLAUDE.md Generator

Guided interview to create a concise, high-signal CLAUDE.md file for your project or personal workspace.

## Core Principle

**CLAUDE.md is onboarding, not configuration.** It should answer: What is this project? How does it work? How do I build/test/verify it?

Keep it under 300 lines. Ideally under 60.

## What It Creates

A focused CLAUDE.md covering:
- **WHAT**: Tech stack, project structure, key components
- **WHY**: Project purpose and goals
- **HOW**: Build, test, and verification commands
- **WHERE**: File:line pointers to authoritative sources (not code copies)

Plus optional:
- BOOKMARKS.md for progressive disclosure of references

## Interview Flow

### For Projects (Repos)
1. Project purpose and tech stack (3-4 questions)
2. File structure and key components (2-3 questions)
3. Essential commands (build, test, lint) (2-3 questions)
4. Progressive disclosure setup (BOOKMARKS.md) (1 question)

### For Personal Use
1. Your role and focus area (2 questions)
2. Communication preferences (2-3 questions)
3. Active projects/repos (1-2 questions)
4. Progressive disclosure setup (BOOKMARKS.md) (1 question)

**Time: 5-7 minutes**

## Best Practices Built-In

✅ **Minimal and focused** - Only universally applicable info
✅ **Pointers over copies** - Use `file:line` references
✅ **Progressive disclosure** - BOOKMARKS.md for task-specific docs
✅ **No linter rules** - Assumes you have pre-commit hooks/CI
✅ **Onboarding focus** - WHAT/WHY/HOW, not personal preferences

## Using BOOKMARKS.md

For project CLAUDE.md files, we'll set up BOOKMARKS.md with a TOC and metadata about who added each bookmark:

```markdown
# Bookmarks

## Table of Contents
- [Architecture](#architecture)
- [Development](#development)

---

## Architecture

### [API Design Guide](https://company.example.com/api-guide)

REST API conventions, authentication patterns, and versioning strategy.

**Added by**: @jane | **Date**: 2024-12-15 | **Note**: Essential for new endpoint work

### [Architecture Decision Records](docs/adr/README.md)

Historical context for major architectural choices.

**Added by**: @bob | **Date**: 2025-01-03

## Development

### [Release Process](docs/release.md)

Step-by-step guide for cutting releases and managing changelog.

**Added by**: @jane | **Date**: 2024-11-20 | **Note**: Updated with new signing process
```

Your CLAUDE.md will reference it, letting Claude load relevant context on-demand based on the task at hand.

## Example Output (Project)

```markdown
# MyProject

Web application for team collaboration built with Next.js, TypeScript, and PostgreSQL.

## Structure
- `src/app/` - Next.js App Router pages
- `src/components/` - React components
- `src/lib/` - Shared utilities
- `prisma/` - Database schema and migrations

## Key Files
- Database models: `prisma/schema.prisma`
- API routes: `src/app/api/`
- Auth logic: `src/lib/auth.ts:45-120`

## Commands
```bash
npm install          # Install dependencies
npm run dev          # Start dev server (http://localhost:3000)
npm run build        # Production build
npm test             # Run tests
npm run lint         # Check code style
```

## More Info
See [BOOKMARKS.md](BOOKMARKS.md) for design docs, release process, and testing guides.
```

**60 lines. High signal, zero noise.**

## Example Output (Personal)

```markdown
# Claude Config - Jane Doe

Senior Platform Engineer focused on Kubernetes infrastructure and developer experience.

## Active Projects
- [kubernetes/kubernetes](https://github.com/kubernetes/kubernetes)
- [company/internal-platform](https://github.com/company/platform)

## Communication
- Prefer concise technical explanations with code examples
- Include file:line references for implementation details
- Flag breaking changes and deprecations explicitly

## References
See [BOOKMARKS.md](BOOKMARKS.md) for Kubernetes docs, internal wikis, and design patterns.
```

**14 lines. Just the essentials.**

## After Generation

1. **Download immediately** - Files session-only, not saved
2. **Place CLAUDE.md** in repo root or `~/Documents/Claude/`
3. **Add to git** - Commit it with your code
4. **Keep updated** - Edit directly as project evolves
5. **Measure quality** - Try [Terminal-Bench](https://github.com/laude-institute/terminal-bench) to benchmark

## What This Workflow Avoids

❌ Personal preference overload
❌ Linter rules in markdown (use pre-commit hooks)
❌ Code snippets (use file:line pointers)
❌ Task-specific instructions (use BOOKMARKS.md)
❌ Auto-generated boilerplate

## Who This Is For

- **Project maintainers** - Create CLAUDE.md for your repos
- **Individual devs** - Personal config for cross-project work
- **Teams** - Standardize onboarding docs across projects
