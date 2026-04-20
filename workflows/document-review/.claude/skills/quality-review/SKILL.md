---
name: quality-review
description: Deep quality review of the entire documentation corpus.
---

# Quality Review Documentation Skill

You are performing a deep quality review of a project's documentation corpus.
Your job is to evaluate each document against 7 quality dimensions and produce
a structured findings report.

## Your Role

Read every document in the inventory, evaluate its quality, identify issues,
and classify findings by severity and dimension. This is a docs-only review —
you are not cross-referencing against source code (that's `/code-check`).

## Critical Rules

- **Read the inventory first.** This phase requires `/scan` to have been run.
  If `artifacts/inventory.md` does not exist, inform the user
  and recommend running `/scan` first.
- **Process one file at a time.** Review each document completely, write its
  findings to the output file, then move to the next. Do not accumulate
  findings across all documents in memory — this causes context window buildup
  that leads to skipped documents and incomplete coverage.
- **Be specific.** Every finding must cite the exact file, section, or line
  where the issue occurs.
- **Show evidence.** Every finding must include a direct quote from the
  document — the actual text that is wrong, missing, or unclear. Use a
  fenced code block or blockquote. Never describe evidence indirectly
  (e.g., "the section does not mention X"); instead quote what the section
  *does* say and explain why it falls short.
- **Don't nitpick style.** Focus on content quality over formatting
  preferences. Minor markdown formatting issues are not worth reporting unless
  they affect readability.
- **Assess audience fit.** Identify who each document is written for and
  evaluate whether the content is appropriate for that audience.

## Before You Record a Finding

Every finding must survive these checks. If any check fails, the finding is
a false positive — discard it.

### Check surrounding context

Read at least 10 lines above and below the issue before flagging it. Many
"missing" content is present in adjacent lines, tabs, or admonitions that are
easy to miss when scanning a narrow range.

- A placeholder flagged as ambiguous may be clarified in the very next
  paragraph.
- A "missing prerequisite" may be stated in an admonition or note block
  adjacent to the step.

### Follow cross-references before claiming content is absent

If a document links to another page (e.g., "see the [Validation Guide]
(validation.md)"), read the linked page before flagging missing content. The
linked page may contain the verification steps, error handling, or detail you
expected. Flag only when the linked page also lacks the content.

### Verify filesystem claims

When a document references a file or script (e.g., `./scripts/deploy.sh`),
use Glob or Read to confirm it exists before reporting "script may not exist"
or "file is missing." If the file exists, the finding is a false positive.

### Do not make definitive claims about code behavior

Quality review is a docs-only phase. If a finding depends on knowing what
the code does (e.g., whether a value is configurable, whether a handler
exists), either:

- Flag it with explicit uncertainty: "Cannot verify from docs alone —
  confirm via /code-check"
- Omit it entirely and let `/code-check` catch it

Never state "the code does X" or "the default is exactly Y" from this phase.

### Respect multi-component project boundaries

In projects with multiple components (e.g., `maas-api/`, `maas-controller/`,
an operator), deploying one component does not conflict with a separately
managed component. Before flagging a "conflict" between two deployment
instructions, verify they target the same component.

### Calibrate procedural checks for documentation context

Documentation shell snippets are not production scripts. Apply these
adjustments:

- **Variable validation.** Do not flag missing `[[ -z "$VAR" ]]` checks in
  doc snippets when the variable is set from a guaranteed source (e.g., a
  Kubernetes API call) in the same code block. Documentation prioritizes
  readability over defensive scripting.
- **Error handling.** Flag missing error guidance only when there is no
  linked troubleshooting resource AND the procedure has 5+ steps AND common
  failure modes exist. A procedure that links to a troubleshooting or
  validation guide has addressed this, even if inline error notes are absent.

## Quality Dimensions

Evaluate each document against these 7 dimensions:

1. **Accuracy** — Are statements factually correct? This includes:
   - Version numbers, command syntax, or flag names that contradict other
     documents or the project's own configuration files
   - Empty or broken code blocks that claim to show a command or output
   - Placeholder values (e.g., `username`, `password`) presented as if they
     are real values a user should copy verbatim
   - Statements that contradict what the reader would actually experience
   Flag claims that seem suspect based on what you can determine from the
   documentation alone. Note that `/code-check` does deeper code
   cross-referencing, but obvious factual errors belong here — don't defer
   everything to code-check.

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

7. **Examples** — Check every code block and inline code sample:
   - **Presence.** Are code examples provided where the reader would need
     them? A configuration reference with no example snippet, or a CLI
     description with no invocation, is a High finding.
   - **Syntax validity.** Does each code block look syntactically valid for
     the language shown (per the language tag or surrounding context)? Flag
     obviously broken syntax — unclosed brackets, unterminated strings,
     invalid YAML indentation — as a Critical finding. Empty code blocks
     (a fenced block with no content) that claim to show a command or
     output are Critical (Accuracy), not just an Examples issue.
   - **Placeholder clarity.** Are user-supplied values clearly distinguished
     from literal values? Flag values that look real but are meant to be
     replaced (e.g., `192.168.1.100` as a placeholder IP, `my-password` as
     a credential) without any indication to substitute. Severity:
     Low (Clarity).
   - **Command completeness.** Do CLI commands include all required arguments
     and flags to actually run? A command missing a required positional
     argument or a mandatory flag is a Critical finding.
   - **Explanation.** Are non-obvious code constructs explained? An example
     using advanced syntax, flags, or patterns that the target audience
     would not recognize should have accompanying explanation. Severity:
     Low.

## Finding Severities

Classify each finding by impact:

- **Critical** — Incorrect information, broken commands, or missing steps that would block users or cause them to take wrong actions
- **High** — Significant gaps, contradictions, or outdated content that degrades the user experience
- **Medium** — Issues that cause confusion but have workarounds or limited impact
- **Low** — Minor improvements to clarity, structure, or presentation

## Reviewer Lens

Different document types need different scrutiny. After identifying what a
document is, adopt the appropriate lens to focus your evaluation.

### Detecting document type

Classify each document as one of:

- **Procedural** — contains numbered steps, shell commands, installation
  instructions, tutorials, quickstarts, or getting-started guides. The reader
  intends to follow along and do something.
- **Conceptual** — explains how something works, describes architecture, or
  provides background context. The reader is trying to understand, not act.
- **Reference** — catalogs options, parameters, API fields, or configuration
  keys. The reader looks up specific facts.
- **Mixed** — combines explanatory sections with procedural steps (e.g., an
  architecture overview followed by a deployment guide). Apply both lenses to
  the relevant sections.

Use the inventory's "Has Instructions" field as a starting signal, but verify
by reading the document — some docs tagged "No" contain implicit instructions,
and some tagged "Yes" are primarily conceptual with minor code snippets.

### Developer lens (procedural and reference docs)

Read as an implementer who will follow every step and run every command. Ask:

- Can I actually follow this from start to finish?
- Are the prerequisites complete before I start?
- Will these commands run as written?
- What happens when something goes wrong?
- Can I verify each step succeeded?

This lens triggers the **procedural document checks** below and emphasizes the
**Examples** and **Completeness** dimensions. Findings from this lens are
typically high-severity (Critical, High) because they directly block users.

### Architect lens (conceptual docs)

Read as someone building a mental model of the system. Ask:

- **Internal consistency.** Does the description of components and their
  relationships hold together? Flag contradictions between prose and diagrams,
  or between different sections of the same document. Severity: Critical
  (Accuracy) or Medium (Consistency).
- **Abstraction level.** Is the depth right for the audience? Flag
  implementation details that belong in a procedure rather than a concept.
  Flag content that is too abstract for a developer who needs concrete
  guidance. Severity: Low (Clarity).
- **"Why" context.** Does the document explain *why*, not just *what*?
  Configuration options should explain when you would use them and what
  trade-offs are involved. Architecture descriptions should explain design
  decisions, not just list components. Severity: High (Completeness) if
  entirely absent, Low (Clarity) if present but shallow.
- **Onward paths.** Are there cross-references where a reader would need to
  go elsewhere to complete a task or deepen understanding? A concept that
  describes a feature but never links to the procedure for using it is a High
  finding (Structure).

This lens emphasizes the **Accuracy**, **Clarity**, and **Structure**
dimensions.

## Procedural Document Checks

When a document contains executable instructions (tagged "Has Instructions:
Yes" in the inventory, or containing numbered steps, shell commands, or
installation procedures), apply these additional checks. These catch the
highest-impact documentation gaps — issues that leave users stuck with no
recourse when something goes wrong.

### Failure path coverage

- **Verification steps.** Every command or action that changes state should
  have a way to confirm it succeeded. Flag procedures where a create/apply/
  install step has no corresponding get/describe/status check. Example: an
  `oc apply -f manifest.yaml` with no `oc get` to confirm the resource exists
  is a High finding (Completeness).
- **Error guidance.** Flag procedures that describe only the happy path with no
  mention of what to do if a step fails. At minimum, common failure modes
  should be acknowledged. A procedure with 5+ steps and zero error handling is
  a High finding (Completeness).
- **Undocumented intermediate state.** Flag procedures where failure at step N
  would leave the system in a state the documentation never describes. If a
  user gets halfway through and something breaks, can they recover or roll
  back? Missing rollback/undo guidance is a High finding (Completeness).
- **Prerequisite placement.** Flag prerequisites that first appear mid-procedure
  rather than at the top. A tool, credential, or permission that is needed at
  step 5 but not mentioned until step 5 is a High finding (Structure).

### Cross-step consistency

Check that variable names, resource names, file paths, and output values chain
correctly across steps. If step 2 creates a resource named `my-app` but step 4
references `myapp`, flag it as Critical (Accuracy).

Classify procedural findings using the same severity and dimension system as
all other findings. The most common classification is High (Completeness) for
missing verification, error handling, and rollback guidance.

## Process

### Step 1: Load the Inventory

Read `artifacts/inventory.md` to understand what documents
exist and how they're organized. Build a list of all document paths to review.

### Step 2: Initialize the Findings File

Write the file header to `artifacts/findings-quality-review.md` using
the template at `templates/findings-quality-review.md`. Fill in the date, repository, commit SHA,
and instruction. Leave the summary table counts as `N` — you will update them
at the end.

Write the `## Findings by Document` heading. The file is now ready to receive
per-document findings incrementally.

### Step 3: Review Each Document (One at a Time)

Process documents **one at a time** to prevent context window buildup. For each
document:

1. **Read** the document fully
2. **Identify** the target audience (end user, developer, operator, general)
3. **Detect document type** — classify as procedural, conceptual, reference, or
   mixed (see Reviewer Lens above). This determines which lens to apply.
4. **Assess audience fit:**
   - Is the assumed knowledge level appropriate for the target audience?
   - Are prerequisites clearly stated?
   - Is jargon defined or avoided based on audience?
   - Does the document serve its apparent purpose (tutorial vs reference vs
     explanation)?
5. **Evaluate** against each of the 7 quality dimensions
6. **Apply lens-specific checks:**
   - **Procedural / reference / mixed docs** → apply the developer lens and
     procedural document checks (failure path coverage, cross-step consistency).
     These are the highest-value findings for procedural docs.
   - **Conceptual / mixed docs** → apply the architect lens (internal
     consistency, abstraction level, "why" context, onward paths).
   - For mixed docs, apply both sets of checks to the relevant sections.
7. **Record** findings with:
   - **Severity**: Critical, High, Medium, or Low
   - **Dimension**: Which quality dimension is affected
   - **File**: File path and line in backticks (e.g., `docs/guide.md:42`)
   - **Issue**: What the problem is
   - **Evidence**: Quote the problematic text
   - **Fix**: The correction, if known with high confidence (omit if unsure)
   - **Audience impact**: How this affects the target audience
8. **Append** the document's section to `artifacts/findings-quality-review.md`
   immediately — including the document heading, audience assessment, and all
   findings (or an explicit note that no issues were found). Do not hold
   findings in memory across documents.

If a document has no issues, still append its section with a note:
`No issues identified.`

### Step 4: Cross-Document Consistency Check

After all individual documents have been reviewed, check for cross-document
issues:

- Contradictory statements between documents
- Inconsistent terminology (same concept called different names)
- Duplicated content that could drift out of sync
- Missing cross-references between related documents
- Inconsistent formatting conventions

Append the `## Cross-Document Issues` section to the findings file.

### Step 5: Update Summary Table

Read the findings file you have built. Count findings for each
dimension × severity cell. Update the summary table at the top of
`artifacts/findings-quality-review.md` with the actual counts,
replacing the placeholder `N` values. Include row totals (per dimension) and
column totals (per severity).

## Output

- `artifacts/findings-quality-review.md`
