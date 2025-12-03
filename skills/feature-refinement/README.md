# Feature Refinement Skill

A Claude Code skill for guiding users through the Red Hat AI feature refinement process.

## Overview

This skill helps Product Managers, Engineering Managers, and other stakeholders create comprehensive feature refinement documents for Red Hat AI products (RHOAI, RHAIIS, RHEL AI). It follows the official Feature Refinement Template and ensures all required sections, dependencies, and approval processes are properly documented.

## Installation

### For Project-Specific Use
This skill is already located in the project directory:
```
.claude/skills/feature-refinement/
```

### For Personal Use (Available Across All Projects)
Copy the skill to your personal Claude skills directory:

```bash
mkdir -p ~/.claude/skills/
cp -r .claude/skills/feature-refinement ~/.claude/skills/
```

## Usage

Claude will automatically invoke this skill when you mention feature refinement tasks. You can also explicitly ask Claude to use it:

**Examples:**
- "Help me create a feature refinement document for a new RHOAI feature"
- "I need to refine a feature for RHEL AI"
- "Walk me through the feature refinement process"
- "Use the feature refinement skill to document this new capability"

## What This Skill Does

The skill guides you through a comprehensive 7-step process:

1. **Gather Initial Information** - Collects basic feature metadata (Jira link, owners, product)
2. **Define Feature Details** - Documents overview, requirements, acceptance criteria, risks
3. **Verify Prerequisites & Dependencies** - Checks build onboarding, licensing, accelerator support, architecture review needs
4. **Create High-Level Delivery Plan** - Builds team delivery table with effort estimates
5. **Documentation and UXD Engagement** - Ensures proper engagement with Docs and UX teams
6. **Generate Document** - Creates the complete feature refinement document
7. **Feature Owner Next Steps** - Provides checklist for announcement, review, and approval

## Key Features

- **Interactive Guidance**: Asks clarifying questions to gather all required information
- **Format Templates**: Provides proper formatting for user stories (As a/I want/So that) and acceptance criteria (Given/When/Then)
- **Dependency Tracking**: Ensures all prerequisites are identified (build onboarding, licensing, AIPCC, architecture review)
- **Team Coordination**: Helps build comprehensive team delivery plans with effort estimates
- **Stakeholder Management**: Includes complete email distribution lists and engagement processes
- **Process Compliance**: Follows official Red Hat AI feature refinement workflow

## File Structure

```
.claude/skills/feature-refinement/
├── SKILL.md          # Main skill definition with step-by-step workflow
├── REFERENCE.md      # Complete template reference and detailed guidance
└── README.md         # This file
```

## Products Supported

- **RHOAI** (Red Hat OpenShift AI)
  - Managed
  - Self-managed
- **RHAIIS** (Red Hat AI Infrastructure Services)
- **RHEL AI** (Red Hat Enterprise Linux AI)

## T-Shirt Size Reference

The skill uses standard sprint-based sizing:
- **XS**: < 1 sprint
- **S**: 1 sprint (3 weeks)
- **M**: 2 sprints (6 weeks)
- **L**: 3 sprints (9 weeks) - Consider breaking down
- **XL**: 4 sprints (12 weeks) - Must break down

## Key Contacts & Teams

The skill includes contact information and distribution lists for:
- Documentation team
- UXD team (Jenn Giardino, Beau Morley)
- Core platform team (team-ai-core-platform@redhat.com)
- All relevant stakeholder groups

## Prerequisites Knowledge

The skill references several important processes:
- JIRA epic/feature linking
- AIPCC package request process (AIPCC-1)
- Build onboarding epics (RHOAIENG-31244, RHOAIENG-31290, RHOAIENG-31303)
- Architecture review requirements
- Docs intake process

## Output Format

The skill can generate the feature refinement document in:
- **Google Doc format** (recommended for collaboration)
- **Markdown format** (for version control)

Both formats include all required sections, tables, and proper formatting.

## Tips for Best Results

1. **Have Information Ready**: Gather your Jira link, feature description, and key stakeholders before starting
2. **Be Specific**: Provide detailed answers for feature overview and requirements
3. **Think Cross-Team**: Consider all teams that might be impacted
4. **Use Provided Formats**: Leverage the user story and acceptance criteria templates
5. **Don't Skip Prerequisites**: Complete all dependency checks (build, licensing, AIPCC, architecture)
6. **Engage Early**: Include Docs and UXD teams from the beginning

## Customization

To modify this skill for your organization:
1. Edit `SKILL.md` to adjust the workflow or questions
2. Update `REFERENCE.md` with your template structure
3. Change contact emails and distribution lists as needed
4. Adjust T-shirt sizing scales if you use different sprint lengths

## Related Documentation

- [Feature Refinement Documents Folder](https://drive.google.com/drive/folders/1SZjUobSqm4t8etx9nVY0agPhH4Wu0IuS?usp=drive_link)
- [Docs Intake Process](https://docs.google.com/document/d/1G_LKipII0DMX3UxpkxVEpgM9Pk5tHcfZdvnkjn9E1mI/edit?tab=t.0)
- Build Onboarding Epics: RHOAIENG-31244 (DevPreview), RHOAIENG-31290 (TechPreview), RHOAIENG-31303 (GA)
- AIPCC Package Requests: AIPCC-1

## Support

For questions about:
- **Build Process**: team-ai-core-platform@redhat.com
- **UX Design**: Jenn Giardino (jgiardin@redhat.com) or Beau Morley (bmorley@redhat.com)
- **Documentation**: openshift-ai-docs@redhat.com
- **AIPCC/Accelerators**: Follow AIPCC-1 process

## Version

Created: 2025-11-12
Compatible with: Claude Code Skills system
