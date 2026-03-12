# Cluster Change Log

**Cluster:** [url]
**Session started:** [date/time]
**Total changes:** N

## Changes

Record every cluster modification in the order it was performed. The cleanup
agent reads this file and reverts changes in reverse order.

### Change 1: [brief description]

- **Action:** create | apply | patch | label | script
- **Resource:** [Kind/name, e.g., Namespace/my-project]
- **Namespace:** [namespace, or -- for cluster-scoped]
- **Command:** `[exact command executed]`
- **Revert command:** `[exact command to undo this change]`

### Change 2: [brief description]

- **Action:** apply
- **Resource:** Deployment/my-app
- **Namespace:** my-project
- **Command:** `oc apply -f deploy.yaml`
- **Revert command:** `oc delete deployment/my-app -n my-project --ignore-not-found`

### Change N: Executed shell script

- **Action:** script
- **Script:** `scripts/setup.sh`
- **Effects:**
  - Created ConfigMap/app-config in namespace my-project
  - Created Secret/app-secret in namespace my-project
  - Modified ServiceAccount/default in namespace my-project (added image pull secret)
- **Revert commands:**
  - `oc delete configmap/app-config -n my-project --ignore-not-found`
  - `oc delete secret/app-secret -n my-project --ignore-not-found`
