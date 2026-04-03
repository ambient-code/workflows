# /odh-update - Update Open Data Hub to Latest Nightly

Update an existing ODH installation to the latest nightly build or a specific version.

## Command Usage

```bash
/odh-update                                       # Pull latest odh-stable-nightly
/odh-update image=quay.io/opendatahub/opendatahub-operator-catalog:odh-stable-nightly
/odh-update image=quay.io/opendatahub/opendatahub-operator-catalog:latest
```

## Available Image Tags

| Tag | Updated | Use Case |
|-----|---------|----------|
| `odh-stable-nightly` (default) | Daily at midnight UTC | Pull latest nightly |
| `latest` | On every push | Bleeding edge |
| `odh-stable` | Stable releases | Stable deployments |

## How ODH Updates Work

ODH nightlies typically bump the CSV version daily (unlike RHOAI stable which keeps the same version). This means:
- **Updating the CatalogSource + refreshing the catalog pod** is usually enough
- OLM detects the new CSV version and auto-creates an InstallPlan
- No forced reinstall needed in most cases (unlike RHOAI)

If the CSV version doesn't change (component images only), this command handles the forced reinstall automatically.

## Prerequisites

1. **Existing ODH**: ODH must already be installed (use `/odh-install` for fresh installations)
2. **Cluster access**: Logged into OpenShift cluster with cluster-admin privileges (use `/oc-login`)

## Process

### Step 1: Parse Input Arguments

```bash
CATALOG_IMAGE="quay.io/opendatahub/opendatahub-operator-catalog:odh-stable-nightly"

for arg in "$@"; do
  case "$arg" in
    image=*)
      CATALOG_IMAGE="${arg#*=}"
      ;;
    *)
      echo "Unknown parameter: $arg (expected: image=)"
      ;;
  esac
done

echo "Target catalog image: $CATALOG_IMAGE"
```

### Step 2: Verify Cluster Access and Existing Installation

```bash
oc whoami &>/dev/null || { echo "ERROR: Not logged into OpenShift cluster"; exit 1; }
echo "Logged in as: $(oc whoami)"
echo "Cluster: $(oc whoami --show-server)"

CSV_LINE=$(oc get csv -n openshift-operators 2>/dev/null | grep opendatahub-operator || echo "")
[[ -n "$CSV_LINE" ]] || { echo "ERROR: ODH not installed. Use /odh-install first."; exit 1; }

CURRENT_CSV=$(echo "$CSV_LINE" | awk '{print $1}')
CURRENT_CHANNEL=$(oc get subscription opendatahub-operator -n openshift-operators \
  -o jsonpath='{.spec.channel}' 2>/dev/null || echo "fast")

echo "Current CSV: $CURRENT_CSV"
echo "Current channel: $CURRENT_CHANNEL (will be preserved)"
```

### Step 3: Update CatalogSource

```bash
echo "Updating ODH CatalogSource to: $CATALOG_IMAGE"
oc patch catalogsource odh-catalog -n openshift-marketplace --type=merge \
  -p "{\"spec\":{\"image\":\"${CATALOG_IMAGE}\"}}" 2>&1 || {
  # CatalogSource may not exist yet, create it
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
EOF
}
```

### Step 4: Force Catalog Refresh

```bash
echo "Forcing catalog pod to pull latest image..."
oc delete pod -n openshift-marketplace -l olm.catalogSource=odh-catalog 2>/dev/null || true

TIMEOUT=120
ELAPSED=0
while [[ $ELAPSED -lt $TIMEOUT ]]; do
  PHASE=$(oc get pod -n openshift-marketplace -l olm.catalogSource=odh-catalog \
    -o jsonpath='{.items[0].status.phase}' 2>/dev/null || echo "")
  if [[ "$PHASE" == "Running" ]]; then
    echo "Catalog refreshed with latest image"
    break
  fi
  sleep 5
  ELAPSED=$((ELAPSED + 5))
  echo "Waiting for catalog pod... (${ELAPSED}s/${TIMEOUT}s)"
done
```

### Step 5: Wait for OLM to Detect New Version

OLM polls the catalog every 15 minutes but also reacts within ~30s of the catalog pod coming up.

```bash
echo "Waiting for OLM to detect new CSV version..."
sleep 30

NEW_CSV_LINE=$(oc get csv -n openshift-operators 2>/dev/null | grep opendatahub-operator || echo "")
NEW_CSV=$(echo "$NEW_CSV_LINE" | awk '{print $1}')

if [[ "$NEW_CSV" != "$CURRENT_CSV" ]]; then
  echo "New CSV detected: $NEW_CSV (was: $CURRENT_CSV)"
  echo "OLM is auto-upgrading..."
else
  echo "CSV version unchanged: $CURRENT_CSV"
  echo "Checking for newer component images in catalog..."

  # Get catalog operator image
  CATALOG_POD=$(oc get pod -n openshift-marketplace -l olm.catalogSource=odh-catalog -o name | head -1)
  CATALOG_OP=$(oc exec -n openshift-marketplace $CATALOG_POD -- \
    sh -c "grep -B1 'odh_rhel9_operator_image\|manager_image' /configs/opendatahub-operator/catalog.yaml 2>/dev/null | grep 'image:' | tail -1 | awk '{print \$3}'" 2>/dev/null || echo "")
  DEPLOYED_OP=$(oc get deployment opendatahub-operator-controller-manager -n openshift-operators \
    -o jsonpath='{.spec.template.spec.containers[0].image}' 2>/dev/null || echo "")

  if [[ -n "$CATALOG_OP" && "$DEPLOYED_OP" != "$CATALOG_OP" ]]; then
    echo "Newer component images found — performing forced reinstall..."

    SUB=$(oc get subscription opendatahub-operator -n openshift-operators \
      -o jsonpath='{.metadata.name}' 2>/dev/null)
    oc delete csv "$CURRENT_CSV" -n openshift-operators 2>&1 || true
    sleep 5
    oc delete subscription "$SUB" -n openshift-operators 2>&1 || true
    sleep 5

    cat << EOF | oc apply -f -
apiVersion: operators.coreos.com/v1alpha1
kind: Subscription
metadata:
  name: opendatahub-operator
  namespace: openshift-operators
spec:
  channel: ${CURRENT_CHANNEL}
  name: opendatahub-operator
  source: odh-catalog
  sourceNamespace: openshift-marketplace
  installPlanApproval: Automatic
EOF
    echo "Subscription recreated — waiting for new CSV..."
  else
    echo "All component images are up to date — no reinstall needed"
  fi
fi
```

### Step 6: Wait for CSV to Succeed

```bash
TIMEOUT=600
ELAPSED=0
CSV_PHASE=""

while [[ $ELAPSED -lt $TIMEOUT ]]; do
  CSV_LINE=$(oc get csv -n openshift-operators 2>/dev/null | grep opendatahub-operator | grep -v Replacing || echo "")
  if [[ -n "$CSV_LINE" ]]; then
    CSV_NAME=$(echo "$CSV_LINE" | awk '{print $1}')
    CSV_PHASE=$(echo "$CSV_LINE" | awk '{print $NF}')
    echo "CSV: $CSV_NAME, Phase: $CSV_PHASE"
    if [[ "$CSV_PHASE" == "Succeeded" ]]; then
      echo "ODH operator updated successfully"
      break
    fi
  fi
  sleep 10
  ELAPSED=$((ELAPSED + 10))
  echo "Waiting for CSV... (${ELAPSED}s/${TIMEOUT}s)"
done

[[ "$CSV_PHASE" == "Succeeded" ]] || echo "WARNING: CSV not yet Succeeded — check manually"
```

### Step 7: Verify DSC Still Ready

```bash
sleep 15
READY=$(oc get datasciencecluster default-dsc \
  -o jsonpath='{.status.conditions[?(@.type=="Ready")].status}' 2>/dev/null || echo "")

echo ""
echo "=== ODH Update Summary ==="
echo ""
echo "CSV:"
oc get csv -n openshift-operators | grep opendatahub-operator

echo ""
echo "Catalog image: $CATALOG_IMAGE"
echo "DSC Ready: ${READY:-Unknown}"

if [[ "$READY" != "True" ]]; then
  echo ""
  echo "DSC not yet Ready — not-ready components:"
  oc get datasciencecluster default-dsc \
    -o jsonpath='{range .status.conditions[*]}{.type}{": "}{.status}{" ("}{.reason}{")\n"}{end}' \
    2>/dev/null | grep -v "True\|Removed" || true
fi

echo ""
echo "ODH update complete!"
```

## Pulling the Latest Nightly Daily

Since `odh-stable-nightly` is rebuilt every day at midnight UTC, just re-run:

```bash
/odh-update
```

Or manually:
```bash
# Refresh catalog pod to pull latest nightly
oc delete pod -n openshift-marketplace -l olm.catalogSource=odh-catalog
```

OLM will detect the new CSV version and auto-upgrade within ~30 seconds.
