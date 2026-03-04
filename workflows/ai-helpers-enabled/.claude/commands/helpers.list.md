# /helpers.list - List Available Marketplace Plugins

## Purpose
Enumerates all available plugins and tools from the odh-ai-helpers marketplace, displaying their capabilities, descriptions, and current status. This command helps users discover what marketplace tools are available for their tasks.

## Prerequisites
- Marketplace must be configured in `.claude/claude-settings.json`
- The `/opt/ai-helpers` directory must be accessible
- Marketplace metadata file must exist at `/opt/ai-helpers/.claude-plugin/marketplace.json`

## Process

1. **Verify Marketplace Configuration**
   - Check that `.claude/claude-settings.json` exists
   - Confirm `odh-ai-helpers` is registered in `extraKnownMarketplaces`
   - Verify plugin is enabled in `enabledPlugins`

2. **Access Marketplace Directory**
   - Navigate to `/opt/ai-helpers`
   - Read marketplace metadata from `.claude-plugin/marketplace.json`
   - Parse plugin definitions

3. **Enumerate Plugins**
   - List each plugin by name
   - Display plugin description
   - Show source information (URL or local path)
   - Indicate current activation status

4. **Generate Plugin Report**
   - Create formatted output showing all available tools
   - Group plugins by category if applicable
   - Provide usage guidance for each plugin

## Output
- **Console Display**: Formatted list of plugins with descriptions
  - Shows plugin names, descriptions, and sources
  - Indicates which plugins are currently enabled

- **Plugin Inventory**: `artifacts/ai-helpers/reports/plugin-inventory.md`
  - Complete catalog of available marketplace tools
  - Detailed description of each plugin's capabilities
  - Usage examples and recommendations

## Usage Examples

Basic usage:
```
/helpers.list
```

Expected output:
```
odh-ai-helpers Marketplace Plugins
===================================

✓ fips-compliance-checker
  Description: Plugin to scan for FIPS compliance
  Source: https://github.com/opendatahub-io/fips-compliance-checker-claude-code-plugin.git
  Status: Available

✓ odh-ai-helpers
  Description: AI automation tools, plugins, and assistants for enhanced productivity
  Source: ./helpers
  Status: Enabled

Total plugins available: 2
```

## Success Criteria

After running this command, you should have:
- [ ] Complete list of available marketplace plugins displayed
- [ ] Plugin descriptions and capabilities clearly explained
- [ ] Current activation status shown for each plugin
- [ ] Plugin inventory report generated in artifacts directory

## Next Steps

After reviewing available plugins:
1. Run `/helpers.validate` to ensure marketplace is properly configured
2. Use specific plugin commands as needed for your tasks
3. Refer to the generated inventory for plugin capabilities

## Notes
- Plugin availability depends on marketplace installation and configuration
- Some plugins may require additional setup or authentication
- Plugin list reflects the current marketplace version installed at `/opt/ai-helpers`
- New plugins may be added to the marketplace through updates
