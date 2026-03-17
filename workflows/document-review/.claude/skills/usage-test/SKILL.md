---
name: usage-test
description: Interact with the installed project as a user would and verify usage documentation accuracy.
---

# Usage Test Skill

You are interacting with a project that has just been installed on a live
OpenShift cluster. Your job is to follow the project's documented usage
instructions — API calls, CLI commands, workflows, and interactions — and
verify that the documentation accurately reflects the actual user experience.

## Your Role

Find post-installation usage documentation (getting started, tutorials, usage
guides, API examples), execute the documented interactions on the cluster,
compare actual results against documented expectations, and record
discrepancies. This phase answers: "Now that the project is installed, does the
documentation accurately describe how to use it?"

## Critical Rules

- **Install-test must have succeeded.** This phase requires a working
  installation on the cluster. If
  `artifacts/document-review/findings-install-test.md` does not exist or shows
  the install was skipped or failed, write a skip file and stop.
- **Read the inventory first.** If `artifacts/document-review/inventory.md`
  does not exist, inform the user and recommend running `/scan` first.
- **Use the cluster, not localhost.** All interactions happen on the cluster
  identified by `$CLUSTER_URL` and `$CLUSTER_TOKEN`.
- **Read-only on the local filesystem.** Do not modify project files. You may
  create temporary files in `/tmp` if needed.
- **Log every cluster change.** Append to the existing change log at
  `artifacts/document-review/cluster-changes.md`. The cleanup agent will
  revert these along with install-test changes.
- **Don't guess expected behavior.** Compare only against what the
  documentation explicitly states. If behavior is undocumented, record it as
  a gap.

## Cluster Environment

The cluster should already be authenticated from install-test. Verify
connectivity:

```bash
oc whoami
oc version
```

If the session has expired, re-authenticate:

```bash
bash scripts/install-oc.sh
oc login --token="$CLUSTER_TOKEN" --server="$CLUSTER_URL"
```

If the phase cannot proceed, write a skip file to
`artifacts/document-review/findings-usage-test.md`:

```markdown
# Usage Test Findings

**Project:** [name]
**Tested:** [date]
**Status:** Skipped
**Reason:** [why — e.g., "install-test did not succeed", "no usage docs found"]
```

Then stop. Do not proceed with interaction steps.

Specific skip conditions:

- `artifacts/document-review/findings-install-test.md` does not exist, shows
  `**Status:** Skipped`, or shows critical installation failures — the phase
  cannot proceed without a working installation.
- `oc login` fails — record the error message as the reason.
- No usage or post-installation documentation is found in the inventory.

## What to Test

Focus on documented post-installation interactions. Exclude pure installation
and setup documentation (already covered by install-test).

### API and Route Access

- Documented API endpoints (curl commands, REST calls)
- Documented routes (web console URLs, service endpoints)
- Expected response formats and status codes

### CLI Interactions

- Documented `oc` / `kubectl` commands for interacting with installed resources
- CRUD operations on custom resources
- Status and health checks

### Documented Workflows

- End-to-end usage scenarios (e.g., "create a resource, verify it, modify it")
- Multi-step procedures in usage or tutorial documentation
- Documented configuration changes and their expected effects

### Expected Behaviors

- Documented outputs and responses
- Status transitions and state changes
- Documented error messages and how to handle them

### Feature Verification

- Do documented features actually work on the running installation?
- Do documented options and parameters have the described effect?

## Change Logging

Append to the **existing** change log at
`artifacts/document-review/cluster-changes.md`. Do not overwrite it — it
already contains install-test changes. Follow the same format:

- **Action**: What was done
- **Resource**: Kind and name
- **Namespace**: Where it lives
- **Command**: The exact command executed
- **Revert command**: The exact command to undo this change

Log every create, apply, patch, delete, or modification you make during
usage testing.

## Process

### Step 1: Load Context

Read these files:

- `artifacts/document-review/inventory.md` — identify usage documentation
- `artifacts/document-review/findings-install-test.md` — confirm install
  succeeded and understand what was installed

Check the install-test findings status. If the status is "Skipped" or shows
critical failures that prevented installation, write the skip file and stop.

### Step 2: Identify Usage Documentation

From the inventory, find documents about:

- Usage, interaction, getting started (post-install)
- Tutorials and walkthroughs
- API reference with examples
- CLI usage examples
- Configuration and customization guides
- Operational procedures (monitoring, scaling, troubleshooting)

Exclude pure installation/setup documentation (already covered by
install-test). Focus on what comes AFTER installation.

If no usage documentation is found, write the skip file with reason "no
usage documentation found" and stop.

### Step 3: Extract Interaction Steps

For each usage document, extract the documented interactions:

- API calls with expected responses
- CLI commands with expected output
- Configuration changes with expected effects
- Multi-step workflows

For each interaction, record:

- **Source**: Document path, section heading, and line number
- **Interaction**: The exact command or action
- **Expected result**: Documented output, response, or behavior
- **Prerequisites**: What must be true for this interaction to work

### Step 4: Execute Interactions

For each interaction:

1. **Announce** what you're about to test
2. **Verify prerequisites** — check that required resources exist on the
   cluster
3. **Execute** the documented interaction
4. **Capture** stdout, stderr, and exit code
5. **Compare** actual result with documented expectation:
   - **Match**: Behavior matches documentation
   - **Mismatch**: Behavior differs from documentation
   - **Undocumented**: Interaction works but docs don't describe what to expect
6. **If the interaction fails:**
   - Record the exact error
   - Investigate the cause (check resource status, events, logs):

     ```bash
     oc get events -n <namespace> --sort-by='.lastTimestamp'
     oc describe <resource> <name> -n <namespace>
     oc logs <pod> -n <namespace>
     ```

   - Determine whether this is a documentation issue or an installation issue
   - Record the error and root cause
7. **Log any cluster changes** made during the interaction to the change log

### Step 5: Assess User Experience

Beyond step-by-step accuracy, evaluate the documented user journey:

- **Discoverability**: Would a user know to try these interactions after
  installing? Are usage docs linked from install docs?
- **Completeness**: Do usage docs cover the primary use cases of the installed
  project?
- **Feedback**: Do docs tell the user how to confirm interactions worked?
- **Error paths**: Do docs explain what to do if an interaction fails?

### Step 6: Record Findings

Classify each finding:

- Documented interaction doesn't work → **Critical** (Accuracy)
- Documented output doesn't match actual → **Critical** (Accuracy)
- Feature works but usage is undocumented → **High** (Completeness)
- Missing link from install docs to usage docs → **High** (Structure)
- Interaction works but no expected output documented → **Low** (Examples)
- Usage docs don't cover error scenarios → **Low** (Completeness)

### Step 7: Write Findings

Follow the template at `templates/findings-usage-test.md` exactly. Write to
`artifacts/document-review/findings-usage-test.md`.

## Output

- `artifacts/document-review/findings-usage-test.md`
- Appended entries in `artifacts/document-review/cluster-changes.md`
