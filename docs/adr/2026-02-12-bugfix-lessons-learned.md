# Bugfix Workflow Refactor — Lessons Learned

**Date:** 2026-02-12 (updated 2026-02-14)
**PR:** feature/bugfix-workflow-skills-refactor
**Scope:** `workflows/bugfix/`

## Context

The bugfix workflow was refactored from a command-heavy design to a skill-based
architecture with a dedicated controller. Over the course of iterative testing
and revision, we discovered a number of practical lessons about how AI agents
interpret workflow instructions. This document captures those lessons for future
workflow authors.

## Lessons

### 1. Commands as thin wrappers over skills works well

The original workflow had all process logic inline in command files
(`.claude/commands/*.md`). We refactored to a three-layer architecture:
a controller skill manages flow, phase skills contain the full multi-step
process, and commands are thin wrappers that point at the controller.

The main motivation: **users get the benefit of the workflow even if they don't
know the commands exist.** With the old command-only design, all the workflow's
value was hidden behind slash commands. Users would just say "fix this bug" and
the model would comply — using its general knowledge, not the workflow's
carefully designed process. The result looked reasonable, so users thought they
were getting the workflow's benefit. They weren't. The commands never fired.

With skills, the controller can route to the appropriate phase skill regardless
of whether the user typed `/fix` or "fix this bug." The process logic is
accessible to both entry points.

Additional benefits of this separation:

- **Skills are reusable.** The controller, `CLAUDE.md`, or other skills can
  reference the same skill file. Commands are just one entry point.
- **Skills are independently editable.** You can revise a skill's process
  without touching the command wrapper, controller, or systemPrompt.
- **Commands stay simple.** A command wrapper is ~5 lines — it points at the
  controller and names the phase. There's almost nothing to get wrong.
- **The model reads the process at execution time.** Instead of loading all
  process details into the systemPrompt (where they compete for attention), the
  model reads only the skill it needs, when it needs it.

**Guideline:** Put process logic in skill files, not commands. Commands should
be pointers, not implementations.

### 2. A controller skill is the key to reliable phase transitions

This was the single most important discovery. The model consistently failed to
transition correctly between phases when flow logic was in the systemPrompt,
`CLAUDE.md`, or individual skills. After a phase completed, the model would
get stuck in the previous skill's context — saying "yes" to a recommendation
would re-run the current phase instead of advancing.

The fix: a dedicated **controller skill** (`.claude/skills/controller/SKILL.md`)
that owns all flow management. The controller:

- Has the complete phase list with one-sentence descriptions of each phase
- Defines how to execute phases (announce, read skill, execute, report)
- Owns all next-step recommendations (skills don't recommend anything)
- Gets **re-read when choosing or starting a phase** to reset context

The re-read is critical. After executing a skill, the model's context is full
of that skill's instructions. Re-reading the controller reloads the transition
rules and prevents context bleed.

We initially added a response-interpretation table to the controller ("yes" →
recommended phase, question → don't execute, etc.) but removed it. Like other
over-specified routing rules (see lesson 3 in the earlier version of this ADR),
it caused more problems than it solved. The model handles conversational intent
naturally — explicit tables gave it a competing signal.

**What we tried that didn't work:**

- **Routing rules in the systemPrompt.** The model treated them as suggestions,
  not as authoritative. They competed with skill-level instructions.
- **"Stop and wait" at multiple levels.** We added pause rules to the
  systemPrompt, `CLAUDE.md`, and every skill. This helped with auto-advance
  but didn't fix skill selection — the model still got stuck in the wrong skill.
- **Subagent dispatch via Task tool.** Launching each phase as a subagent fixed
  transitions perfectly (clean context per phase) but killed the user experience
  — the platform doesn't show subagent progress, so the user saw nothing until
  the phase was complete.

The winning pattern: **direct execution + controller re-read.** The model
executes skills in the main process (full visibility), but re-reads the
controller when it needs to decide what phase to run next (correct transitions).

**Guideline:** For multi-phase workflows, create a controller skill that owns
all flow logic. Have the model re-read it at phase transition points.

### 3. Skills should report findings, not recommend next steps

We initially had each skill end with a "Recommended next step" (e.g.,
fix → test, test → review). This caused persistent problems:

- Skills would recommend skipping phases (e.g., fix → PR, skipping test
  and review)
- Static recommendations fought with dynamic reasoning (the model recommends
  skipping to `/fix`, then the skill's hardcoded "next: `/reproduce`" pulls
  it back)
- Softening the language ("present these if they make sense") didn't help

The fix: **remove all next-step logic from skills.** Skills now end with
"Report your findings" — just the facts. The controller has a "Recommending
Next Steps" section that considers the situation and offers appropriate options.

**Guideline:** Separate concerns cleanly. Skills own process; the controller
owns flow. Don't let skills make flow decisions.

### 4. Flexible recommendations beat rigid routing tables

Our first controller had a rigid table: "assess → reproduce, reproduce →
diagnose, diagnose → fix..." This was too prescriptive. The model would
recommend `/reproduce` after an assessment even when the root cause was obvious
and `/fix` was the right call.

The fix: replace the rigid table with guidance on **when to skip forward**
(obvious root cause → offer `/fix`), **when to go back** (test failures →
offer `/fix`), and **when to end early** (trivial fix → skip `/document`).
Present multiple options with a top recommendation, not a single mandated path.

**Guideline:** Give the controller judgment, not just a lookup table. The model
is good at reading situations — give it permission to adapt.

### 5. Controller re-read timing is a balancing act

The controller must be re-read often enough to prevent the model from going
rogue, but not so often that it overwhelms the context window.

- **"Re-read after every phase completes"** wasn't enough. After a phase ended
  and the model presented recommendations, the user's next message arrived on
  a new turn. By then the controller context had faded, and the model
  interpreted "Let's just fix it" as a general instruction — dropping out of
  the workflow entirely and doing fix + test + push in one shot without pausing.
- **"Re-read before every user message"** was too aggressive. The controller is
  ~120 lines. Re-reading it on every clarifying question or mid-phase exchange
  wastes context budget.
- **"Re-read when choosing or starting a phase"** was the right balance. This
  covers the critical moments (phase transitions, user selecting next step)
  without triggering on every single message.

**Guideline:** Instruct the model to re-read the controller at decision points,
not on a fixed schedule. The systemPrompt and `CLAUDE.md` should both reinforce
this.

### 6. Phase descriptions in the controller improve recommendations

The initial controller had a table mapping phase names to skill paths, but no
descriptions. The model made poor recommendations because it only knew phase
*names*, not what each phase *does*. For example, it would skip `/review` after
`/test` because it didn't know review catches problems that tests miss.

Adding a one-sentence description to each phase ("Critically evaluate the fix
and tests — look for gaps, regressions, and missed edge cases") gave the model
enough context to make better judgment calls about which phases to recommend.

**Guideline:** Don't assume the model knows what your phases do from their
names alone. Include brief descriptions in the controller.

### 7. Less instruction text produces better behavior

The original systemPrompt was ~100 lines and included key responsibilities,
best practices, output locations, agent orchestration details, command-to-skill
mappings, and multi-paragraph behavioral instructions. The final version is
~10 lines: identity, a pointer to the controller, and the workspace layout.

**What we learned:** Every line in the systemPrompt competes for the model's
attention. Redundant instructions don't reinforce — they create ambiguity. When
two sections say similar things in different words, the model may follow either
one, and the choice is unpredictable.

**Guideline:** If a rule is already enforced where it matters (in the
controller, in a skill file, in `CLAUDE.md`), don't repeat it in the
systemPrompt.

### 8. Command wrappers must explicitly say "read the file"

The original command wrappers said: "Using the Diagnose Skill from
`.claude/skills/diagnose/SKILL.md`, apply the skill as needed." The model
treated this as conceptual guidance and improvised instead of reading the file.

Changing to "**Read** `.claude/skills/controller/SKILL.md` **and follow it**"
fixed the behavior.

**What we learned:** The model distinguishes between "here's context about a
skill" and "go read this file right now." Vague delegation ("apply the skill")
gets treated as a suggestion. Explicit file reads get treated as instructions.

**Guideline:** When you want the model to read a file, say "read" in imperative
form. Don't describe the skill — point at it.

### 9. Agents must announce phases before executing them

When the model silently picks a skill and starts executing it, the user has no
way to catch a wrong selection until the model is deep into the wrong process.

Adding a simple rule — "announce which phase you are about to run" — gives the
user a checkpoint to redirect.

**What we learned:** Phase announcement is cheap (one sentence) and prevents
expensive mistakes (running the wrong multi-step process). It also serves as a
forcing function: the model has to commit to a choice explicitly, which may
improve selection accuracy.

**Guideline:** Always require the model to announce its intent before acting.

### 10. "Never push to upstream" must explicitly include bots

The PR skill said "never push directly to upstream," but when running as
`ambient-code[bot]`, the model reasoned that the bot might have org push access
and tried to push directly. It failed, then spiraled into workarounds.

**What we learned:** The model interprets rules in context. "Never push to
upstream" is clear for human users, but the model sees a bot identity and
reasons that bots might be exceptions. The rule needed to explicitly say
"even if you are authenticated as an org bot or app."

**Guideline:** When writing prohibitions, enumerate the exceptions you want to
prevent. The model will find creative interpretations if you leave room.

### 11. GitHub App identity ≠ user identity

When `gh` is authenticated as a GitHub App (`ambient-code[bot]`), standard
commands like `gh api user` return 403. The model concluded it couldn't
determine the user's identity and couldn't find forks.

The solution: `gh api /installation/repositories --jq '.repositories[0].owner.login'`
returns the actual user's GitHub username, because the app is installed on the
user's account.

**What we learned:** Platform-specific identity resolution needs explicit
guidance. The model doesn't know about the GitHub App installation model and
won't discover this API endpoint on its own.

**Guideline:** For platform-specific workflows (auth, identity, permissions),
encode the exact commands in the skill file. Don't expect the model to discover
non-obvious API patterns.

### 12. Fork detection must search the user's account, not the bot's

The PR skill used `gh repo list --fork` (which defaults to the authenticated
identity) to find existing forks. When running as a bot, this searched the
bot's repos — which had no forks. The user's fork existed but was invisible.

**Fix:** `gh repo list GH_USER --fork` — explicitly pass the real user's
GitHub username (determined via lesson #11).

**Guideline:** Never assume the authenticated identity is the user. When
running in a managed environment, resolve the actual user identity first.

### 13. Test API responses against real data, not assumptions

The fork detection command used `.parent.nameWithOwner` in a `jq` filter, but
the GitHub API doesn't return that field on the parent object. It returns
`.parent.owner.login` and `.parent.name` separately. The filter silently
matched nothing, so the skill concluded no fork existed — even though the
user's fork was right there.

This went undetected through several rounds of testing because the skill was
always tested in scenarios where the fork didn't exist yet (so the empty result
looked correct). It only surfaced when a real fork existed and the skill still
couldn't find it.

**Guideline:** When encoding API queries in a skill file, verify the response
schema against real output. Don't assume field names from documentation or
other API endpoints — run the actual command and inspect the JSON.

### 14. GitHub App on user ≠ permission on upstream

A GitHub App installed on the user's account can push to the user's fork, but
**cannot create PRs on the upstream repo** via `gh pr create --repo upstream`.
The `createPullRequest` GraphQL mutation runs against the upstream repo, which
requires the app to be installed there — not just on the user's account.

The model's instinct when `gh pr create` fails is to debug and retry. But this
isn't a fixable error — it's a fundamental permission boundary. The skill
wasted cycles trying workarounds before falling back to an unsatisfying patch
file experience.

The fix: mark this as an **expected** outcome (not an error) when running as
a bot, and go directly to providing a GitHub compare URL that pre-fills the PR
creation form. The user clicks the link, pastes the title and body, and
submits — a much better experience than a patch file.

**Guideline:** When a failure is structural (not transient), treat it as a
known path, not an error to debug. Design the fallback as a first-class
experience, not a degraded one.

### 15. Don't give up too early on environment discovery

The model tried to run tests requiring Python 3.12, found that `python3.12`
wasn't on the PATH, and declared it couldn't run the tests. When prompted, it
discovered `uv` was available and used `uv run --python 3.12` to run them
successfully.

**What we learned:** The model's first instinct when a tool is missing is to
report failure. It doesn't automatically check for version managers (`uv`,
`pyenv`, `nvm`) that could provide the required runtime.

**Guideline:** Add a brief note in `CLAUDE.md` or relevant skills: "Check for
version managers before concluding a runtime isn't available."

### 16. Patch files should be a last resort, not a fallback

The original PR skill fell back to generating a patch file when push failed.
This was a bad user experience — the user expected help creating a PR, not a
`.patch` file to download. The fix was a 4-rung fallback ladder: try fork →
ask user to create fork → provide manual push commands → patch file only as
absolute last resort.

**What we learned:** The model gravitates toward whatever escape hatch is
available. If "generate a patch file" is documented as a fallback, the model
will reach for it quickly. Making it explicitly the last resort (with
intermediate options) forced better behavior.

**Guideline:** Order fallbacks from best UX to worst, and mark the worst ones
as "only after exhausting all other options."

## Summary

The overarching theme: **centralize flow, distribute process.**

The model performs better when it has:

- A controller skill that owns all phase transitions and recommendations
- Detailed phase skills that focus on process (not flow)
- A minimal systemPrompt that points at the controller
- Re-reads of the controller at decision points (not every turn)
- Phase descriptions in the controller to inform recommendations
- Flexible recommendations with multiple options (not rigid routing tables)
- Explicit file-read instructions (not conceptual descriptions)

And it performs worse when it has:

- Flow logic scattered across systemPrompt, CLAUDE.md, and skills
- Static next-step recommendations in skills that fight with dynamic reasoning
- Rigid routing tables that prevent adapting to the situation
- Explicit response-interpretation tables ("yes" → next phase)
- Redundant instructions across multiple locations
- Creative room in prohibitions (without closing loopholes)
- Easy escape hatches for bad outcomes (patch file as first fallback)
