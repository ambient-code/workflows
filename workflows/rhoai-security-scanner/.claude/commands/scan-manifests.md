# /scan-manifests - Kubernetes Manifest Security Scanner

Scan all Kubernetes manifests for security vulnerabilities and misconfigurations.

## Scanning Targets

Look for YAML files in:
- `manifests/` directories
- `k8s/` or `kubernetes/` folders
- `deployments/` or `deploy/` directories
- Any `*.yaml` or `*.yml` files

## Security Checks

1. **Container Security**
   - Running as root user
   - Privileged containers
   - Missing security contexts
   - Unrestricted capabilities
   - Host network/PID/IPC usage

2. **Resource Limits**
   - Missing CPU/memory limits
   - Missing resource requests
   - Unbounded resource consumption

3. **Network Policies**
   - Missing network segmentation
   - Overly permissive rules
   - Exposed services

4. **RBAC Issues**
   - Excessive permissions
   - Wildcard resources
   - Cluster-admin bindings

5. **Secret Exposure**
   - Hardcoded secrets
   - Environment variable secrets
   - Unencrypted configmaps

## Generate Report

Create findings at `artifacts/vulnerabilities/manifest-scan-[timestamp].md` with:
- File path and line numbers
- Vulnerability description
- Risk level (Critical/High/Medium/Low)
- CIS benchmark reference
- Remediation example
