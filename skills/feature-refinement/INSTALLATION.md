# Feature Refinement Skill - Installation Guide

## Overview

This directory contains a complete Anthropic skill for guiding users through the Red Hat AI feature refinement process.

## Skill Structure

```
.claude/skills/feature-refinement/
├── SKILL.md          # Main skill definition (required)
├── REFERENCE.md      # Complete template reference
├── TEMPLATE.md       # Blank template for document generation
└── README.md         # Usage documentation
```

## Installation Options

### Option 1: Project-Specific Installation (Recommended for Teams)

The skill is already set up in this project at `.claude/skills/feature-refinement/`.

To use it in your project:

1. **Copy to your project:**
   ```bash
   cp -r .claude /path/to/your/project/
   ```

2. **Commit to version control:**
   ```bash
   git add .claude/skills/feature-refinement/
   git commit -m "Add feature refinement skill"
   ```

This makes the skill available to anyone working on the project.

### Option 2: Personal Installation (Available Across All Projects)

To use this skill in all your Claude Code sessions:

1. **Copy to your personal Claude directory:**
   ```bash
   mkdir -p ~/.claude/skills/
   cp -r .claude/skills/feature-refinement ~/.claude/skills/
   ```

2. **Verify installation:**
   ```bash
   ls -la ~/.claude/skills/feature-refinement/
   ```

You should see:
```
SKILL.md
REFERENCE.md
TEMPLATE.md
README.md
```

## Verification

To verify the skill is properly installed:

1. Start a Claude Code session
2. Ask: "What skills are available?"
3. Look for "feature-refinement" in the list

Or simply test it:
```
"Help me create a feature refinement document"
```

Claude should automatically invoke the feature-refinement skill.

## Usage

Once installed, Claude will automatically use this skill when you mention feature refinement tasks:

**Example prompts:**
- "Create a feature refinement document for a new RHOAI feature"
- "Help me refine this feature for RHEL AI"
- "Walk me through the feature refinement process"
- "I need to document a new feature for the team"

## What's Included

### SKILL.md (Required)
The main skill file with:
- YAML frontmatter (name and description)
- Complete 7-step workflow
- Question prompts for gathering information
- Guidance on all template sections

### REFERENCE.md
Comprehensive reference containing:
- Full template structure
- All required sections explained
- Roles and responsibilities
- Contact information and distribution lists
- T-shirt sizing guide

### TEMPLATE.md
Ready-to-use template with:
- All sections pre-formatted
- Markdown/Google Doc compatible
- Checkboxes for tracking progress
- Placeholder text with guidance

### README.md
Documentation including:
- Overview and capabilities
- Installation instructions
- Usage examples
- Tips for best results
- Support contacts

## Customization

To adapt this skill for your organization:

1. **Edit SKILL.md:**
   - Update the description in YAML frontmatter
   - Modify questions and workflow steps
   - Adjust guidance for your process

2. **Edit REFERENCE.md:**
   - Change contact emails
   - Update distribution lists
   - Modify T-shirt sizing scales
   - Add organization-specific sections

3. **Edit TEMPLATE.md:**
   - Adjust table formats
   - Add/remove sections
   - Update checklist items

## Requirements

- Claude Code CLI
- Skills feature enabled (available in recent Claude Code versions)

## Troubleshooting

**Skill not appearing:**
- Verify SKILL.md exists and has proper YAML frontmatter
- Check that the name field contains only lowercase letters, numbers, and hyphens
- Ensure description is under 1024 characters
- Restart Claude Code session

**Skill not triggering automatically:**
- Try explicitly mentioning "feature refinement" in your request
- Ask "Use the feature-refinement skill to help me..."
- Check that the description accurately reflects when to use the skill

**File permission issues:**
```bash
chmod -R 755 ~/.claude/skills/feature-refinement/
```

## Support

For questions about:
- **This skill**: Review README.md in the skill directory
- **Claude Code skills system**: Visit https://docs.claude.com/en/docs/claude-code/skills
- **Feature refinement process**: Contact team-ai-core-platform@redhat.com

## Version Information

- **Created**: 2025-11-12
- **Compatible with**: Claude Code Skills system
- **Target Products**: RHOAI, RHAIIS, RHEL AI

## Next Steps

After installation:

1. ✅ Verify the skill is recognized by Claude
2. ✅ Test with a sample feature refinement
3. ✅ Customize for your organization (optional)
4. ✅ Share with team members (if using project installation)
5. ✅ Review REFERENCE.md for complete template details

## File Manifest

```
.claude/skills/feature-refinement/SKILL.md       - Main skill definition
.claude/skills/feature-refinement/REFERENCE.md   - Complete reference guide
.claude/skills/feature-refinement/TEMPLATE.md    - Blank document template
.claude/skills/feature-refinement/README.md      - Usage documentation
```

Total files: 4
Total size: ~30KB
