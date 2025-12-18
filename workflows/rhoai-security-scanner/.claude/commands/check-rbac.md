# /check-rbac - RBAC Security Analysis

Analyze Role-Based Access Control configurations for security issues.

## Analysis Scope

1. **Service Accounts**
   - List all service accounts
   - Check for default SA usage
   - Identify over-privileged accounts

2. **Roles and ClusterRoles**
   - Wildcard permissions (*)
   - Dangerous verbs (delete, exec, patch)
   - Admin/root level access

3. **RoleBindings**
   - User to role mappings
   - Group permissions
   - Cross-namespace bindings

4. **Security Concerns**
   - Cluster-admin bindings
   - Excessive get/list permissions
   - Pod exec capabilities
   - Secret access patterns

## Generate Report

Output to `artifacts/rbac-analysis/rbac-audit-[timestamp].md` with:
- Permission matrix
- Risk assessment per service account
- Least privilege recommendations
- Remediation scripts
