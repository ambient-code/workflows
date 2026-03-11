---
name: review
description: Deep quality review of the entire documentation corpus.
---

# Review Documentation Skill

You are performing a deep quality review of a project's documentation corpus.
Your job is to evaluate each document against 7 quality dimensions and produce
a structured findings report.

## Your Role

Read every document in the inventory, evaluate its quality, identify issues,
and classify findings by severity and dimension. This is a docs-only review —
you are not cross-referencing against source code (that's `/verify`).

## Critical Rules

- **Read the inventory first.** This phase requires `/scan` to have been run.
  If `artifacts/document-review/inventory.md` does not exist, inform the user
  and recommend running `/scan` first.
- **Be specific.** Every finding must cite the exact file, section, or line
  where the issue occurs.
- **Show evidence.** Quote the problematic text. Don't just say "unclear" —
  explain why.
- **Don't nitpick style.** Focus on content quality over formatting
  preferences. Minor markdown formatting issues are not worth reporting unless
  they affect readability.
- **Assess audience fit.** Identify who each document is written for and
  evaluate whether the content is appropriate for that audience.

## Quality Dimensions

Evaluate each document against these 7 dimensions:

1. **Accuracy** — Are statements factually correct? Flag claims that seem
   suspect based on what you can determine from the documentation alone. Note
   that `/verify` does deeper code cross-referencing.

2. **Completeness** — Does the document cover its topic fully? Are there
   obvious omissions? Are prerequisites listed? Are edge cases mentioned?

3. **Consistency** — Does terminology match across documents? Are formatting
   conventions consistent? Do factual claims agree between documents?

4. **Clarity** — Is the language clear and unambiguous? Are concepts explained
   before they're used? Is the level of detail appropriate for the target
   audience?

5. **Currency** — Are there references to deprecated features, old version
   numbers, dead links, or outdated screenshots? Does the content reflect the
   current state of the project?

6. **Structure** — Are headings logical and hierarchical? Does information flow
   in a sensible order? Is the document navigable? Are there appropriate
   cross-references?

7. **Examples** — Are code samples present where needed? Do examples look
   syntactically correct? Are examples explained? Do they cover common use
   cases?

## Finding Severities

Classify each finding:

- **Error** — Factually incorrect information that would mislead users
- **Gap** — Missing documentation for existing functionality or concepts
- **Inconsistency** — Contradictions between documents or within a document
- **Stale** — Outdated content, dead links, references to removed features
- **Improvement** — Could be clearer, better structured, or more helpful

## Process

### Step 1: Load the Inventory

Read `artifacts/document-review/inventory.md` to understand what documents
exist and how they're organized.

### Step 2: Review Each Document

For each document (or logical group of related documents):

1. Read the document fully
2. Identify the target audience (end user, developer, operator, general)
3. Evaluate against each of the 7 quality dimensions
4. Record findings with:
   - **Severity**: Error, Gap, Inconsistency, Stale, or Improvement
   - **Dimension**: Which quality dimension is affected
   - **Location**: File path and section heading or line reference
   - **Description**: What the issue is
   - **Evidence**: Quote the problematic text
   - **Audience impact**: How this affects the target audience

### Step 3: Cross-Document Consistency Check

After reviewing individual documents, check for cross-document issues:

- Contradictory statements between documents
- Inconsistent terminology (same concept called different names)
- Duplicated content that could drift out of sync
- Missing cross-references between related documents
- Inconsistent formatting conventions

### Step 4: Audience Assessment

For each document, evaluate audience-appropriateness:

- Is the assumed knowledge level appropriate for the target audience?
- Are prerequisites clearly stated?
- Is jargon defined or avoided based on audience?
- Does the document serve its apparent purpose (tutorial vs reference vs
  explanation)?

### Step 5: Write Findings

Follow the template at `templates/findings-review.md` exactly. Write findings to
`artifacts/document-review/findings-review.md`.

## Output

- `artifacts/document-review/findings-review.md`
