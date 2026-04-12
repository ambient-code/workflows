# /mirror-images - Mirror RHOAI Images to Disconnected Bastion Registries

## Purpose

Copy all RHOAI operator, FBC (File-Based Catalog), and component images deployed on a connected OpenShift cluster to both disconnected cluster bastion registries. Runs the mirror job from a pod on the connected cluster for fast AWS-internal transfers.

## Prerequisites

- `oc` CLI installed and authenticated to the **connected** OpenShift cluster
- The connected cluster has RHOAI operator installed and running
- Network access from the connected cluster to both bastion registries
- Bastion registry credentials (username/password) for both disconnected clusters

## Inputs

The user must provide (or you must ask for):

| Input | Description | Example |
|-------|-------------|---------|
| `PIPELINE_BASTION` | Bastion registry host:port for the pipeline cluster | `bastion.ods-dis-pipeline.aws.rh-ods.com:8443` |
| `RHOAI_TEST_BASTION` | Bastion registry host:port for the rhoai-test cluster | `bastion.ods-dis-rhoai-test.aws.rh-ods.com:8443` |
| `BASTION_USER` | Registry username for both bastions | `mir_reg` |
| `BASTION_PASSWORD` | Registry password for both bastions | (prompt securely) |
| `RHOAI_VERSION` | RHOAI version label (for naming) | `3.4` |
| `EXCLUDE_PATTERNS` | Optional image name patterns to skip | `workbench,training,pipeline-runtime,spark` |

## Process

### Phase 1: Extract Image List from Connected Cluster

1. **Get RHOAI CSV (ClusterServiceVersion)**

   ```bash
   CSV_NAME=$(oc get csv -n redhat-ods-operator -o name | grep rhods-operator)
   ```

2. **Extract relatedImages from CSV**

   ```bash
   oc get "$CSV_NAME" -n redhat-ods-operator -o jsonpath='{.spec.relatedImages[*]}' | jq -r '.[] | "\(.name) \(.image)"'
   ```

3. **Extract images from running pods**

   ```bash
   oc get pods --all-namespaces -o jsonpath='{range .items[*]}{range .spec.containers[*]}{.image}{"\n"}{end}{range .spec.initContainers[*]}{.image}{"\n"}{end}{end}' | grep -E '(rhoai|rhods|odh)' | sort -u
   ```

4. **Merge and deduplicate** the two lists. For each image, extract:
   - Source registry (e.g., `quay.io/rhoai/` or `registry.redhat.io/`)
   - Repository name (e.g., `odh-dashboard-rhel9`)
   - Digest (`sha256:...`)

5. **Apply exclusion filters** — remove images matching `EXCLUDE_PATTERNS`

6. **Save the image list** to `artifacts/rhoai-manager/mirror-images-{version}.txt` with format:

   ```text
   quay.io/rhoai/odh-dashboard-rhel9@sha256:abc123...
   quay.io/rhoai/odh-model-controller-rhel9@sha256:def456...
   ```

### Phase 2: Build Combined Pull Secret

1. **Get the connected cluster's pull secret**

   ```bash
   oc get secret/pull-secret -n openshift-config -o jsonpath='{.data.\.dockerconfigjson}' | base64 -d > /tmp/cluster-pull-secret.json
   ```

2. **Add bastion registry credentials** — merge both bastion auths into the pull secret:

   ```bash
   # Generate base64 auth for bastions
   BASTION_AUTH=$(printf '%s:%s' "$BASTION_USER" "$BASTION_PASSWORD" | base64 | tr -d '\n')
   ```

   Use `jq` to merge the bastion auths into `.auths`:

   ```bash
   jq --arg pipeline "$PIPELINE_BASTION" \
      --arg rhoaitest "$RHOAI_TEST_BASTION" \
      --arg auth "$BASTION_AUTH" \
      '.auths[$pipeline] = {"auth": $auth} | .auths[$rhoaitest] = {"auth": $auth}' \
      /tmp/cluster-pull-secret.json > /tmp/combined-pull-secret.json
   ```

3. **Create the secret in the mirror namespace**

   ```bash
   oc new-project image-mirror 2>/dev/null || true
   oc delete secret mirror-pull-secret -n image-mirror 2>/dev/null || true
   oc create secret generic mirror-pull-secret \
     --from-file=auth.json=/tmp/combined-pull-secret.json \
     -n image-mirror
   ```

4. **Clean up local temp files**

   ```bash
   rm -f /tmp/cluster-pull-secret.json /tmp/combined-pull-secret.json
   ```

### Phase 3: Generate Mirror Script

Generate a bash script that mirrors all images. The script must:

- Accept the pull secret path, and both bastion hostnames
- For each image in the list:
  - Determine the source reference (`registry/repo@digest`)
  - Mirror to both bastions with retries (3 attempts)
  - Use `oc image mirror` with these critical flags:
    - `--keep-manifest-list=true` — preserves manifest list digests referenced by the CSV
    - `--filter-by-os=".*"` — mirrors all architectures (prevents manifest list stripping)
    - `--insecure=true` — bastion registries use self-signed certs
    - `-a "$PULL_SECRET"` — combined auth file
  - Tag destination as `:latest` to prevent Quay tagless manifest garbage collection
  - Verify each mirror with `oc image info`
- Track and report: verified count, failed count, skipped count
- Print a summary at the end

**Mirror command pattern per image:**

```bash
oc image mirror \
  "${SOURCE_REGISTRY}/${REPO}@${DIGEST}" \
  "${BASTION}/${REPO}:latest" \
  --insecure=true \
  -a "$PULL_SECRET" \
  --keep-manifest-list=true \
  --filter-by-os=".*"
```

**Verification command per image:**

```bash
oc image info "${BASTION}/${REPO}:latest" --insecure=true -a "$PULL_SECRET"
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

5. **If any images failed**, report them and offer to create a retry script with only the failed images.

### Phase 6: Cleanup

After successful verification:

```bash
oc delete pod image-mirror -n image-mirror
oc delete configmap mirror-script -n image-mirror
oc delete secret mirror-pull-secret -n image-mirror
oc delete project image-mirror
```

Clean up any local temp files.

## Important Notes

- **Why pod-based mirroring**: Running `oc image mirror` from a pod on the connected AWS cluster uses AWS internal networking (40-116 MB/s) instead of local internet (~2 MB/s). This eliminates connection drops on large blob uploads (some RHOAI images are 5-7 GB).
- **Why `:latest` tag**: Quay garbage-collects manifests that have no tags. Even though clusters pull by digest, pushing with `:latest` prevents GC from removing the manifests.
- **Why `--filter-by-os=".*"`**: Using `--filter-by-os=linux/amd64` strips the manifest list and replaces it with a single-arch manifest. The CSV references the manifest list digest, so this would break image resolution. `".*"` preserves the full manifest list.
- **Why `--keep-manifest-list=true`**: Ensures the manifest list is pushed as-is to the destination, preserving the exact digest the CSV references.
- **Large images**: Some RHOAI images (automl ~5.5GB, autorag ~7.2GB, ta-lmes-job ~6.7GB) take 5-15 minutes each. The 4-hour `activeDeadlineSeconds` on the pod accommodates this.

## Output

- `artifacts/rhoai-manager/mirror-images-{version}.txt` — full image list extracted from the connected cluster
- `artifacts/rhoai-manager/mirror-log-{version}.txt` — complete mirror pod log with verification results
