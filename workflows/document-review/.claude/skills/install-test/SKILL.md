---
name: install-test
description: Execute documented installation instructions on a cluster and verify accuracy.
---

# Install Test Skill

You are executing a project's documented installation instructions on a live
OpenShift cluster to verify they work as described. For each step you compare
actual results against documented expectations, troubleshoot failures to
determine correct steps, and track common errors with their solutions.

## Your Role

Find installation instruction blocks in documentation, execute them on a
cluster, compare actual vs documented results, troubleshoot failures to
determine the correct steps, and record errors users might encounter along with
their solutions. The troubleshooting guide you produce is a primary input for
`/fix` when updating documentation with error-handling guidance.

## Critical Rules

- **Read the inventory first.** This phase requires `/scan` to have been run.
  If `artifacts/inventory.md` does not exist, inform the user
  and recommend running `/scan` first.
- **Use the cluster, not localhost.** All execution happens on the cluster
  identified by `$CLUSTER_URL`, `$CLUSTER_USERNAME`, and `$CLUSTER_PASSWORD`.
  Never run installation
  steps directly on the local host system.
- **Read-only on the local filesystem.** Do not modify project files. You may
  create temporary files in `/tmp` if needed.
- **Confirm before destructive cluster operations.** If troubleshooting
  requires destructive changes (deleting namespaces, removing CRDs, uninstalling
  operators), confirm with the user first.
- **Track every error.** Every error a user might encounter following these docs
  is valuable. Record it with the cause and solution.
- **Don't guess fixes.** When troubleshooting, verify the correct steps against
  source code, Makefile targets, or other authoritative sources in the repo.
- **Log every cluster change.** Every command that creates, modifies, or deletes
  a cluster resource must be recorded in the change log at
  `artifacts/cluster-changes.md`. This includes changes made
  during troubleshooting. The cleanup agent depends on this log to revert all
  changes.

## Cluster Environment Setup

1. Install the OpenShift CLI if not already available:

   ```bash
   bash scripts/install-oc.sh
   ```

2. Login to the cluster:

   ```bash
   oc login -u "$CLUSTER_USERNAME" -p "$CLUSTER_PASSWORD" --server="$CLUSTER_URL"
   ```

3. Verify connectivity:

   ```bash
   oc whoami
   oc version
   ```

If the phase cannot proceed for any reason, write a minimal findings file to
`artifacts/findings-install-test.md` noting the skip reason so
the final report can include it. Use this format:

```markdown
# Installation Test Findings

**Date:** [date]
**Repository:** [repository]
**Instruction:** [task and goal description]

---

**Status:** Skipped
**Reason:** [why — e.g., "CLUSTER_URL not set", "cluster login failed: unauthorized", "no installation docs found"]
```

Then stop. Do not proceed with execution steps.

Specific skip conditions:

- `$CLUSTER_URL`, `$CLUSTER_USERNAME`, or `$CLUSTER_PASSWORD` are not set —
  the phase cannot proceed without cluster access.
- `oc login` fails — record the error message as the reason.
- No installation-related documents are found in the inventory.

## Change Logging

**Before executing any command that modifies the cluster**, initialize the
change log at `artifacts/cluster-changes.md` using the template
at `templates/cluster-changes.md`.

Every cluster modification must be logged immediately after execution — do not
batch them at the end. For each change, record:

- **Action**: What was done (create, apply, patch, label, script)
- **Resource**: Kind and name (e.g., `Deployment/my-app`)
- **Namespace**: Where it lives, or `--` for cluster-scoped resources
- **Command**: The exact command that was executed
- **Revert command**: The exact command to undo this change

### What counts as a change

- `oc create`, `oc apply`, `oc run`, `oc new-project`, `oc adm` commands that
  create or modify resources
- `oc patch`, `oc label`, `oc annotate` on existing resources
- `oc delete` (record what was deleted so the cleanup report is accurate)
- `kubectl` equivalents of the above
- `helm install`, `helm upgrade`
- `make` targets that deploy to the cluster
- Any shell script that modifies cluster state

### Logging shell script effects

When a documented step runs a shell script (`bash scripts/setup.sh`, `make
deploy`, etc.), you cannot rely on the script name alone for cleanup. You must:

1. **Read the script** before executing it to understand what it will do
2. **List the expected effects** (resources created, modified, deleted)
3. **Execute the script**
4. **Verify the effects** by checking which resources now exist:

   ```bash
   oc get all -n <namespace>
   oc get crd | grep <pattern>
   ```

5. **Log each effect as a separate entry** in the change log with individual
   revert commands. Use action type `script` and record the script path.

If a script's effects cannot be fully determined by reading it (e.g., it calls
other scripts, uses dynamic resource names), log what you can identify and add
a note: `Effects may be incomplete — manual review recommended`.

## Process

### Step 1: Load Context

Read `artifacts/inventory.md`. Identify documents that contain
installation instructions — look for docs tagged with "Has Instructions: Yes"
and topics related to installation, setup, deployment, quickstart, or getting
started.

If no installation-related documents are found, write the skip findings file
(see above) and finish early.

### Step 2: Extract Installation Steps

For each installation document, extract the ordered sequence of steps:

- Fenced code blocks with `bash`, `sh`, `shell`, or `console` language tags
- Lines prefixed with `$` or `>` (shell prompt indicators)
- Numbered steps containing commands
- `oc`, `kubectl`, `helm`, `make`, or `operator-sdk` invocations
- Any command that creates, applies, or configures cluster resources

For each step, record:

- **Source**: Document path, section heading, and line number
- **Command**: The exact command to execute
- **Expected result**: Any documented output, success criteria, or resource state
- **Prerequisites**: Steps or conditions that must be met first
- **Sequence position**: Where this falls in the logical flow

### Step 3: Assess Logical Flow

Before executing, evaluate the documented order:

- Are prerequisites satisfied before they're needed?
- Are namespaces/projects created before resources reference them?
- Are CRDs installed before CRs are created?
- Are dependencies (operators, images, secrets) set up in the right order?
- Are there implicit steps the reader must infer?

Flag any ordering issues as findings before execution begins.

### Step 4: Execute Steps

For each step in sequence:

1. **Announce** what you're about to execute (document, section, command)
2. **Execute** the command on the cluster via `oc` or the documented tool
3. **Capture** stdout, stderr, and exit code
4. **Compare** the actual result with the documented expected result:
   - **Match**: Output aligns with documentation
   - **Mismatch**: Output differs from what the docs describe
   - **Undocumented result**: Command succeeds but docs don't describe what
     the user should see
5. **If the step fails:**
   - Record the exact error message
   - Investigate the cause (check resource status, events, logs):

     ```bash
     oc get events -n <namespace> --sort-by='.lastTimestamp'
     oc describe <resource> <name> -n <namespace>
     oc logs <pod> -n <namespace>
     ```

   - Determine the correct command or missing prerequisites by checking source
     code, Makefiles, Dockerfiles, or other authoritative references in the repo
   - Record the error and solution as a troubleshooting entry
   - Execute the corrected step to continue the flow
6. **Verify resource state** after creation/modification steps:

   ```bash
   oc get <resource> -n <namespace>
   oc wait --for=condition=Available <resource>/<name> -n <namespace> --timeout=120s
   ```

### Step 5: Record Findings

For each issue found, classify it:

**Documentation accuracy issues:**

- Documented command doesn't work -> **Critical** (Accuracy)
- Documented output doesn't match actual -> **Critical** (Accuracy)
- Documented prerequisite is wrong or missing -> **High** (Completeness)

**Flow issues:**

- Steps in wrong order -> **Critical** (Structure)
- Missing intermediate step -> **High** (Completeness)
- Implicit step not documented -> **High** (Completeness)

**Completeness issues:**

- No expected output documented -> **Low** (Examples)
- Missing error handling / what-if guidance -> **Low** (Completeness)
- Missing cleanup / uninstall instructions -> **High** (Completeness)

### Step 6: Write Findings

Follow the template at `templates/findings-install-test.md` exactly. Write to
`artifacts/findings-install-test.md`.

The **Troubleshooting Guide** section is critical — `/fix` uses it to add
error-handling guidance to the documentation. For every error encountered during
execution, record:

- The exact error message or symptom
- Which step triggers it
- The root cause
- The solution (exact commands to resolve it)
- How the documentation should be updated to prevent user confusion

## Output

- `artifacts/findings-install-test.md`
- `artifacts/cluster-changes.md`
