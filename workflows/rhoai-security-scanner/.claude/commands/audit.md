# /audit - Comprehensive RHOAI Security Audit

Perform a comprehensive security audit of the Red Hat OpenShift AI deployment.

## Audit Scope

1. **Infrastructure Security**
   - Scan all Kubernetes manifests in the project
   - Check namespace configurations
   - Review network policies and ingress rules
   - Analyze persistent volume claims and storage security

2. **RHOAI Component Security**
   - Model serving endpoints authentication
   - Jupyter notebook server configurations
   - Data Science Pipeline security
   - Model registry access controls
   - Workbench configurations

3. **RBAC and Access Control**
   - Service account permissions
   - Role bindings and cluster roles
   - OAuth configurations
   - User access patterns

4. **Secret Management**
   - Scan for hardcoded credentials
   - Check secret encryption at rest
   - Validate secret rotation policies
   - API key management

5. **Container Security**
   - Image vulnerability scanning
   - Check for latest security patches
   - Validate image signing
   - Runtime security policies

6. **Compliance Checks**
   - CIS Kubernetes Benchmark compliance
   - Red Hat security standards
   - NIST framework alignment
   - Industry-specific regulations

## Audit Process

1. **Discovery Phase**
   - Enumerate all RHOAI components
   - Map service dependencies
   - Identify external integrations

2. **Scanning Phase**
   - Run automated security scans
   - Check for CVEs and known vulnerabilities
   - Analyze configurations against best practices

3. **Analysis Phase**
   - Risk scoring of findings
   - Impact assessment
   - Attack vector analysis

4. **Reporting Phase**
   - Generate detailed findings report
   - Provide remediation recommendations
   - Create executive summary

## Output

Generate comprehensive security audit report at:
- `artifacts/security-reports/audit-[timestamp].md`
- `artifacts/vulnerabilities/findings-[timestamp].json`
- `artifacts/remediation/fixes-[timestamp].sh`

Include:
- Executive summary with risk scores
- Detailed vulnerability findings
- CVSS scores for each finding
- Remediation steps and scripts
- Compliance status dashboard

## Priority Checks

Focus on:
1. Critical vulnerabilities (CVSS 9.0+)
2. Public-facing endpoints
3. Privileged service accounts
4. Unencrypted secrets
5. Missing network policies
6. Outdated container images
7. Excessive RBAC permissions
