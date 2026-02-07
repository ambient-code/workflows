# Writing a Good CLAUDE.md

Also applicable to `AGENTS.md` for OpenCode, Zed, Cursor, and Codex.

## Core Principle

LLMs are stateless. Claude knows nothing about your codebase at the start of each session. `CLAUDE.md` is the only file that goes into every single conversation, making it the highest-leverage file in your repo. Every bad line in it multiplies across every task.

## Best Practices

1. **Onboard, don't configure.** Cover WHAT (tech stack, project structure, what each part does), WHY (purpose of the project), HOW (commands to build, test, verify).

2. **Less is more.** Keep your file under 300 lines. Ideally under 60.

3. **Only universally applicable instructions.** If it doesn't matter for every single task, it doesn't belong here.

4. **Progressive disclosure.** Use BOOKMARKS.md for a token-optimized approach to progressive disclosure. Put task-specific docs in separate files (for example, `docs/release.md`). List BOOKMARKS.md and a fragment about it in your CLAUDE.md. This lets Claude decide which files are most relevant to the task.

5. **Prefer pointers to copies.** Don't paste code snippets into docs. They go stale. Use `file:line` references to point Claude at the authoritative source.

6. **Don't use it as a linter.** Use linters with auto-fix. LLMs are in-context learners and will follow patterns they see in your codebase. Ensure you have pre-commit hooks and CI checks that enforce your coding style, rather than trying to explain it all in CLAUDE.md. Claude will make mistakes no matter what you put in CLAUDE.md. Keep those mistakes from polluting your codebase with a strong CI pipeline and code review process, not with a long style guide in CLAUDE.md.

7. **Don't auto-generate it.** Skip `/init` and follow this guide. Think carefully about every line. Develop a method of measuring your changes. Try [Terminal-Bench](https://github.com/laude-institute/terminal-bench).

8. **Claude may ignore it.** Claude Code wraps your file with a system reminder that says "this context may or may not be relevant."

## Bookmarks: `/bookmark` for Managed Context Links

Leverage the `/bookmark` skill to manage reference links in a controlled way that can be committed with the code. This prevents bloating CLAUDE.md with things that aren't universally relevant to your codebase.

When you find a useful doc, API reference, or design decision, run `/bookmark <url> <description>` and it gets added to the list. CLAUDE.md knows about BOOKMARKS.md, and the team gets a shared, version-controlled collection of links that stays current through normal PR workflow.

## Example: Minimal Project CLAUDE.md

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

## Example: Minimal Personal CLAUDE.md

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

## Enriched BOOKMARKS.md

Make BOOKMARKS.md easy for Claude to navigate with:

1. **Table of Contents** - Quick jump links to sections
2. **Descriptions** - What's in the doc, not just a title
3. **Metadata** - Who added it, when, and why (optional comment)

**Example**:
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
```

This structure helps Claude:
- Scan the TOC to find relevant sections quickly
- Understand what's in a doc before loading it
- See who on the team added it (helpful for questions)
- Track when information was added (freshness indicator)

## What to Avoid

❌ Personal communication preferences and long mission statements
❌ Linter rules (use pre-commit hooks and CI instead)
❌ Code snippets that will go stale
❌ Task-specific instructions (use BOOKMARKS.md)
❌ Auto-generated boilerplate
❌ Anything that doesn't matter for every task

## Measuring Quality

Use these tools to measure and improve your CLAUDE.md:

- **[Terminal-Bench](https://github.com/laude-institute/terminal-bench)** - Benchmark for testing AI agents in real terminal environments

## Remember

**Every line in CLAUDE.md multiplies across every conversation.** Make each one count.
