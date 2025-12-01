# ACP Interactive Pod Support - Design Proposal

**Gitpod-like browser IDE access for ACP session workspaces**

## Executive Summary

Add browser-based IDE support to ACP using **sidecar containers** with OpenVSCode Server and OpenShift OAuth. Enables zero-install development environments with enterprise SSO and pre-configured tooling.

**Phase 1 (4 weeks):** Browser IDE + Pre-configured environments + OAuth SSO
**Phase 2 (Future):** Port forwarding + Workspace snapshots

---

## Architecture

### Sidecar Pattern

```
Session Pod
├─ claude-runner (existing)
├─ openvscode-server (IDE)
└─ oauth-proxy (auth)
   ↓
Shared workspace PVC
```

### Core Components

1. **CRD Enhancement** - `spec.ideEnabled` triggers IDE injection
2. **Operator** - Reconciles IDE sidecars, Services, Routes
3. **Backend API** - `/api/.../sessions/{id}/ide` endpoints
4. **Frontend** - "Open IDE" button in session detail

---

## Implementation

### 1. CRD Schema

**File:** `components/operator/api/v1/agenticsession_types.go`

```go
type AgenticSessionSpec struct {
    // ... existing fields ...

    IDEEnabled bool        `json:"ideEnabled,omitempty"`
    IDEConfig  *IDEConfig  `json:"ideConfig,omitempty"`
}

type IDEConfig struct {
    Image      string                       `json:"image,omitempty"`
    Extensions []string                     `json:"extensions,omitempty"`
    Resources  corev1.ResourceRequirements  `json:"resources,omitempty"`
}

type AgenticSessionStatus struct {
    // ... existing fields ...

    IDEURL     string  `json:"ideURL,omitempty"`
    IDEPhase   string  `json:"idePhase,omitempty"`  // Pending|Starting|Ready|Failed
    IDEMessage string  `json:"ideMessage,omitempty"`
}
```

### 2. Container Specs

**IDE Sidecar:**
```yaml
- name: openvscode-server
  image: quay.io/redhat-acp/openvscode-server-bundle:latest
  ports:
    - containerPort: 8080
      name: ide
  env:
    - name: OPENVSCODE_SERVER_ROOT
      value: /workspace/sessions/{{ .session.name }}
  volumeMounts:
    - name: workspace
      mountPath: /workspace
  resources:
    requests: {memory: "512Mi", cpu: "200m"}
    limits: {memory: "2Gi", cpu: "2000m"}
```

**OAuth Proxy Sidecar:**
```yaml
- name: oauth-proxy
  image: quay.io/openshift/origin-oauth-proxy:latest
  ports:
    - containerPort: 8443
      name: https
  args:
    - --provider=openshift
    - --https-address=:8443
    - --upstream=http://localhost:8080
    - --tls-cert=/etc/tls/private/tls.crt
    - --tls-key=/etc/tls/private/tls.key
    - --cookie-secret-file=/etc/proxy/secrets/session_secret
    - --openshift-service-account={{ .session.name }}-ide
    - --skip-auth-regex=^/healthz
  volumeMounts:
    - {name: proxy-tls, mountPath: /etc/tls/private}
    - {name: proxy-secret, mountPath: /etc/proxy/secrets}
  resources:
    requests: {memory: "128Mi", cpu: "50m"}
    limits: {memory: "256Mi", cpu: "200m"}
```

### 3. Operator Reconciliation

**File:** `components/operator/controllers/agenticsession_controller.go`

**Key Logic:**
1. **Try in-place pod update** (zero downtime)
2. **Fallback to graceful recreation** if update fails
3. **Create ServiceAccount** with OAuth redirect annotation
4. **Create Service** with TLS cert annotation (auto-generates cert)
5. **Create Route** with reencrypt termination
6. **Update status** with IDE URL

**Pod Update Strategy:**
```go
if !hasIDEContainer {
    pod.Spec.Containers = append(pod.Spec.Containers, ideContainer, oauthContainer)
    pod.Spec.Volumes = append(pod.Spec.Volumes, tlsVolume, secretVolume)

    if err := r.Client.Update(ctx, pod); err != nil {
        // Fallback: graceful recreation
        r.updateIDEStatus(ctx, session, "Recreating", "Pod restart required", "")
        r.Client.Delete(ctx, pod)  // ReplicaSet recreates
        return fmt.Errorf("requeueing after pod recreation")
    }
}
```

**ServiceAccount:**
```go
sa := &corev1.ServiceAccount{
    ObjectMeta: metav1.ObjectMeta{
        Name: fmt.Sprintf("%s-ide", session.Name),
        Annotations: map[string]string{
            "serviceaccounts.openshift.io/oauth-redirectreference.ide":
                `{"kind":"OAuthRedirectReference","reference":{"kind":"Route","name":"SESSION-ide"}}`,
        },
        OwnerReferences: []metav1.OwnerReference{
            *metav1.NewControllerRef(session, v1.GroupVersion.WithKind("AgenticSession")),
        },
    },
}
```

**Service with TLS:**
```go
service := &corev1.Service{
    ObjectMeta: metav1.ObjectMeta{
        Annotations: map[string]string{
            "service.alpha.openshift.io/serving-cert-secret-name": fmt.Sprintf("%s-ide-tls", session.Name),
        },
    },
    Spec: corev1.ServiceSpec{
        Ports: []corev1.ServicePort{{Name: "https", Port: 8443, TargetPort: intstr.FromInt(8443)}},
    },
}
```

**Route:**
```go
route := &routev1.Route{
    Spec: routev1.RouteSpec{
        TLS: &routev1.TLSConfig{
            Termination: routev1.TLSTerminationReencrypt,
            InsecureEdgeTerminationPolicy: routev1.InsecureEdgeTerminationPolicyRedirect,
        },
    },
}
```

### 4. Backend API

**File:** `components/backend/pkg/handlers/ide.go`

```go
// POST /api/projects/{project}/agentic-sessions/{session}/ide
func EnableIDEForSession(c *gin.Context) {
    clients, _ := middleware.GetK8sClientsForRequest(c)  // RBAC enforcement
    session, _ := fetchSession(clients, project, sessionName)

    session.Spec.IDEEnabled = true
    clients.DynamicClient.Update(ctx, session)

    // Poll for status.ideURL (operator reconciles)
    ideURL := waitForIDEReady(clients, session)

    c.JSON(http.StatusOK, gin.H{"ideURL": ideURL, "phase": session.Status.IDEPhase})
}

// GET /api/projects/{project}/agentic-sessions/{session}/ide
func GetIDEStatus(c *gin.Context) { /* return status */ }

// DELETE /api/projects/{project}/agentic-sessions/{session}/ide
func DisableIDEForSession(c *gin.Context) { /* set ideEnabled=false */ }
```

### 5. Workflow IDE Configuration

**File:** `.ambient/ide.json` in workflow repos

```json
{
  "vscode": {
    "extensions": [
      "redhat.vscode-yaml",
      "ms-python.python",
      "golang.go"
    ],
    "settings": {
      "editor.formatOnSave": true,
      "python.linting.enabled": true
    },
    "tasks": [
      {"label": "Run Tests", "type": "shell", "command": "make test"}
    ]
  },
  "startup": {
    "openFiles": ["README.md", "CLAUDE.md"]
  }
}
```

**File:** `components/runners/claude-code-runner/workflow_loader.py`

```python
def apply_ide_configuration(workspace_path: str, workflow_path: str):
    ide_config_path = os.path.join(workflow_path, '.ambient', 'ide.json')
    if not os.path.exists(ide_config_path):
        return

    with open(ide_config_path) as f:
        ide_config = json.load(f)

    vscode_dir = os.path.join(workspace_path, '.vscode')
    os.makedirs(vscode_dir, exist_ok=True)

    if 'vscode' in ide_config:
        # Write settings.json, extensions.json, tasks.json
        write_vscode_configs(vscode_dir, ide_config['vscode'])
```

### 6. Frontend UI

**File:** `components/frontend/src/components/sessions/SessionDetail.tsx`

```tsx
function IDEAccessButton({ session }: { session: AgenticSession }) {
  const [ideStatus, setIDEStatus] = useState<IDEStatus | null>(null);
  const [enabling, setEnabling] = useState(false);

  const enableIDE = async () => {
    setEnabling(true);
    const response = await fetch(`/api/projects/${session.project}/agentic-sessions/${session.name}/ide`, {method: 'POST'});
    const data = await response.json();
    setIDEStatus(data);
    setEnabling(false);
  };

  const openIDE = () => window.open(ideStatus?.ideURL, '_blank');

  if (!ideStatus || ideStatus.phase !== 'Ready') {
    return <Button onClick={enableIDE} disabled={enabling}>
      {enabling ? 'Enabling IDE...' : 'Enable IDE Access'}
    </Button>;
  }

  return <Button onClick={openIDE} variant="primary">Open IDE</Button>;
}
```

---

## Security & Authentication

### OAuth Proxy (Enterprise SSO)

- **OpenShift OAuth integration** - Automatic SSO with cluster users
- **No tokens in URLs** - Secure cookie-based sessions
- **ServiceAccount RBAC** - User must have namespace access
- **TLS end-to-end** - Reencrypt termination at Route
- **Cookie encryption** - 32-byte session secret (rotates on restart)

### RBAC

- IDE access inherits session RBAC permissions
- User must have `get` + `patch` on `AgenticSession`
- Backend enforces via `GetK8sClientsForRequest(c)`

---

## Resource Management

**Per-Session Overhead:**
- IDE: 512Mi–2Gi memory, 200m–2000m CPU
- OAuth: 128Mi–256Mi memory, 50m–200m CPU
- **Total:** ~640MB memory + 250m CPU per active IDE

**No additional storage** (reuses workspace PVC)

---

## Custom Image

**Build:** `quay.io/redhat-acp/openvscode-server-bundle:latest`

**Dockerfile:**
```dockerfile
FROM gitpod/openvscode-server:latest

# Pre-bundle extensions for air-gap environments
RUN code-server --install-extension redhat.vscode-yaml \
    && code-server --install-extension ms-python.python \
    && code-server --install-extension golang.go \
    && code-server --install-extension redhat.openshift-toolkit
```

**Benefits:**
- Air-gap compatible
- Faster startup (no marketplace downloads)
- Offline-ready

---

## Phase 2: Enhanced Features

### Port Forwarding

**Auto-detect running services** in IDE:
- Operator watches Services labeled `session={name}`
- Auto-creates Routes for ports marked `public: true`
- IDE shows "Open in Browser" with Route URL

**Config:**
```json
{
  "portForwarding": {
    "autoDetect": true,
    "rules": [
      {"port": 3000, "label": "Dev Server", "public": true},
      {"port": 8080, "label": "API", "public": true}
    ]
  }
}
```

### Workspace Snapshots

**VolumeSnapshot CSI integration:**
```bash
POST /api/projects/{p}/sessions/{s}/ide/snapshot
{"name": "feature-xyz", "description": "Ready for review"}
```

- Create VolumeSnapshot of workspace PVC
- Store metadata in `WorkspaceSnapshot` CRD
- Generate share URL: `/snapshots/{id}/restore`
- Restore = new session from snapshot

---

## Implementation Schedule

### Phase 1 (4 weeks)

**Week 1: Operator & CRD**
- Update CRD schema
- Implement `reconcileIDE()` + `cleanupIDE()`
- OAuth proxy sidecar injection
- Pod update with fallback-to-recreate logic
- Unit tests

**Week 2: Backend API**
- `/ide` endpoints (POST/GET/DELETE)
- RBAC enforcement via `GetK8sClientsForRequest`
- Integration tests
- Observability (logging, metrics)

**Week 3: Custom Image & Workflow**
- Build `openvscode-server-bundle` image
- Frontend IDE button + status polling
- Workflow loader IDE config parsing
- Example workflow with `.ambient/ide.json`

**Week 4: Testing & Hardening**
- E2E test suite
- Performance validation (startup <60s)
- Security review
- Documentation

### Phase 2 (Future)
- Port forwarding: 2 weeks
- Workspace snapshots: 3 weeks

---

## Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Sidecar pattern** | Shares PVC/network, simpler RBAC |
| **OpenVSCode Server** | OSS, lightweight (300MB vs 1GB+ Dev Spaces) |
| **OAuth from day 1** | Enterprise SSO, production-ready |
| **Pre-bundled image** | Air-gap compatible, offline-ready |
| **Try update, fallback recreate** | Zero-downtime when possible |

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Pod restart required | Graceful recreation with user warning |
| PVC I/O contention | Monitor metrics, QoS limits |
| Image vulnerabilities | Use UBI base, Trivy/Clair scanning |
| Marketplace blocked | Pre-bundle extensions |
| Resource exhaustion | ResourceQuotas, monitoring/alerting |

---

## Success Metrics

**Phase 1:**
- [ ] IDE accessible <60 seconds
- [ ] Workflow config applies automatically
- [ ] <5% overhead when IDE inactive
- [ ] Zero data loss during enable/disable
- [ ] RBAC correctly enforced

**Phase 2:**
- [ ] Port forwarding auto-detects services
- [ ] Snapshots handle >100MB workspaces
- [ ] Snapshot restore <2 minutes

---

## Critical Files

**Operator:**
- `components/operator/api/v1/agenticsession_types.go`
- `components/operator/controllers/agenticsession_controller.go`

**Backend:**
- `components/backend/pkg/handlers/ide.go` (new)
- `components/backend/pkg/routes/routes.go`

**Frontend:**
- `components/frontend/src/components/sessions/SessionDetail.tsx`
- `components/frontend/src/types/session.ts`

**Runner:**
- `components/runners/claude-code-runner/workflow_loader.py`

**Testing:**
- `components/operator/controllers/agenticsession_controller_test.go`
- `test/e2e/ide_access_test.go` (new)

---

## Quickstart

**Enable IDE (UI):**
1. Open session detail page
2. Click "Enable IDE Access"
3. Click "Open IDE" → opens in new tab

**Enable IDE (API):**
```bash
curl -X POST https://acp.example.com/api/projects/my-proj/agentic-sessions/my-session/ide \
  -H "Authorization: Bearer $TOKEN"

# Response: {"ideURL": "https://my-session-ide.apps.cluster.com"}
```

**Configure Workflow:**
```bash
# In workflow repo
cat > .ambient/ide.json <<EOF
{
  "vscode": {
    "extensions": ["golang.go"],
    "settings": {"editor.formatOnSave": true}
  }
}
EOF
```

---

**Architecture:** Sidecar containers (OpenVSCode Server + OAuth proxy)
**Authentication:** OpenShift OAuth SSO
**Storage:** Shared workspace PVC
**Deployment:** Operator-managed Services + Routes
**Configuration:** `.ambient/ide.json` in workflows
