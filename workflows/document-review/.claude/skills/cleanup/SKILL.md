---
name: cleanup
description: Revert all cluster changes made during install-test using the change log.
---

# Cleanup Skill

You are reverting all changes made to the OpenShift cluster during the
install-test phase. You read the change log, revert each change in reverse
order, and report what succeeded and what could not be reverted.

## Your Role

Ensure the cluster is returned to its pre-test state. Every change recorded in
the change log must be attempted. Log all results, especially failures, so the
user knows what manual cleanup remains.

## Critical Rules

- **Revert in reverse order.** Changes must be undone in the opposite order they
  were made. Deleting a namespace before deleting its resources is fine (the
  namespace deletion cascades), but deleting a CRD before deleting its CRs
  will fail. Reverse order handles most dependency issues.
- **Never skip a change.** Attempt to revert every entry in the log, even if
  earlier reverts failed.
- **Log everything.** Record the result of every revert attempt — success or
  failure with the exact error.
- **Don't be destructive beyond the log.** Only revert changes listed in the
  change log. Do not delete resources that were not created during install-test.
- **Handle partial failures gracefully.** If a revert fails, continue with the
  remaining changes. Collect all failures for the final report.

## Inputs

- `artifacts/cluster-changes.md` — the change log produced by
  install-test

If this file does not exist or is empty, report that no changes were logged and
finish immediately.

## Cluster Login

Use the same credentials as install-test:

```bash
bash scripts/install-oc.sh
oc login -u "$CLUSTER_USERNAME" -p "$CLUSTER_PASSWORD" --server="$CLUSTER_URL"
```

If login fails, report the failure and list all changes that could not be
reverted.

## Process

### Step 1: Read the Change Log

Read `artifacts/cluster-changes.md`. Parse all change entries
and build a list of revert operations.

### Step 2: Build Revert Plan

Reverse the order of changes. For each change, determine the revert command:

**Resource creation** (`oc create`, `oc apply`, `oc run`, etc.):

```bash
oc delete <kind>/<name> -n <namespace> --ignore-not-found
```

**Namespace/project creation** (`oc new-project`, `oc create namespace`):

```bash
oc delete project <name> --ignore-not-found
```

Namespace deletion cascades to all resources within it, so if all created
resources are within a single namespace, deleting the namespace is sufficient.
Skip individual resource deletions for resources inside a namespace that will
be deleted.

**Operator installations** (Subscription, CSV, InstallPlan):

```bash
oc delete subscription <name> -n <namespace> --ignore-not-found
oc delete csv <name> -n <namespace> --ignore-not-found
```

**CRD creation:**

```bash
oc delete crd <name> --ignore-not-found
```

**Resource modifications** (patches, labels, annotations on pre-existing
resources):

- Use the original value from the change log to restore
- If original value was not recorded, flag as needing manual review

**Shell script effects:**

- Use the revert commands recorded in the change log
- If effects were not fully captured, flag as needing manual review

### Step 3: Execute Reverts

For each revert operation (in reverse order):

1. **Announce** what you're reverting
2. **Execute** the revert command
3. **Verify** the resource is gone or restored:

   ```bash
   oc get <kind>/<name> -n <namespace> 2>&1
   ```

4. **Record** the result:
   - **Success**: Resource deleted or restored
   - **Already gone**: Resource did not exist (not an error — may have been
     cascade-deleted)
   - **Failed**: Command failed — record the error message

### Step 4: Write the Cleanup Report

Follow the template at `templates/cleanup-report.md` exactly. Write to
`artifacts/cleanup-report.md`.

## Output

- `artifacts/cleanup-report.md`
