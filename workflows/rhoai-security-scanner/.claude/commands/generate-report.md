# /generate-report - Security Report Generation

Generate a comprehensive security assessment report combining all scan results.

## Report Sections

1. **Executive Summary**
   - Overall security posture score
   - Critical findings count
   - Compliance status
   - Key recommendations

2. **Vulnerability Summary**
   - CVE findings by severity
   - CVSS score distribution
   - Affected components
   - Patch availability

3. **Configuration Issues**
   - Misconfigurations by category
   - Security policy violations
   - Best practice deviations

4. **RBAC Analysis**
   - Permission summary
   - Over-privileged accounts
   - Access control gaps

5. **Compliance Status**
   - CIS Benchmark results
   - Red Hat standards compliance
   - Industry regulation alignment

6. **Remediation Plan**
   - Priority-ordered fixes
   - Effort estimates
   - Implementation scripts
   - Testing requirements

## Output Format

Generate multiple formats at:
- `artifacts/security-reports/full-report-[timestamp].md` - Detailed markdown
- `artifacts/security-reports/executive-summary-[timestamp].pdf` - Management overview
- `artifacts/security-reports/findings-[timestamp].csv` - Spreadsheet format
- `artifacts/remediation/action-plan-[timestamp].md` - Step-by-step fixes

Include visualizations:
- Risk heat map
- Trend analysis
- Component vulnerability matrix
