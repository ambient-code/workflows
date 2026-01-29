# Issue Triage Workflow

A systematic workflow for triaging repository issue backlogs with AI-powered recommendations and bulk operations support.

## Overview

This workflow helps teams efficiently triage large issue backlogs by:
- Analyzing all open issues in a repository
- Providing actionable recommendations (CLOSE, FIX_NOW, BACKLOG, NEEDS_INFO, etc.)
- Generating interactive HTML reports with sorting and simulation
- Supporting bulk operations for GitHub and Jira
- Automating monthly triage via GitHub Actions

## Features

### Interactive HTML Report
- **Sortable Columns**: Click any column header to sort (default: by recommendation)
- **Simulation Mode**: Preview how recommendations affect the backlog before applying
- **Last Modified Tracking**: See who last updated each issue and when
- **Filters**: Filter by recommendation, type, priority, or search
- **Bulk Operations**: Select issues and generate operations script

### Recommendations
- **CLOSE**: Invalid, obsolete, or duplicate issues
- **FIX_NOW**: Critical issues or quick wins
- **BACKLOG**: Valid issues for future work
- **NEEDS_INFO**: Blocked on additional information
- **DUPLICATE**: Duplicate of existing issue
- **AMBER_AUTO**: Can be fixed automatically by Amber
- **ASSIGN**: Ready to be assigned to a developer
- **WONT_FIX**: Valid but won't be addressed

### Bulk Operations
Execute bulk operations on GitHub or Jira:
```bash
./scripts/bulk-operations.sh --backend github --repo owner/repo --operations operations.json
```

Supports:
- Closing issues
- Adding labels
- Assigning issues
- Linking duplicates
- Adding comments

## Quick Start

### Option 1: Manual Triage (Local)

1. **Start workflow:**
   ```bash
   ambient session create --workflow triage
   ```

2. **Provide repository:**
   ```
   Triage the backlog for https://github.com/owner/repo
   ```

3. **Open generated report:**
   ```bash
   open artifacts/triage/report.html
   ```

### Option 2: Automated Triage (GitHub Actions)

1. **Copy workflow to your repo:**
   ```bash
   cp .github/workflows/triage-report.yml /your/repo/.github/workflows/
   ```

2. **Commit and push:**
   ```bash
   git add .github/workflows/triage-report.yml
   git commit -m "Add automated triage workflow"
   git push
   ```

3. **Workflow runs automatically monthly or manually via Actions tab**

4. **Download artifact and open report.html**

## Files

- `.ambient/ambient.json` - Workflow definition
- `templates/report.html` - Interactive HTML template
- `templates/triage-report.md` - Markdown template
- `scripts/bulk-operations.sh` - Bulk operations script
- `.github/workflows/triage-report.yml` - GitHub Actions workflow

## Outputs

Generated in `artifacts/triage/`:
- `report.html` - Interactive dashboard with sorting, simulation, filters
- `triage-report.md` - Markdown format for easy reading
- `operations.json` - Example bulk operations
- `triage_issues.json` - Structured JSON data

## GitHub Actions Configuration

The workflow runs:
- **Schedule**: Monthly on 1st at 00:00 UTC
- **Manual**: Via workflow_dispatch
- **Retention**: 90 days

Configure by editing `.github/workflows/triage-report.yml`

## Customization

### Modify Report UI
Edit `templates/report.html`:
- Change colors/styling
- Add new columns
- Modify filters
- Add charts

### Customize Recommendations
Edit `.ambient/ambient.json`:
- Add new recommendation types
- Change triage logic
- Modify output format

### Adjust GitHub Actions
Edit `.github/workflows/triage-report.yml`:
- Change schedule
- Modify retention period
- Add notifications

## Requirements

- GitHub CLI (`gh`) for issue fetching
- Jira REST API credentials (for Jira backend)
- Python 3.x (for GitHub Actions workflow)

## Support

For questions or issues:
- Review this README
- Check example outputs in the package
- Open an issue at https://github.com/ambient-code/workflows

## License

MIT
