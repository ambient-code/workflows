---
name: scan
description: Discover and catalog all documentation in the target project.
---

# Scan Documentation Skill

You are surveying a project to discover and catalog all documentation. This is
the first phase of the document review workflow. Your job is to find everything
that constitutes documentation and produce a structured inventory.

## Your Role

Discover all documentation files, classify them by type and audience, and
produce an inventory that subsequent phases will use as their input. This is
discovery only — do not evaluate quality yet.

## Critical Rules

- **Do not evaluate documentation quality.** This phase is discovery and
  cataloging only.
- **Be thorough.** Documentation lives in many places — don't just check
  `docs/`.
- **Respect scope.** If the user specified particular files or directories,
  limit the scan to those. Otherwise, scan everything.

## Process

### Step 1: Locate the Project

Check if the project repository is already accessible:

```bash
# Check common locations
ls /workspace/repos/ 2>/dev/null
ls /workspace/artifacts/ 2>/dev/null
```

- If the repo is already present (e.g., mounted via `add_dirs`), note its path
- If not and the user provided a URL, clone it:

```bash
gh repo clone OWNER/REPO /workspace/repos/REPO
```

- If neither, ask the user where the project is located

### Step 2: Discover Documentation Files

Search for documentation using multiple strategies:

**Standard documentation files (project root):**

- `README*` (README.md, README.rst, README.txt, etc.)
- `CONTRIBUTING*`
- `LICENSE*`, `NOTICE*`, `AUTHORS*`
- `SECURITY*`, `CODE_OF_CONDUCT*`
- `CLAUDE.md`, `AGENTS.md` (AI-specific docs)

**Documentation directories:**

- `docs/`, `doc/`, `documentation/`
- `wiki/`, `guides/`, `tutorials/`
- `examples/`, `samples/`
- `man/`, `manpages/`
- `api/`, `api-docs/`

**Formats to find:**

- Markdown (`.md`, `.mdx`)
- reStructuredText (`.rst`)
- Plain text (`.txt`)
- AsciiDoc (`.adoc`, `.asciidoc`)
- HTML documentation (`.html` in doc directories)

**Other documentation sources:**

- Inline API documentation (JSDoc, Javadoc, docstrings — note their presence
  but don't catalog every file)
- Configuration file comments (note if config files have substantial inline
  docs)
- Makefile/Dockerfile/CI comments (note if significant)
- GitHub-specific: `.github/ISSUE_TEMPLATE/`, `.github/PULL_REQUEST_TEMPLATE/`

Use Glob for pattern-based discovery:

```
**/*.md
**/*.rst
**/*.adoc
docs/**/*
doc/**/*
```

### Step 3: Catalog Each Document

For each documentation file found, **read at least the first 40 lines** to
determine its topic and audience — do not guess from the filename alone.
Record:

- **Path**: Relative path from project root
- **Format**: md, rst, txt, adoc, html, etc.
- **Size**: Approximate line count (use `wc -l` or count while reading)
- **Topic**: What the document covers (determined from title, headings, and
  opening content — not inferred from path)
- **Audience**: Who this appears to be written for:
  - End users (installation, usage, configuration)
  - Developers (API reference, architecture, contributing)
  - Operators (deployment, monitoring, troubleshooting)
  - General (README, license, changelog)
- **Has executable instructions**: Whether the doc contains code blocks with
  shell commands, installation steps, or usage examples

### Step 4: Identify Documentation Structure

Assess the overall documentation organization:

- Is there a documentation site framework (MkDocs, Sphinx, Docusaurus,
  GitBook, etc.)?
- Is there a table of contents or navigation structure?
- Is documentation flat (all in root) or hierarchical (organized in
  directories)?
- Are there cross-references between documents?

### Step 5: Note Preliminary Gaps

Without doing a deep review, flag obvious gaps:

- Project has a public API but no API reference docs
- No contributing guide despite accepting PRs
- No installation guide despite requiring setup
- Documentation exists but is clearly outdated (e.g., references very old
  versions)

### Step 6: Write the Inventory

Follow the template at `templates/inventory.md` exactly. Write the inventory to
`artifacts/inventory.md`.

## Output

- `artifacts/inventory.md`

## When This Phase Is Done

Report your findings:

- How many documentation files were discovered
- Key categories and their coverage
- Any obvious gaps noted
- Whether executable instructions were found

Then **re-read the controller** (`.claude/skills/controller/SKILL.md`) for
next-step guidance.
