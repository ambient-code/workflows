# /helpers.scan-fips - Run FIPS Compliance Scan

## Purpose
Executes a FIPS (Federal Information Processing Standards) compliance scan on the codebase using the fips-compliance-checker plugin from the odh-ai-helpers marketplace. This command identifies cryptographic implementations that may not comply with FIPS 140-2/140-3 standards.

## Prerequisites
- odh-ai-helpers marketplace must be configured and enabled
- fips-compliance-checker plugin must be available
- Target codebase must be accessible in the workspace
- Run `/helpers.validate` first to ensure marketplace is operational

## Process

1. **Verify Plugin Availability**
   - Confirm fips-compliance-checker plugin is accessible
   - Check marketplace configuration
   - Validate plugin dependencies are met

2. **Prepare Scan Environment**
   - Identify target directory for scanning (default: current workspace)
   - Create output directory for scan results
   - Initialize scan configuration

3. **Execute FIPS Scan**
   - Invoke fips-compliance-checker plugin
   - Scan codebase for cryptographic library usage
   - Check for FIPS-approved algorithms
   - Identify non-compliant implementations
   - Detect deprecated or weak cryptographic functions

4. **Analyze Results**
   - Parse scan output
   - Categorize findings by severity
   - Identify file locations of non-compliant code
   - Generate recommendations for remediation

5. **Generate Compliance Report**
   - Create detailed report of findings
   - Include code snippets showing issues
   - Provide remediation guidance
   - Summarize compliance status

## Output
- **FIPS Compliance Report**: `artifacts/ai-helpers/reports/fips-compliance.md`
  - Executive summary of compliance status
  - Detailed findings with file locations and line numbers
  - Severity classification (Critical, High, Medium, Low)
  - Remediation recommendations
  - List of FIPS-approved alternatives

- **Scan Log**: `artifacts/ai-helpers/reports/fips-scan-log.txt`
  - Raw output from fips-compliance-checker plugin
  - Timestamp and scan configuration
  - Complete list of files scanned

## Usage Examples

Scan current workspace:
```
/helpers.scan-fips
```

Scan specific directory:
```
/helpers.scan-fips path/to/code
```

Expected output:
```
FIPS Compliance Scan Report
============================

Scan Summary:
- Files scanned: 47
- Issues found: 3
- Critical: 1
- High: 1
- Medium: 1
- Low: 0

Critical Issues:
----------------
1. Non-FIPS approved algorithm detected
   File: src/crypto/encryption.py:23
   Issue: Using MD5 hashing (not FIPS 140-2 approved)
   Recommendation: Replace with SHA-256 or SHA-3

High Issues:
-----------
1. Weak key length detected
   File: src/auth/keys.py:45
   Issue: RSA key length < 2048 bits
   Recommendation: Use minimum 2048-bit RSA keys

Medium Issues:
-------------
1. Deprecated cryptographic function
   File: src/utils/crypto.py:67
   Issue: Using DES encryption
   Recommendation: Migrate to AES-256

Compliance Status: ✗ NON-COMPLIANT

Review the detailed report at:
artifacts/ai-helpers/reports/fips-compliance.md
```

## Success Criteria

After running this command, you should have:
- [ ] FIPS compliance scan completed successfully
- [ ] All cryptographic implementations analyzed
- [ ] Non-compliant code identified with file locations
- [ ] Remediation recommendations provided
- [ ] Compliance report generated

## Next Steps

After reviewing the scan results:
1. Prioritize fixes based on severity (Critical → High → Medium → Low)
2. Review remediation recommendations for each issue
3. Implement approved cryptographic alternatives
4. Re-run `/helpers.scan-fips` to verify fixes
5. Document compliance status in project documentation

## Notes
- Scan may take several minutes for large codebases
- Plugin scans for common non-compliant patterns but may not catch all issues
- Manual security review is recommended in addition to automated scanning
- FIPS compliance requirements vary by use case and jurisdiction
- Consult security team for compliance interpretation
- Some findings may be false positives - review carefully
- Plugin requires access to codebase files (read permissions)
