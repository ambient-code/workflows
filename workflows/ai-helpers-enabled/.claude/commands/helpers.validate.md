# /helpers.validate - Validate Marketplace Configuration

## Purpose
Performs comprehensive validation of the odh-ai-helpers marketplace configuration to ensure it is properly set up and accessible. This command diagnoses configuration issues and verifies that marketplace plugins are ready to use.

## Prerequisites
- Workflow must be loaded in an ACP session
- `.claude/claude-settings.json` should exist in the workflow directory

## Process

1. **Check Configuration Files**
   - Verify `.claude/claude-settings.json` exists
   - Validate JSON syntax is correct
   - Confirm `extraKnownMarketplaces` section is present
   - Check that `odh-ai-helpers` marketplace is registered
   - Verify plugin enablement in `enabledPlugins` section

2. **Validate Marketplace Directory**
   - Check if `/opt/ai-helpers` directory exists and is accessible
   - Count files in marketplace directory
   - Verify directory permissions allow read access

3. **Check Marketplace Metadata**
   - Locate marketplace definition at `/opt/ai-helpers/.claude-plugin/marketplace.json`
   - Validate metadata file syntax
   - Extract marketplace name and owner information
   - Enumerate registered plugins

4. **Test Plugin Availability**
   - Attempt to access each registered plugin
   - Verify plugin source paths are valid
   - Check for any plugin loading errors

5. **Generate Validation Report**
   - Document configuration status
   - List any issues found
   - Provide remediation recommendations
   - Summary of marketplace health

## Output
- **Validation Report**: `artifacts/ai-helpers/reports/marketplace-validation.md`
  - Configuration status (PASS/FAIL)
  - Marketplace directory accessibility
  - List of detected plugins
  - Issues found and recommendations
  - Overall marketplace health status

## Usage Examples

Basic usage:
```
/helpers.validate
```

Expected successful output:
```
Marketplace Validation Report
==============================

Configuration Check: ✓ PASS
- Claude settings file: EXISTS
- Marketplace registered: YES (odh-ai-helpers)
- Plugin enabled: YES

Marketplace Availability: ✓ PASS
- Directory /opt/ai-helpers: ACCESSIBLE
- Files found: 101
- Metadata file: PRESENT

Plugins Detected: 2
- fips-compliance-checker
- odh-ai-helpers

Overall Status: ✓ HEALTHY

The marketplace is properly configured and ready to use.
```

Expected failure output:
```
Marketplace Validation Report
==============================

Configuration Check: ✗ FAIL
- Claude settings file: MISSING
- Marketplace registered: NO
- Plugin enabled: N/A

Marketplace Availability: ✗ FAIL
- Directory /opt/ai-helpers: NOT FOUND

Recommendations:
1. Ensure workflow is loaded in an ACP session with marketplace support
2. Verify /opt/ai-helpers is mounted in the session environment
3. Check .claude/claude-settings.json configuration

Overall Status: ✗ UNAVAILABLE
```

## Success Criteria

After running this command, you should have:
- [ ] Configuration validation completed
- [ ] Marketplace accessibility confirmed
- [ ] Plugin availability verified
- [ ] Validation report generated with clear status
- [ ] Remediation steps provided if issues found

## Next Steps

If validation passes:
1. Run `/helpers.list` to see available plugins
2. Proceed with using marketplace tools in your workflow

If validation fails:
1. Review the validation report for specific issues
2. Follow remediation recommendations
3. Contact support if issues persist
4. Check ACP session configuration

## Notes
- This command is safe to run multiple times
- Validation checks are non-invasive (read-only)
- Run this command if marketplace plugins aren't working as expected
- Validation report includes timestamps for troubleshooting
- Directory checks may fail outside of ACP sessions (expected behavior)
