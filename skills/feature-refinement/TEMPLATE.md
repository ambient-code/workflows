# Feature Refinement Document Template

**Document Title:** FeatureRefinement - [JIRA#] - [TITLE]

---

## Feature Metadata

| Field | Value |
|-------|-------|
| **Feature Jira Link** | [Link to XXXSTRAT-####] |
| **Slack Channel / Thread** | [Link or N/A] |
| **Feature Owner** | [Name] |
| **Delivery Owner** | [Name] |
| **RFE Council Reviewer** | [Name] |
| **Product** | [RHOAI (managed/self-managed) / RHAIIS / RHEL AI] |
| **Status** | Not started |

---

## Feature Details

### Feature Overview

[Description of feature. Answer the following:
- Who (which persona/user role) benefits from this feature, and how?
- What is the difference between today's current state and a world with this feature?
- High level user narrative: Tell how the user would use this functionality and when they would use it.]

### The Why

[Why are we doing this feature now? What will this bring to the platform, how will it help us win customers, and what types of customers will benefit from it? What supporting data do we have? If this is assumptive and not data-driven, provide clear success metrics for validating assumptions.]

### High Level Requirements

*Format: As a [user role/persona], I want [capability/feature], So that [benefit/business value]*

1. As a [persona], I want [capability], So that [benefit]
2. As a [persona], I want [capability], So that [benefit]
3. [Add more as needed]

### Non-Functional Requirements

- **Performance**: [Performance parameters and expectations]
- **Security**: [Security concerns or areas to watch]
- **Disconnected Environments**: [Special considerations if applicable]
- **User Expectations**: [User experience requirements]
- **Upgrade Considerations**: [Considerations from previous releases]
- [Add others as needed]

### Out-of-Scope

[Define the boundaries of the feature. List items that are Out-of-Scope:]

- [Out-of-scope item 1]
- [Out-of-scope item 2]
- [Add more as needed]

### Acceptance Criteria

*Format: Given [context or precondition], When [action taken], Then [expected outcome]*

1. **Given** [context], **When** [action], **Then** [outcome]
2. **Given** [context], **When** [action], **Then** [outcome]
3. [Add more as needed]

### Risks & Assumptions

**Risks:** *Potential blockers or threats to successful delivery*
- [Risk 1]
- [Risk 2]
- [Add more as needed]

**Assumptions:** *Conditions believed to be true but needing validation*
- [Assumption 1]
- [Assumption 2]
- [Add more as needed]

### Supporting Documentation

- Design: [Link]
- Workflows: [Link]
- Wireframes: [Link]
- Discovery Notes: [Link]
- Technical Documentation: [Link]
- [Add others as needed]

### Additional Clarifying Information

[Add any other information that would further clarify the requirement and aid the delivery teams in understanding the full context of this request.]

---

## New Feature / Component Prerequisites & Dependencies

### ODH/RHOAI Build Process Onboarding

**Will this feature require onboarding of a new container Image or component?** ☐ YES ☐ NO

**If YES:**
- Follow onboarding instructions for appropriate epic:
  - DevPreview: Clone RHOAIENG-31244
  - TechPreview: Clone RHOAIENG-31290
  - GA: Clone RHOAIENG-31303
- Email team-ai-core-platform@redhat.com for questions

### License Validation

**Will this feature require bringing in new upstream projects or sub-projects into the product?** ☐ YES ☐ NO

**If YES:**
- License type: [Apache 2.0 preferred]
- If not Apache 2.0, justification: [Explain and post to forum-openshift-ai-architecture]

### Accelerator/Package Support

**Does this feature require support from the AIPCC team?** ☐ YES ☐ NO

**If YES:**
- New/updated package requests: [Details - follow AIPCC-1 process]
- Accelerators to support: [List accelerators]
- Other AIPCC work needed: [Describe and create AIPCC Feature]

### Architecture Review Check

**Does the feature have the label "requires_architecture_review"?** ☐ YES ☐ NO

**Does the related RFE indicate "Requires architecture review: YES"?** ☐ YES ☐ NO

**If YES to either:**
- ⚠️ Feature design MUST be reviewed at the OpenShift AI Architecture Forum before committing to a solution
- Teams may conduct spikes/research before formal review

### Additional Dependencies

[Include any other prerequisites or dependencies needed to deliver this feature]

---

## High Level Plan

### Teams Involved in Feature Delivery

| Team | Start Date | Work to Deliver (EPIC) | Team Dependencies | T-Shirt Size | Approval/Comments |
|------|------------|------------------------|-------------------|--------------|-------------------|
| team-ai-core-platform | [Date] | [EPIC link/description] | [Dependencies] | [XS/S/M/L/XL] | [Name/Date or What's needed] |
| [Team Name] | [Date] | [EPIC link/description] | [Dependencies] | [XS/S/M/L/XL] | [Name/Date or What's needed] |
| [Team Name] | [Date] | [EPIC link/description] | [Dependencies] | [XS/S/M/L/XL] | [Name/Date or What's needed] |

**T-Shirt Size Scale:**
- **XS**: < 1 sprint
- **S**: 1 sprint (3 weeks)
- **M**: 2 sprints (6 weeks)
- **L**: 3 sprints (9 weeks) - Highly recommend breaking down
- **XL**: 4 sprints (12 weeks) - Too big! Break it down!

*Note: Do not include time waiting on upstream or other teams*

---

## Documentation and UXD Engagement

### Documentation Team Engagement

- [ ] Added "Documentation" component to the feature
- [ ] Set "Product Documentation Required" field to Yes
- [ ] Added docs team to High Level Plan table
- [ ] Reviewed [Docs Intake Process](https://docs.google.com/document/d/1G_LKipII0DMX3UxpkxVEpgM9Pk5tHcfZdvnkjn9E1mI/edit?tab=t.0)
- [ ] Flagged for Release Notes (if applicable)

### UXD Team Engagement

- [ ] Added "UXD" component to the feature
- [ ] Added UXD team to High Level Plan table
- [ ] Contacted:
  - ☐ Jenn Giardino (jgiardin@redhat.com)
  - ☐ Beau Morley (bmorley@redhat.com)

---

## Feature Owner Checklist

### Initial Setup
- [ ] Linked this document in the Jira Feature
- [ ] Created public Slack channel (if needed): [Link]
- [ ] Confirmed POCs from each team
- [ ] Updated status to "In Progress"

### Communication
- [ ] Announced feature via email to all stakeholder teams
- [ ] Scheduled review meeting with delivery teams

### Email Distribution Checklist
Ensure the following teams are included:
- [ ] All teams responsible for impacted components
- [ ] aipcc-eng-directs
- [ ] inference-ai-eng
- [ ] team-psap@redhat.com
- [ ] team-ai-core-platform@redhat.com
- [ ] ai-bu@redhat.com
- [ ] openshift-ai-docs@redhat.com
- [ ] ai-ux-all@redhat.com
- [ ] rhai-service-teams@redhat.com
- [ ] openshift-ai-devtestops@redhat.com
- [ ] openshift-ai-qe@redhat.com
- [ ] dramseur@redhat.com

### Finalization
- [ ] All impacted components listed in Jira Feature's Components field
- [ ] All teams populated Epic's Parent Link field with Feature link
- [ ] All comments addressed
- [ ] All teams approved (check Approval/Comments column)
- [ ] Updated status to "Approved"
- [ ] Set document permissions to Read-Only
- [ ] Uploaded to [Feature Refinement Documents Folder](https://drive.google.com/drive/folders/1SZjUobSqm4t8etx9nVY0agPhH4Wu0IuS?usp=drive_link)

---

## Delivery Owner Checklist

- [ ] Reviewed and agreed to scope and deliverables
- [ ] Coordinated tracked work creation for all teams
- [ ] Ensured all teams signed off
- [ ] Verified Definition of Ready is met
- [ ] Announced feature development start to organization

---

**Document Status:** [Not started / In Progress / Approved]

**Last Updated:** [Date]
