# 🔒 RHOAI Security Scanner Workflow

Comprehensive security scanning and vulnerability assessment for Red Hat OpenShift AI (RHOAI) deployments.

## Overview

This workflow provides automated security scanning capabilities for RHOAI projects, integrating with the [RHOAI Security Scanner](https://gitlab.cee.redhat.com/mstratto/rhoai-security-scanner.git) to identify vulnerabilities, misconfigurations, and compliance issues.

## Features

- 🔍 **Comprehensive Security Audits** - Full deployment scanning
- 📦 **Kubernetes Manifest Analysis** - Configuration security checks  
- 🔐 **RBAC Validation** - Permission and access control analysis
- 🤖 **Model Serving Security** - ML endpoint protection validation
- 📊 **Compliance Reporting** - CIS benchmark and Red Hat standards
- 🛠️ **Automated Remediation** - Fix scripts and recommendations

## Integration with Ambient Code Platform

### How It Works

Unlike traditional Claude marketplace plugins, this workflow integrates through:

1. **Workflow Configuration** (`.ambient/ambient.json`) - Defines the scanner behavior
2. **Slash Commands** (`.claude/commands/`) - Security scanning actions
3. **Integration Scripts** (`scripts/`) - Connect to external scanner tools
4. **MCP Servers** (optional) - Additional tool integrations

### Loading the Workflow

#### Via UI:
1. Navigate to your Ambient Code Platform session
2. Click **Workflows** → **Custom Workflow**
3. Enter:
   - **Git URL**: `https://github.com/your-org/rhoai-security-scanner.git`
   - **Branch**: `main`
   - **Path**: `workflows/workflows/rhoai-security-scanner`
4. Click **Load Workflow**

#### Via API:
```bash
curl -X POST https://your-platform/api/projects/{project}/agentic-sessions/{session}/workflow \
  -H "Content-Type: application/json" \
  -d '{
    "gitUrl": "https://github.com/your-org/workflows.git",
    "branch": "main", 
    "path": "workflows/workflows/rhoai-security-scanner"
  }'
```

## Available Commands

| Command | Description |
|---------|-------------|
| `/audit` | Run comprehensive security audit |
| `/scan-manifests` | Scan Kubernetes YAML files |
| `/check-rbac` | Analyze RBAC configurations |
| `/scan-models` | Check model serving security |
| `/scan-pipelines` | Analyze pipeline security |
| `/generate-report` | Create security report |

## Quick Start

1. **Load the workflow** in your session
2. **Run initial audit**: Type `/audit` in the chat
3. **Review findings** in `artifacts/security-reports/`
4. **Apply remediations** from `artifacts/remediation/`

## External Scanner Integration

This workflow can integrate with the external RHOAI Security Scanner:

### Automatic Integration

The workflow includes `scripts/scanner-integration.sh` which:
1. Clones the scanner repository
2. Installs dependencies
3. Runs security scans
4. Generates reports

### Manual Setup (if needed)

```bash
# Clone the external scanner
git clone https://gitlab.cee.redhat.com/mstratto/rhoai-security-scanner.git

# Install dependencies
cd rhoai-security-scanner
pip install -r requirements.txt

# Run scan
./rhoai-scanner audit --path /your/project
```

## Output Structure

```
artifacts/
├── security-reports/     # Detailed audit reports
│   ├── audit-*.md
│   └── scan-*.md
├── vulnerabilities/      # Finding details
│   ├── findings-*.json
│   └── cve-*.json
├── remediation/         # Fix scripts
│   ├── fixes-*.sh
│   └── patches-*.yaml
├── compliance/          # Compliance reports
│   └── cis-*.md
└── logs/               # Scan logs
    └── scan-*.log
```

## Security Checks Performed

### Infrastructure
- Kubernetes manifest security
- Network policy analysis
- Storage encryption validation
- Secret management review

### RHOAI Components
- Model server authentication
- Jupyter notebook security
- Pipeline access controls
- Registry permissions

### Compliance
- CIS Kubernetes Benchmark
- Red Hat Security Standards
- NIST Framework alignment
- Industry regulations

## Customization

### Adding New Scan Commands

Create new commands in `.claude/commands/`:

```markdown
# /custom-scan

Perform custom security scan for specific components.

[Your scan instructions here]
```

### Modifying Scanner Behavior

Edit `.ambient/ambient.json`:

```json
{
  "settings": {
    "severityThreshold": "high",
    "scanInterval": "daily",
    "includeRemediations": true
  }
}
```

## MCP Server Support (Optional)

To add MCP server plugins, create `.mcp.json`:

```json
{
  "mcpServers": {
    "security-tools": {
      "command": "security-scanner-mcp",
      "args": ["--mode", "server"],
      "env": {
        "SCANNER_API_KEY": "${SCANNER_API_KEY}"
      }
    }
  }
}
```

## Troubleshooting

### Scanner Not Found
If the external scanner can't be cloned:
- Check GitLab access permissions
- Verify network connectivity
- Use fallback scanning mode

### Missing Dependencies
```bash
pip install pyyaml kubernetes requests
```

### Permission Issues
Ensure the service account has:
- Read access to manifests
- List/get on resources
- Access to security APIs

## Support

- **Workflow Issues**: Open issue in this repository
- **Scanner Issues**: Contact RHOAI Security Team
- **Platform Issues**: Ambient Code Platform support

## License

This workflow is provided under the same license as the Ambient Code Platform.

---

**Note**: This workflow replaces traditional Claude marketplace plugins with a platform-native integration that provides the same security scanning capabilities within the Ambient Code Platform architecture.
