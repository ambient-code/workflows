# Docs Updater Workflow

Analyze code changes and keep documentation in sync. This workflow discovers which doc files are affected by a code diff, generates format-aware updates, and opens a docs PR.

## How It Works

1. You provide a code change (PR URL, branch diff, or local changes) and point to where your docs live (separate repo or subfolder in the same repo)
2. The workflow extracts identifiers from the changed code and searches your docs for matches
3. It evaluates each match to determine if the doc content is now stale
4. You review and select which files to update
5. It generates minimal, format-correct updates to those files
6. It opens a draft PR with the documentation updates

## Workflow Phases

| Phase | Purpose |
|-------|---------|
| **Setup** | Establish the diff source and docs location (automatic) |
| **Review** | Discover affected files and preview proposed changes |
| **Update** | Apply accepted changes to documentation files |
| **Open PR** | Push changes and create a draft pull request |

The `/index` command is available separately for building semantic indexes
on large repos.

### Typical Flow

```text
setup → review → (select files) → update → open PR
```

## Getting Started

### Scenario 1: You Have a PR URL

1. Start the workflow
2. Provide the PR URL when asked
3. Point to where docs live (subfolder, separate repo, or current directory)
4. Run `/review` to see which docs need updating

### Scenario 2: You Have Local Changes

1. Start the workflow from within the code repo
2. Choose "local uncommitted changes" when asked
3. Point to where docs live
4. Run `/review` to see which docs need updating

### Scenario 3: Large Docs Location, First Run

1. Run `/index` to build semantic indexes before starting the workflow
2. Start the workflow and complete setup
3. Choose "Review" — discovery will use the indexes automatically

## The Semantic Index System (Optional)

For most repos, the default discovery (identifier matching + grep) works well. On large docs locations with many folders, you can optionally build semantic indexes via `/index` for faster discovery.

Each folder gets an index that captures:

- What the folder documents (overview)
- What each file covers (file summaries)
- What code changes would make these docs outdated
- Key technical concepts and terms

With indexes, the workflow narrows to relevant folders first, then scans individual files — skipping folders that aren't affected by the diff.

**Important**: Indexes are only valuable if you commit and push them so future runs can reuse them. Without committing, the indexes are lost when the session ends and you'd be better off using the default grep-based discovery. Indexes are hash-based — they only rebuild when doc files change.

## Format Support

The workflow handles any text-based documentation format, including Markdown, AsciiDoc, reStructuredText, plain text, HTML, and YAML.

## Directory Structure

```text
docs-updater/
├── .ambient/
│   └── ambient.json              # Workflow configuration
├── .claude/
│   ├── commands/
│   │   └── index.md              # /index command for building semantic indexes
│   └── skills/
│       ├── controller/SKILL.md   # Phase management and transitions
│       ├── discovery/SKILL.md    # File discovery (grep or index-assisted)
│       ├── generation/SKILL.md   # Content generation
│       └── pr/SKILL.md           # PR creation
├── CLAUDE.md                     # Behavioral guidelines
└── README.md                     # This file
```

## Troubleshooting

**No docs found**: Make sure the docs location path is correct and contains documentation files.

**Empty diff**: Verify the code change source — the PR URL must be accessible, or local changes must be uncommitted.

**Too many matches**: If discovery returns too many candidates, the two-pass evaluation (quick scan then deep read) should filter out false positives. If it's still noisy, consider building indexes via `/index`.

**Format issues in generated content**: If the generated update mixes syntax (e.g., Markdown headers in an AsciiDoc file), report it — the generation skill should never mix formats.
