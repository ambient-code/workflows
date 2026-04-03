# /odh-install - Install Open Data Hub on OpenShift Cluster

Install Open Data Hub (ODH) on an OpenShift cluster using OLM (Operator Lifecycle Manager).

## Command Usage

```bash
/odh-install                                      # Latest stable nightly (default)
/odh-install channel=fast                         # Explicit fast channel
/odh-install image=quay.io/opendatahub/opendatahub-operator-catalog:odh-stable-nightly
/odh-install channel=fast image=quay.io/opendatahub/opendatahub-operator-catalog:latest
```

## Available Tags

| Image Tag | Description | Use Case |
|-----------|-------------|----------|
| `odh-stable-nightly` (default) | Daily nightly from main branch | Testing latest ODH builds |
| `latest` | Most recent CI build (any branch) | Bleeding edge |
| `odh-stable` | Latest stable release | Stable deployments |

## Available Channels

| Channel | Description |
|---------|-------------|
| `fast` (default) | Frequent releases tracking main |
| `stable` | Stable releases only |

## Key Differences from RHOAI

| | RHOAI | ODH |
|-|-------|-----|
| Package | `rhods-operator` | `opendatahub-operator` |
| Operator namespace | `redhat-ods-operator` | `openshift-operators` |
| App namespace | `redhat-ods-applications` | `opendatahub` |
| Catalog image | `quay.io/rhoai/rhoai-fbc-fragment` | `quay.io/opendatahub/opendatahub-operator-catalog` |
| Default channel | `stable-3.4` / `beta` | `fast` |

## Prerequisites

1. **Cluster access**: Logged into OpenShift cluster with cluster-admin privileges (use `/oc-login`)
2. **Tools installed**: `oc` CLI must be available
3. **No existing ODH**: For fresh installations only (use `/odh-update` to update)

## Process

### Step 1: Parse Input Arguments

```bash
CATALOG_IMAGE="quay.io/opendatahub/opendatahub-operator-catalog:odh-stable-nightly"
CHANNEL="fast"

for arg in "$@"; do
  case "$arg" in
    channel=*)
      CHANNEL="${arg#*=}"
      ;;
    image=*)
      CATALOG_IMAGE="${arg#*=}"
      ;;
    *)
      echo "Unknown parameter: $arg (expected: channel= or image=)"
      ;;
  esac
done

echo "Catalog image: $CATALOG_IMAGE"
echo "Channel: $CHANNEL"
```

### Step 2: Verify Cluster Access

```bash
oc whoami &>/dev/null || { echo "ERROR: Not logged into OpenShift cluster"; exit 1; }
echo "Logged in as: $(oc whoami)"
echo "Cluster: $(oc whoami --show-server)"

# Check not already installed
if oc get csv -n openshift-operators 2>/dev/null | grep -q opendatahub-operator; then
  echo "ERROR: ODH already installed. Use /odh-update to update."
  exit 1
fi
echo "No existing ODH installation detected"
```

### Step 3: Create CatalogSource

```bash
echo "Creating ODH CatalogSource..."
cat << EOF | oc apply -f -
apiVersion: operators.coreos.com/v1alpha1
kind: CatalogSource
metadata:
  name: odh-catalog
  namespace: openshift-marketplace
spec:
  sourceType: grpc
  image: ${CATALOG_IMAGE}
  displayName: Open Data Hub
  publisher: ODH Community
  updateStrategy:
    registryPoll:
      interval: 15m
  grpcPodConfig:
    securityContextConfig: restricted
EOF

# Wait for catalog pod to be running
TIMEOUT=120
ELAPSED=0
while [[ $ELAPSED -lt $TIMEOUT ]]; do
  PHASE=$(oc get pod -n openshift-marketplace -l olm.catalogSource=odh-catalog \
    -o jsonpath='{.items[0].status.phase}' 2>/dev/null || echo "")
  if [[ "$PHASE" == "Running" ]]; then
    echo "CatalogSource ready"
    break
  fi
  sleep 5
  ELAPSED=$((ELAPSED + 5))
  echo "Waiting for catalog pod... (${ELAPSED}s/${TIMEOUT}s)"
done
```

### Step 4: Create Subscription

ODH installs into `openshift-operators` which already has a global OperatorGroup — no need to create one.

```bash
echo "Creating ODH Subscription..."
cat << EOF | oc apply -f -
apiVersion: operators.coreos.com/v1alpha1
kind: Subscription
metadata:
  name: opendatahub-operator
  namespace: openshift-operators
spec:
  channel: ${CHANNEL}
  name: opendatahub-operator
  source: odh-catalog
  sourceNamespace: openshift-marketplace
  installPlanApproval: Automatic
EOF
```

### Step 5: Wait for Operator CSV

```bash
TIMEOUT=600
ELAPSED=0

while [[ $ELAPSED -lt $TIMEOUT ]]; do
  CSV_LINE=$(oc get csv -n openshift-operators 2>/dev/null | grep opendatahub-operator || echo "")
  if [[ -n "$CSV_LINE" ]]; then
    CSV_NAME=$(echo "$CSV_LINE" | awk '{print $1}')
    CSV_PHASE=$(echo "$CSV_LINE" | awk '{print $NF}')
    echo "CSV: $CSV_NAME, Phase: $CSV_PHASE"
    if [[ "$CSV_PHASE" == "Succeeded" ]]; then
      echo "ODH operator installed successfully"
      break
    fi
  fi
  sleep 10
  ELAPSED=$((ELAPSED + 10))
  echo "Waiting for CSV... (${ELAPSED}s/${TIMEOUT}s)"
done

[[ "$CSV_PHASE" == "Succeeded" ]] || { echo "ERROR: CSV did not reach Succeeded"; exit 1; }
```

### Step 6: Create DSCInitialization

```bash
echo "Creating DSCInitialization..."
cat << EOF | oc apply -f -
apiVersion: dscinitialization.opendatahub.io/v1
kind: DSCInitialization
metadata:
  name: default-dsci
spec:
  applicationsNamespace: opendatahub
  monitoring:
    managementState: Managed
    namespace: opendatahub
  trustedCABundle:
    managementState: Managed
  devFlags:
    logMode: production
EOF
sleep 10
```

### Step 7: Create DataScienceCluster

```bash
echo "Creating DataScienceCluster..."
cat << EOF | oc apply -f -
apiVersion: datasciencecluster.opendatahub.io/v1
kind: DataScienceCluster
metadata:
  name: default-dsc
spec:
  components:
    dashboard:
      managementState: Managed
    workbenches:
      managementState: Managed
    datasciencepipelines:
      managementState: Managed
    kserve:
      managementState: Managed
      serving:
        managementState: Removed
    modelmeshserving:
      managementState: Managed
    ray:
      managementState: Managed
    kueue:
      managementState: Managed
    trainingoperator:
      managementState: Managed
    trustyai:
      managementState: Managed
    modelregistry:
      managementState: Managed
    feastoperator:
      managementState: Managed
EOF
```

### Step 8: Wait for DSC Ready

```bash
TIMEOUT=600
ELAPSED=0

while [[ $ELAPSED -lt $TIMEOUT ]]; do
  READY=$(oc get datasciencecluster default-dsc \
    -o jsonpath='{.status.conditions[?(@.type=="Ready")].status}' 2>/dev/null || echo "")
  echo "DSC Ready: ${READY:-Unknown}"
  if [[ "$READY" == "True" ]]; then
    echo "DataScienceCluster is Ready"
    break
  fi
  sleep 15
  ELAPSED=$((ELAPSED + 15))
  echo "Waiting for DSC... (${ELAPSED}s/${TIMEOUT}s)"
done
```

### Step 9: Verify Installation

```bash
echo ""
echo "=== ODH Installation Summary ==="
echo ""
echo "CSV:"
oc get csv -n openshift-operators | grep opendatahub-operator

echo ""
echo "DSC Status:"
oc get datasciencecluster default-dsc \
  -o jsonpath='{range .status.conditions[*]}{.type}{": "}{.status}{"\n"}{end}' | grep -v "False"

echo ""
echo "Dashboard:"
DASHBOARD=$(oc get route odh-dashboard -n opendatahub -o jsonpath='{.spec.host}' 2>/dev/null || echo "Not ready yet")
echo "  https://$DASHBOARD"

echo ""
echo "ODH installation complete!"
```

## Common Issues

| Problem | Solution |
|---------|----------|
| CSV stuck in `Installing` | Check operator pod logs: `oc logs -n openshift-operators -l name=opendatahub-operator` |
| DSC not Ready | Check components: `oc get dsc default-dsc -o yaml \| grep -A5 conditions` |
| Feast label selector error | Delete old deployment: `oc delete deployment feast-operator-controller-manager -n opendatahub` |
| Catalog pod not starting | Check image pull: `oc describe pod -n openshift-marketplace -l olm.catalogSource=odh-catalog` |
