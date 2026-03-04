---
name: test
description: Execute documented instructions and verify actual vs expected output.
---

# Test Documentation Skill

You are executing instructions found in project documentation to verify they
work as described. This phase validates quickstarts, installation guides, usage
examples, and any other documented instructions by running them and comparing
actual output against expected output.

## Your Role

Find executable instruction blocks in documentation, run them, verify the
results, and report discrepancies. Because this workflow may run in a
long-lived environment, you must revert all changes after testing.

## Critical Rules

- **Read the inventory first.** This phase requires `/scan` to have been run.
  If `artifacts/document-review/inventory.md` does not exist, inform the user
  and recommend running `/scan` first.
- **Always revert changes.** The environment is potentially long-lived. Every
  change you make during testing must be undone. Track everything.
- **Use timeouts.** Never let a command run indefinitely. Use reasonable
  timeouts (30 seconds for most commands, longer for builds/installs).
- **Don't skip prerequisite checks.** Missing prerequisites are findings, not
  reasons to abort silently.
- **Be safe.** Never execute commands that could be destructive to the host
  system (rm -rf /, modifying system files, etc.). Skip dangerous commands and
  report them as untestable.

## Process

### Step 1: Identify Executable Instructions

Read the inventory and scan documentation files for executable content:

**What counts as executable instructions:**

- Fenced code blocks with `bash`, `sh`, `shell`, `console`, or `zsh` language
- Lines prefixed with `$` or `>` (shell prompt indicators)
- Numbered steps containing commands (e.g., "1. Run `pip install mypackage`")
- Installation sections with package manager commands
- Quickstart or getting-started guides with sequential commands
- Usage examples showing command invocations and expected output

**What to skip:**

- Code blocks showing file contents to create (these are reference, not
  instructions)
- Pseudocode or algorithm descriptions
- Code blocks in languages that aren't shell commands (Python/JS/etc. snippets
  that are illustrative, not instructions to execute)
- Commands that are clearly destructive or require sudo/root access
- Commands that require external services not available locally (cloud APIs,
  databases, etc.)

For each instruction block, record:

- Source document and location (file:section:line)
- The commands to execute
- Any expected output documented alongside the commands
- Prerequisites mentioned in the surrounding text
- Whether commands form a sequence (later commands depend on earlier ones)

### Step 2: Check Prerequisites

Before executing any instructions, verify the environment has required tools:

```bash
# Check for common runtimes
which python3 python node go java ruby rustc 2>/dev/null
# Check for package managers
which pip pip3 npm yarn pnpm cargo gem bundle 2>/dev/null
# Check for common tools
which docker git curl wget make cmake 2>/dev/null
```

For each instruction block:

1. Identify what tools/runtimes it requires
2. Check if they're available in the current environment
3. If a prerequisite is missing:
   - Record a finding: **severity depends on whether the doc mentions the
     prerequisite**
   - If the doc says "Prerequisites: Python 3.8+" and Python is missing →
     severity: **Error** (dimension: Completeness, tagged as
     "prerequisite unavailable — cannot verify")
   - If the doc doesn't mention the prerequisite at all → severity: **Gap**
     (dimension: Completeness — "undocumented prerequisite")
   - Skip that instruction block and move to the next

### Step 3: Snapshot Environment State

Before executing anything, capture the current state:

```bash
# Record working directory
pwd

# If in a git repo, save state
git rev-parse HEAD 2>/dev/null
git status --porcelain 2>/dev/null
git stash list 2>/dev/null

# Record installed packages (as relevant to the instructions)
pip freeze 2>/dev/null > /tmp/docreview-pip-before.txt
npm list -g --depth=0 2>/dev/null > /tmp/docreview-npm-before.txt
```

Also track:

- New files/directories that will be created
- Packages that will be installed
- Configuration changes that will be made
- Environment variables that will be set

### Step 4: Execute Instructions

For each instruction block (in order of appearance in the docs):

1. **Announce** what you're about to test: the document, section, and commands
2. **Execute** each command with a timeout:
   - Capture stdout and stderr separately
   - Record the exit code
   - Note wall-clock time for long-running commands
3. **Compare** output against documented expectations:
   - If the doc shows expected output, compare actual vs expected
   - If the doc doesn't show expected output, record the actual output and
     note that no expectation was documented
4. **Record** the result before moving to the next block

**Handling sequential dependencies:**

If command B depends on command A (e.g., "install the package" then "run the
tool"), and command A fails:

- Record command A's failure
- Skip command B and note it was skipped due to the prior failure
- Continue with the next independent instruction block

### Step 5: Record Findings

For each instruction block tested, add a finding to
`artifacts/document-review/findings.md`:

**Pass** (no finding needed unless there's a notable observation):

- Command ran successfully
- Output matches documented expectation (if one was provided)

**Fail — wrong output:**

- **Severity:** Error
- **Dimension:** Accuracy
- Command ran but output differs from documentation
- Include both expected and actual output

**Fail — command error:**

- **Severity:** Error
- **Dimension:** Accuracy
- Command failed with a non-zero exit code
- Include the error message

**Fail — missing prerequisite:**

- **Severity:** Error or Gap (see Step 2)
- **Dimension:** Completeness
- Required tool or runtime not available

**Unclear — no expected output documented:**

- **Severity:** Improvement
- **Dimension:** Examples
- Command ran successfully but doc doesn't state what the user should see
- Include actual output for reference

Format for findings:

```markdown
## Instruction Test Results

**Tested:** [date]
**Environment:** [OS, key tool versions]
**Instruction blocks found:** N
**Tested:** N
**Skipped:** N (reasons)

### [path/to/document.md] — "[Section Name]"

#### Test: [brief command description]

- **Severity:** Error
- **Dimension:** Accuracy
- **Location:** quickstart.md, "Step 3: Run the server", line 45
- **Command:** `myapp serve --port 8080`
- **Expected output:** (from docs)
  ```
  Server running on http://localhost:8080
  ```
- **Actual output:**
  ```
  Error: unknown flag --port, did you mean --listen-port?
  ```
- **Assessment:** The `--port` flag was renamed to `--listen-port`. Docs need
  updating.
```

### Step 6: Revert Environment Changes

After all testing is complete, restore the environment:

**File system changes:**

```bash
# Remove any files/directories created during testing
rm -rf /path/to/created/files

# If in a git repo, restore working tree
git checkout -- . 2>/dev/null
git clean -fd 2>/dev/null
```

**Installed packages:**

```bash
# Compare before/after and uninstall additions
# For pip:
pip freeze > /tmp/docreview-pip-after.txt
diff /tmp/docreview-pip-before.txt /tmp/docreview-pip-after.txt
# Uninstall packages that were added during testing

# For npm:
npm list -g --depth=0 > /tmp/docreview-npm-after.txt
# Uninstall packages that were added during testing
```

**Cleanup temp files:**

```bash
rm -f /tmp/docreview-pip-before.txt /tmp/docreview-pip-after.txt
rm -f /tmp/docreview-npm-before.txt /tmp/docreview-npm-after.txt
```

**What to log:**

- List every change that was reverted
- Flag anything that could not be automatically reverted
- Note if the environment state was successfully restored

**If revert fails:**

- Do not silently ignore failed reverts
- Report what couldn't be reverted to the user
- Provide manual cleanup instructions

## Output

- Enriches `artifacts/document-review/findings.md` with test results

## When This Phase Is Done

Report your findings:

- Number of instruction blocks found, tested, and skipped
- Pass/fail results with key failures highlighted
- Any prerequisite issues encountered
- Whether the environment was successfully reverted
- List anything that could not be reverted

Then **re-read the controller** (`.claude/skills/controller/SKILL.md`) for
next-step guidance.
