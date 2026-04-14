# /mirror-images - Mirror All Images from Connected Cluster to Disconnected Bastion Registries

## Purpose

Mirror all images required for a complete RHOAI deployment (operator, components, and infrastructure services) from a connected OpenShift cluster to one or more disconnected cluster bastion registries. This includes RHOAI operator and component images, FBC (File-Based Catalog) images, and all infrastructure images (databases, object storage, authentication, model serving runtimes, vector databases, etc.) so that a fresh disconnected cluster can be fully set up from scratch.

Runs the mirror job from a pod on the connected cluster for fast AWS-internal transfers.

## Prerequisites

- `oc` CLI installed and authenticated to the **connected** OpenShift cluster
- The connected cluster has RHOAI operator installed and running with all components deployed
- All infrastructure services (minio, keycloak, postgres, model serving, etc.) should be running on the connected cluster so their images can be captured
- Network access from the connected cluster to the bastion registries
- Bastion registry credentials (username/password) for each target registry

## Inputs

The user must provide (or you must ask for):

| Input | Description | Example |
|-------|-------------|---------|
| `BASTION_REGISTRIES` | Comma-separated list of bastion registry host:port | `bastion.ods-dis-rhoai-test.aws.rh-ods.com:8443` |
| `BASTION_USER` | Registry username for the bastions | `mir_reg` |
| `BASTION_PASSWORD` | Registry password for the bastions | (prompt securely) |
| `EXCLUDE_PATTERNS` | Optional image name patterns to skip (empty by default) | `spark,habana` |
| `EXTRA_NAMESPACES` | Optional additional namespaces to scan (beyond auto-detected) | `my-custom-ns` |

**Auto-detected (no user input needed):**

| Value | Source |
|-------|--------|
| `RHOAI_VERSION` | Extracted from the CSV version on the connected cluster (e.g., `rhods-operator.3.4.0` -> `3.4`) |
| `INFRA_NAMESPACES` | Auto-detected from running pods (minio, keycloak, milvus, evalhub, postgresql, llama-stack, llm-models, etc.) |

## Process

### Phase 1: Extract Complete Image List from Connected Cluster

The goal is to capture **every** image needed for a fully functional disconnected RHOAI deployment, organized into categories.

#### 1a. Get RHOAI CSV and detect version

```bash
CSV_NAME=$(oc get csv -n redhat-ods-operator -o name | grep rhods-operator)
RHOAI_VERSION=$(oc get "$CSV_NAME" -n redhat-ods-operator -o jsonpath='{.spec.version}' | grep -oE '^[0-9]+\.[0-9]+')
```

#### 1b. Extract relatedImages from RHOAI CSV

These are ALL images the operator references, including ones not currently running (workbenches, pipeline runtimes, training images, etc.). **Mirror all of them** — do NOT skip any by default.

```bash
oc get "$CSV_NAME" -n redhat-ods-operator -o jsonpath='{.spec.relatedImages[*]}' | jq -r '.[] | .image' | sort -u
```

**Registry Fallback for Nightly Images:** RHOAI nightly CSV references images as `registry.redhat.io/rhoai/...@sha256:...`, but these images often do NOT exist at `registry.redhat.io` — they only exist at `quay.io/rhoai/...`. Before mirroring, verify each `registry.redhat.io/rhoai/` image exists at the source. If it returns "manifest unknown" or "unauthorized", retry from `quay.io/rhoai/` with the same repo name and digest. Apply this fallback automatically in the mirror script:

```bash
# For each image from registry.redhat.io/rhoai/:
#   1. Try: oc image info registry.redhat.io/rhoai/IMAGE@sha256:DIGEST
#   2. If fails: try quay.io/rhoai/IMAGE@sha256:DIGEST
#   3. Use whichever source succeeds for the mirror operation
```

#### 1c. Extract images from ALL relevant running pods

Scan all namespaces for running pod images. Include both containers and initContainers. Do NOT filter by rhoai/rhods/odh — capture everything except core OpenShift platform images (`openshift-*`, `kube-*` namespaces) and GPU operator images (`nvcr.io/nvidia`).

```bash
# Get all images from non-platform namespaces
oc get pods --all-namespaces -o jsonpath='{range .items[*]}{.metadata.namespace}{"\t"}{range .spec.containers[*]}{.image}{"\n"}{end}{range .spec.initContainers[*]}{.image}{"\n"}{end}{end}' \
  | grep -vE '^(openshift-|kube-)' \
  | awk '{print $NF}' \
  | sort -u
```

This captures infrastructure images from namespaces like:

| Namespace | Images Captured |
|-----------|----------------|
| `redhat-ods-operator` | RHOAI operator |
| `redhat-ods-applications` | All RHOAI component operators and controllers |
| `minio` | MinIO object storage (`quay.io/minio/minio`) |
| `keycloak` | Red Hat Build of Keycloak server and operator (`registry.redhat.io/rhbk/keycloak-rhel9`, `keycloak-rhel9-operator`) |
| `evalhub` | EvalHub server and PostgreSQL (`odh-eval-hub-rhel9`, `postgresql-15`) |
| `postgresql` | Standalone PostgreSQL instances (`postgresql-15`, `postgresql-16`) |
| `llama-stack` | LlamaStack core runtime (`odh-llama-stack-core-rhel9`) |
| `llm-models` | vLLM serving runtime (`vllm-cuda-rhel9`), model download jobs |
| `milvus` | Milvus vector database (`milvusdb/milvus`) |
| `ai-pipelines`, `test`, `zj` | DSP pipeline components, MariaDB (`mariadb-105`), Argo workflow controller, service mesh proxy |
| `cert-manager` | Cert-manager and operator |
| `kuadrant-system` | Authorino, Limitador, DNS operators (API gateway) |
| `rhoai-model-registries` | Model registry and its PostgreSQL |
| `tenant` | TrustyAI LMEval job runner |

#### 1d. Extract images from CatalogSources

```bash
oc get catalogsource --all-namespaces -o jsonpath='{range .items[*]}{.spec.image}{"\n"}{end}' | sort -u
```

#### 1e. Extract images from RHOAI Dashboard config (module architecture images)

These are images referenced by the Dashboard for model arch features (AutoML, AutoRAG, EvalHub, GenAI, MaaS, MLflow, Model Registry). They appear as running pods on the connected cluster but are important to capture explicitly:

```bash
# These are typically in the CSV relatedImages but verify by checking running mod-arch pods
oc get pods --all-namespaces -o jsonpath='{range .items[*]}{range .spec.containers[*]}{.image}{"\n"}{end}{end}' | grep 'mod-arch' | sort -u
```

#### 1f. Merge and deduplicate

Combine all image lists from 1b, 1c, 1d, and 1e. Deduplicate by full image reference (registry/repo@digest). For each image, extract:
- Source registry (e.g., `registry.redhat.io/rhoai/`, `quay.io/minio/`, `milvusdb/`)
- Repository name (e.g., `odh-dashboard-rhel9`, `minio`, `milvus`)
- Digest (`sha256:...`) or tag

#### 1g. Apply exclusion filters (only if user specified)

Only remove images matching user-provided `EXCLUDE_PATTERNS`. **No images are excluded by default.**

#### 1h. Check for images already on bastion (skip duplicates)

Before mirroring, check each image against the bastion to avoid re-mirroring images that already exist. This significantly speeds up incremental mirrors (e.g., when only a few images changed in a nightly build):

```bash
# For each image, compute the bastion destination path and check if it exists:
BASTION_DEST="${BASTION}/${DEST_REPO}@${DIGEST}"
if oc image info "$BASTION_DEST" --insecure=true -a "$PULL_SECRET" &>/dev/null; then
  echo "SKIP (already on bastion): $BASTION_DEST"
  SKIPPED_COUNT=$((SKIPPED_COUNT + 1))
  continue
fi
```

Report the skip count in the summary. This check adds ~1-2 seconds per image but can save hours of mirroring for unchanged images.

#### 1i. Filter out images that don't need mirroring

Skip images that:
- Are already on the bastion registry (`bastion.*:8443/`)
- Are from `nvcr.io/nvidia` (GPU operator images managed separately)
- Are from `quay.io/openshift-release-dev` (OCP platform images managed by OCP mirroring)

#### 1j. Save the image list

Save to `artifacts/rhoai-manager/mirror-images-{version}.txt` with format:

```text
# RHOAI Operator and Components
registry.redhat.io/rhoai/odh-rhel9-operator@sha256:abc123...
registry.redhat.io/rhoai/odh-dashboard-rhel9@sha256:def456...
...

# Infrastructure: Databases
registry.redhat.io/rhel9/mariadb-105@sha256:...
registry.redhat.io/rhel9/postgresql-15@sha256:...
registry.redhat.io/rhel9/postgresql-16@sha256:...

# Infrastructure: Object Storage
quay.io/minio/minio@sha256:...

# Infrastructure: Authentication
registry.redhat.io/rhbk/keycloak-rhel9@sha256:...
registry.redhat.io/rhbk/keycloak-rhel9-operator@sha256:...

# Infrastructure: Model Serving
registry.redhat.io/rhaii-early-access/vllm-cuda-rhel9@sha256:...

# Infrastructure: Vector Database
milvusdb/milvus@sha256:...

# Infrastructure: Service Mesh
registry.redhat.io/openshift-service-mesh/proxyv2-rhel9@sha256:...

# Infrastructure: Cert Manager
registry.redhat.io/cert-manager/jetstack-cert-manager-rhel9@sha256:...

# Infrastructure: API Gateway (Kuadrant)
registry.redhat.io/rhcl-1/authorino-rhel9@sha256:...

# FBC Catalog
quay.io/rhoai/rhoai-fbc-fragment@sha256:...

# Base Images
registry.redhat.io/ubi9/nginx-126@sha256:...
```

Print a summary showing the count of images per category.

### Phase 2: Build Combined Pull Secret

1. **Get the connected cluster's pull secret**

   ```bash
   oc get secret/pull-secret -n openshift-config -o jsonpath='{.data.\.dockerconfigjson}' | base64 -d > /tmp/cluster-pull-secret.json
   ```

2. **Add bastion registry credentials** — merge each bastion auth into the pull secret:

   ```bash
   # Generate base64 auth for bastions
   BASTION_AUTH=$(printf '%s:%s' "$BASTION_USER" "$BASTION_PASSWORD" | base64 | tr -d '\n')
   ```

   Use `jq` to merge all bastion auths into `.auths`:

   ```bash
   # Build jq expression dynamically for each bastion
   JQ_EXPR='.'
   for BASTION in ${BASTION_REGISTRIES//,/ }; do
     JQ_EXPR="$JQ_EXPR | .auths[\"$BASTION\"] = {\"auth\": \"$BASTION_AUTH\"}"
   done
   jq "$JQ_EXPR" /tmp/cluster-pull-secret.json > /tmp/combined-pull-secret.json
   ```

3. **Add auth for third-party registries** that may require authentication (docker.io, quay.io):

   If the connected cluster's pull secret already has auth for these registries, it will be included automatically. If images from registries like `docker.io` or `milvusdb` (Docker Hub) need mirroring, the pull secret must include Docker Hub credentials. Check and warn if missing.

4. **Create the secret in the mirror namespace**

   ```bash
   oc new-project image-mirror 2>/dev/null || true
   oc delete secret mirror-pull-secret -n image-mirror 2>/dev/null || true
   oc create secret generic mirror-pull-secret \
     --from-file=auth.json=/tmp/combined-pull-secret.json \
     -n image-mirror
   ```

5. **Clean up local temp files**

   ```bash
   rm -f /tmp/cluster-pull-secret.json /tmp/combined-pull-secret.json
   ```

### Phase 3: Generate Mirror Script

Generate a bash script that mirrors all images. The script must:

- Accept the pull secret path and bastion hostnames as arguments
- For each image in the list:
  - Determine the source reference (`registry/repo@digest` or `registry/repo:tag`)
  - Compute the destination path based on the source registry:
    - `registry.redhat.io/rhoai/foo` -> `BASTION/rhoai/foo`
    - `quay.io/minio/minio` -> `BASTION/minio/minio`
    - `registry.redhat.io/rhbk/foo` -> `BASTION/rhbk/foo`
    - `registry.redhat.io/rhel9/foo` -> `BASTION/rhel9/foo`
    - `milvusdb/milvus` -> `BASTION/milvusdb/milvus` (Docker Hub library)
    - `quay.io/opendatahub/foo` -> `BASTION/opendatahub/foo`
    - `docker.io/library/foo` -> `BASTION/library/foo`
  - Mirror to all bastion registries with retries (3 attempts per image)
  - Use `oc image mirror` with these critical flags:
    - `--keep-manifest-list=true` -- preserves manifest list digests referenced by the CSV
    - `--filter-by-os=".*"` -- mirrors all architectures (prevents manifest list stripping)
    - `--insecure=true` -- bastion registries use self-signed certs
    - `-a "$PULL_SECRET"` -- combined auth file
  - Tag destination as `:latest` to prevent Quay tagless manifest garbage collection
  - Verify each mirror with `oc image info`
  - Handle images with tags (not digests) by using `skopeo copy` as fallback if `oc image mirror` fails
- Track and report: verified count, failed count, skipped count, per category
- Print a summary at the end with per-category breakdown

**Mirror command pattern per image:**

```bash
# For digest-referenced images
oc image mirror \
  "${SOURCE_REGISTRY}/${REPO}@${DIGEST}" \
  "${BASTION}/${DEST_REPO}:latest" \
  --insecure=true \
  -a "$PULL_SECRET" \
  --keep-manifest-list=true \
  --filter-by-os=".*"

# For tag-referenced images (e.g., milvusdb/milvus:v2.5.4)
oc image mirror \
  "${SOURCE_IMAGE}" \
  "${BASTION}/${DEST_REPO}:${TAG}" \
  --insecure=true \
  -a "$PULL_SECRET" \
  --keep-manifest-list=true \
  --filter-by-os=".*"
```

**Verification command per image:**

```bash
oc image info "${BASTION}/${DEST_REPO}:latest" --insecure=true -a "$PULL_SECRET"
```

### Phase 4: Deploy Mirror Pod

1. **Create ConfigMap from the mirror script**

   ```bash
   oc delete configmap mirror-script -n image-mirror 2>/dev/null || true
   oc create configmap mirror-script \
     --from-file=mirror.sh=/tmp/mirror-script.sh \
     -n image-mirror
   ```

2. **Create the mirror pod** using this manifest:

   ```yaml
   apiVersion: v1
   kind: Pod
   metadata:
     name: image-mirror
     namespace: image-mirror
   spec:
     restartPolicy: Never
     activeDeadlineSeconds: 14400
     containers:
     - name: mirror
       image: registry.redhat.io/openshift4/ose-cli-rhel9:latest
       command: ["/bin/bash", "/scripts/mirror.sh"]
       volumeMounts:
       - name: auth
         mountPath: /auth
         readOnly: true
       - name: script
         mountPath: /scripts
         readOnly: true
       resources:
         requests:
           memory: "512Mi"
           cpu: "500m"
         limits:
           memory: "2Gi"
           cpu: "2"
     volumes:
     - name: auth
       secret:
         secretName: mirror-pull-secret
     - name: script
       configMap:
         name: mirror-script
         defaultMode: 0755
   ```

3. **Apply the pod manifest**

   ```bash
   oc delete pod image-mirror -n image-mirror 2>/dev/null || true
   oc apply -f /tmp/mirror-pod.yaml
   ```

### Phase 5: Monitor and Verify

1. **Wait for the pod to start**

   ```bash
   oc wait --for=condition=Ready pod/image-mirror -n image-mirror --timeout=120s
   ```

2. **Stream logs** periodically to check progress:

   ```bash
   oc logs image-mirror -n image-mirror --tail=50
   ```

3. **Check at intervals** (every 10-15 minutes) until the pod completes:

   ```bash
   oc get pod image-mirror -n image-mirror -o jsonpath='{.status.phase}'
   ```

4. **When the pod finishes**, retrieve the full log and parse the summary:

   ```bash
   oc logs image-mirror -n image-mirror > artifacts/rhoai-manager/mirror-log-{version}.txt
   ```

5. **If any images failed**, report them by category and offer to create a retry script with only the failed images.

### Phase 5b: Generate IDMS YAML

After mirroring completes, generate the ImageDigestMirrorSet YAML from the list of source registries that were mirrored. This YAML must be applied to the disconnected cluster so it knows to pull from the bastion instead of the original source.

```bash
# Extract unique source registry prefixes from the mirrored image list
# Group by registry/namespace (e.g., registry.redhat.io/rhoai, quay.io/minio, milvusdb)
SOURCE_PREFIXES=$(cat mirror-images-list.txt | grep -v '^#' | grep -v '^$' \
  | sed -E 's|^([^/]+/[^/@]+).*|\1|' | sort -u)

# Generate IDMS YAML
cat > artifacts/rhoai-manager/mirror-idms-${RHOAI_VERSION}.yaml << 'HEADER'
apiVersion: config.openshift.io/v1
kind: ImageDigestMirrorSet
metadata:
  name: rhoai-mirror
spec:
  imageDigestMirrors:
HEADER

for prefix in $SOURCE_PREFIXES; do
  # Compute bastion mirror path (strip registry hostname)
  MIRROR_PATH=$(echo "$prefix" | sed -E 's|^[^/]+/||')
  cat >> artifacts/rhoai-manager/mirror-idms-${RHOAI_VERSION}.yaml << EOF
  - source: $prefix
    mirrors:
    - ${BASTION}/${MIRROR_PATH}
    mirrorSourcePolicy: NeverContactSource
EOF
done

echo "IDMS YAML saved to: artifacts/rhoai-manager/mirror-idms-${RHOAI_VERSION}.yaml"
echo "Apply to disconnected cluster: oc apply -f artifacts/rhoai-manager/mirror-idms-${RHOAI_VERSION}.yaml"
```

**Important:** For Docker Hub images without an explicit registry (e.g., `milvusdb/milvus`), the IDMS source should use the full Docker Hub URL: `docker.io/milvusdb`. For images under `docker.io/library/`, use `docker.io/library`.

### Phase 6: Cleanup

After successful verification:

```bash
oc delete pod image-mirror -n image-mirror
oc delete configmap mirror-script -n image-mirror
oc delete secret mirror-pull-secret -n image-mirror
oc delete project image-mirror
```

Clean up any local temp files.

## Image Categories Reference

The following table lists all image categories that must be mirrored for a complete disconnected RHOAI deployment:

| Category | Source Registry | Example Images | Notes |
|----------|----------------|----------------|-------|
| RHOAI Operator | `registry.redhat.io/rhoai/` | `odh-rhel9-operator`, `odh-operator-bundle` | Core operator |
| RHOAI Components | `registry.redhat.io/rhoai/` | `odh-dashboard-rhel9`, `odh-kserve-controller-rhel9`, `odh-notebook-controller-rhel9`, all `odh-*` images | All CSV relatedImages |
| FBC Catalog | `quay.io/rhoai/` or `quay.io/modh/` | `rhoai-fbc-fragment`, `rhoai-catalog` | OLM catalog source |
| Module Architecture | `registry.redhat.io/rhoai/` | `odh-mod-arch-automl-rhel9`, `odh-mod-arch-autorag-rhel9`, `odh-mod-arch-eval-hub-rhel9`, `odh-mod-arch-gen-ai-rhel9`, `odh-mod-arch-maas-rhel9`, `odh-mod-arch-mlflow-rhel9`, `odh-mod-arch-model-registry-rhel9` | Dashboard module images |
| Model Serving Runtime | `registry.redhat.io/rhaii-early-access/` | `vllm-cuda-rhel9` | vLLM CUDA runtime |
| LlamaStack | `registry.redhat.io/rhoai/` | `odh-llama-stack-core-rhel9`, `odh-llama-stack-k8s-operator-rhel9` | LLM orchestration |
| EvalHub | `registry.redhat.io/rhoai/` | `odh-eval-hub-rhel9`, `odh-ta-lmes-job-rhel9` | Evaluation hub + LMEval job |
| TrustyAI | `registry.redhat.io/rhoai/` | `odh-trustyai-service-operator-rhel9` | AI explainability |
| MariaDB | `registry.redhat.io/rhel9/` | `mariadb-105` | DSP metadata store |
| PostgreSQL | `registry.redhat.io/rhel9/` | `postgresql-15`, `postgresql-16` | EvalHub, Model Registry DBs |
| MinIO | `quay.io/minio/` | `minio` | S3-compatible object storage |
| Keycloak | `registry.redhat.io/rhbk/` | `keycloak-rhel9`, `keycloak-rhel9-operator` | Authentication (LlamaStack, etc.) |
| Milvus | `milvusdb/` (Docker Hub) | `milvus` | Vector database for RAG |
| Service Mesh | `registry.redhat.io/openshift-service-mesh/` | `proxyv2-rhel9`, `istio-pilot-rhel9`, `istio-proxyv2-rhel9`, `istio-rhel9-operator` | Envoy sidecar for pipelines |
| Cert Manager | `registry.redhat.io/cert-manager/` | `jetstack-cert-manager-rhel9`, `cert-manager-operator-rhel9` | TLS certificate management |
| Kuadrant/API Gateway | `registry.redhat.io/rhcl-1/` | `authorino-rhel9`, `limitador-rhel9`, `rhcl-rhel9-operator`, `rhcl-console-plugin-rhel9`, `dns-rhel9-operator` | API auth and rate limiting |
| Model Registry | `registry.redhat.io/rhoai/` | `odh-model-registry-rhel9`, `odh-model-registry-operator-rhel9` | ML model registry |
| DSP Components | `registry.redhat.io/rhoai/` | `odh-ml-pipelines-api-server-v2-rhel9`, `odh-ml-pipelines-persistenceagent-v2-rhel9`, `odh-ml-pipelines-scheduledworkflow-v2-rhel9`, `odh-mlmd-grpc-server-rhel9`, `odh-data-science-pipelines-argo-workflowcontroller-rhel9` | Data Science Pipelines |
| Base Images | `registry.redhat.io/ubi9/` | `nginx-126` | Dashboard web server |
| ODH Components | `quay.io/opendatahub/` | `odh-model-controller` | Upstream ODH images |
| Kube Auth Proxy | `registry.redhat.io/rhoai/` | `odh-kube-auth-proxy-rhel9` | Auth proxy for RHOAI services |
| Metadata/Perf | `registry.redhat.io/rhoai/` | `odh-model-metadata-collection-rhel9`, `odh-model-performance-data-rhel9` | Telemetry images |

## Important Notes

- **Why pod-based mirroring**: Running `oc image mirror` from a pod on the connected AWS cluster uses AWS internal networking (40-116 MB/s) instead of local internet (~2 MB/s). This eliminates connection drops on large blob uploads (some RHOAI images are 5-7 GB).
- **Why `:latest` tag**: Quay garbage-collects manifests that have no tags. Even though clusters pull by digest, pushing with `:latest` prevents GC from removing the manifests.
- **Why `--filter-by-os=".*"`**: Using `--filter-by-os=linux/amd64` strips the manifest list and replaces it with a single-arch manifest. The CSV references the manifest list digest, so this would break image resolution. `".*"` preserves the full manifest list.
- **Why `--keep-manifest-list=true`**: Ensures the manifest list is pushed as-is to the destination, preserving the exact digest the CSV references.
- **Why mirror ALL CSV relatedImages**: Previously, workbench, training, pipeline-runtime, and spark images were excluded by default. This caused failures when users tried to create workbenches or run training jobs on the disconnected cluster. Mirror everything by default.
- **Docker Hub images (milvusdb)**: These images may require Docker Hub credentials in the pull secret. The connected cluster may or may not have these. If `oc image mirror` fails for Docker Hub images, the script should warn and continue, reporting them as needing manual attention.
- **Tag-based images**: Some images (e.g., `milvusdb/milvus:v2.5.4`, `quay.io/opendatahub/odh-model-controller:odh-model-serving-api-stable`) use tags instead of digest references. These need special handling since `--keep-manifest-list` may not apply. Mirror them with the original tag preserved.
- **Large images**: Some RHOAI images (automl ~5.5GB, autorag ~7.2GB, ta-lmes-job ~6.7GB, vllm-cuda ~8GB) take 5-15 minutes each. The 4-hour `activeDeadlineSeconds` on the pod accommodates this.
- **IDMS requirements**: After mirroring, the disconnected cluster needs ImageDigestMirrorSet entries for all source registries. Registries commonly needing IDMS entries: `registry.redhat.io/rhoai`, `registry.redhat.io/rhbk`, `registry.redhat.io/rhel9`, `registry.redhat.io/rhcl-1`, `registry.redhat.io/cert-manager`, `quay.io/minio`, `quay.io/opendatahub`, `milvusdb` (Docker Hub). The mirror script should output the required IDMS YAML for any registries that were mirrored.

## Output

- `artifacts/rhoai-manager/mirror-images-{version}.txt` -- categorized image list extracted from the connected cluster
- `artifacts/rhoai-manager/mirror-log-{version}.txt` -- complete mirror pod log with verification results
- `artifacts/rhoai-manager/mirror-idms-{version}.yaml` -- ImageDigestMirrorSet YAML for the disconnected cluster (generated from the mirrored image list)

## Summary Display

After mirroring completes, display a summary table to the user in this format:

```
**RHOAI v{version} Image Mirror — Complete**

| Metric | Value |
|--------|-------|
| Total images | {total} |
| Verified | {verified} |
| Skipped (already on bastion) | {skipped} |
| Failed | {failed} |
| Duration | {duration} |
| Target | `{bastion_registry}` |

**Image Breakdown:**

| Category | Count |
|----------|-------|
| RHOAI Operator and Components | {count} |
| Model Serving Runtimes (vLLM) | {count} |
| Infrastructure Dependencies | {count} |
| FBC Catalog | {count} |
| Base Images | {count} |

**Artifacts saved:**
- `artifacts/rhoai-manager/mirror-images-{version}.txt` — categorized image list
- `artifacts/rhoai-manager/mirror-log-{version}.txt` — full mirror log ({line_count} lines)
- `artifacts/rhoai-manager/mirror-idms-{version}.yaml` — ImageDigestMirrorSet YAML for disconnected cluster

**Next step:** Apply the IDMS on the disconnected cluster:
oc apply -f artifacts/rhoai-manager/mirror-idms-{version}.yaml
```

If any images failed, append a **Failed Images** section listing them by category with their full image references.
