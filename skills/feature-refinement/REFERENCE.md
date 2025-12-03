# Feature Refinement Template Reference

This reference contains the complete feature refinement template structure for Red Hat AI products.

## Document Naming Convention

Format: `FeatureRefinement - Jira# - TITLE OF STRAT`

## Document Header Table

| Field | Value |
|-------|-------|
| Feature Jira Link | <Add link to the feature (XXXSTRAT-####)> |
| Status | Not started / In Progress / Approved |
| Slack Channel / Thread | <Add slack channel or discussion thread if applicable> |
| Feature Owner | Person |
| Delivery Owner | Person |
| RFE Council Reviewer | Person |
| Product | <RHOAI (managed/self-managed), RHAIIS, or RHEL AI> |

## Feature Details Sections

### 1. Feature Overview
Description of feature. Answer:
- Who (which persona/user role) benefits from this feature, and how?
- What is the difference between today's current state and a world with this feature?
- High level user narrative: How and when would the user use this functionality?

### 2. The Why
- Why are we doing this feature now?
- What will this bring to the platform?
- How will it help us win customers?
- What types of customers will benefit?
- What supporting data do we have?
- If assumptive and not data-driven, provide clear success metrics

### 3. High Level Requirements
List of functionality delivered through this feature, focusing on mandatory requirements for initial release.

**Suggested format:**
- As a [user role/persona]
- I want [capability/feature]
- So that [benefit/business value]

### 4. Non-Functional Requirements
List non-functional requirements such as:
- Performance parameters
- Security concerns or areas to watch
- Special considerations for disconnected environments
- User expectations
- Upgrade from previous release considerations

### 5. Out-of-Scope
Define the boundaries of the feature. List items that are Out-of-Scope.

### 6. Acceptance Criteria
What must be true for this feature to be considered complete? Document clear, testable outcomes that define "done."

**Suggested format:**
- Given [context or precondition]
- When [action taken]
- Then [expected outcome]

### 7. Risks & Assumptions
- **Risks**: Potential blockers or threats to successful delivery
- **Assumptions**: Conditions believed to be true but needing validation

### 8. Supporting Documentation
Provide links (not copies) to:
- Designs
- Workflows
- Wireframes
- Discovery notes
- Technical documentation

### 9. Additional Clarifying Information
Add any other information that would further clarify the requirement and aid delivery teams in understanding the full context.

## New Feature/Component Prerequisites & Dependencies

### ODH/RHOAI Build Process Onboarding
**Will this feature require onboarding of a new container Image or component?** YES / NO

If YES, follow these instructions and email team-ai-core-platform@redhat.com:
- **DevPreview**: Clone RHOAIENG-31244
- **TechPreview**: Clone RHOAIENG-31290
- **GA**: Clone RHOAIENG-31303

### License Validation
**Will this feature require bringing in new upstream projects or sub-projects?** YES / NO

If YES:
- Check licensing for the project (preference: Apache 2.0)
- If Apache License cannot be obtained, post specific reason and required license in forum-openshift-ai-architecture for approval

### Accelerator/Package Support
**Does this feature require support from the AIPCC team?** YES / NO

Questions to identify:
- Are there any new or updated package requests?
  - If yes, follow instructions in AIPCC-1 and clone/populate the ticket
  - Attach the new epic to the STRAT feature
- Which accelerators should be supported or is this for a new accelerator?
- Any other AIPCC work needed (new variant, new image for RHAIIS, etc.)?
  - Open a new Feature in the AIPCC project
  - Fill in the template
  - Attach Feature to RHAISTRAT issue with "depends on" issue link

### Architecture Review Check
- **Does the feature have the label "requires_architecture_review"?** YES / NO
- **Does the related RFE indicate "Requires architecture review: YES"?** YES / NO

If YES to either:
- Feature design MUST be reviewed at the OpenShift AI Architecture Forum before the team commits to a specific solution
- This ensures alignment with overall product vision and provides architectural visibility
- Teams may still conduct spikes or research activities prior to formal review

### Additional Dependencies
Include any other prerequisites or dependencies needed to deliver this feature.

## High Level Plan

### Team Delivery Table

| Team | Start Date | Work to Deliver (EPIC) | Team Dependencies | T-Shirt Size | Approval/Comments |
|------|------------|------------------------|-------------------|--------------|-------------------|
| team-ai-core-platform | | | | | |
| [Additional teams...] | | | | | |

**Team Dependencies**: Describe any support, work, or input needed from other teams

**T-Shirt Size Estimate Scale:**
- **XS**: < 1 sprint
- **S**: 1 sprint (3 weeks)
- **M**: 2 sprints (6 weeks)
- **L**: 3 sprints (9 weeks) - Highly recommend breaking down into multiple features
- **XL**: 4 sprints (12 weeks) - Too big! Break it down!

*Note: Do not include time spent waiting on upstream or other teams, just the size of work done by OpenShift AI stakeholders.*

**Approval/Comments**: Add name/date if approved or note what is needed

## Engaging Documentation and UXD Teams

### Documentation Team
1. Add "Documentation" component to the feature
2. Set "Product Documentation Required" field to Yes
3. Add docs team to the High Level Plan table
4. Review the [Docs Intake Process](https://docs.google.com/document/d/1G_LKipII0DMX3UxpkxVEpgM9Pk5tHcfZdvnkjn9E1mI/edit?tab=t.0)
5. Flag any new features and enhancements for Release Notes

### UXD Team
1. Add "UXD" component to the feature
2. Add UXD team to the High Level Plan table
3. Reach out to:
   - Jenn Giardino: jgiardin@redhat.com
   - Beau Morley: bmorley@redhat.com

## Feature Owner Responsibilities

### Initial Setup
1. Link feature refinement document in Jira Feature
2. [Optional] Create public Slack channel for cross-team discussion
3. Collaborate with team leads to confirm POCs from each team
4. Update document status to "In Progress"

### Communication
Announce the feature via email to:
- All teams responsible for impacted components
- aipcc-eng-directs
- inference-ai-eng
- team-psap@redhat.com
- team-ai-core-platform@redhat.com
- ai-bu@redhat.com
- openshift-ai-docs@redhat.com
- ai-ux-all@redhat.com
- rhai-service-teams@redhat.com
- openshift-ai-devtestops@redhat.com
- openshift-ai-qe@redhat.com
- dramseur@redhat.com

### Review Process
1. Schedule meeting to review refinement document with delivery teams
2. Answer questions and discuss risks/concerns
3. Team members submit questions via document comments or Slack
4. Complete team review and define high-level delivery plan
5. Ensure every contributing team defines at least one Epic

### Finalization
1. Verify all impacted components are listed in Jira Feature's Components field
2. Remind teams to populate Epic's Parent Link field with Feature link
3. Address all comments and update document
4. Confirm team approvals in Approval/Comments column
5. Set document status to "Approved"
6. Change permissions to Read-Only

## Delivery Owner Responsibilities

### Accepting Work
1. Agree to the "why" and "what" is to be delivered
2. Coordinate creation of tracked work for all participating teams
3. Ensure all participating teams have signed off
4. Verify Definition of Ready has been met

### Communication
1. Announce to broader organization that feature development will begin

## Key Feature Owner Tasks Summary

| Task | Responsible |
|------|-------------|
| Clarify requirements and define "why" | Feature Owner |
| Provide detailed user stories and specs | Feature Owner |
| Set up review meetings | Feature Owner |
| Collaborate with development teams | Feature Owner |
| Manage stakeholder expectations | Feature Owner |
| Act as primary stakeholder contact | Feature Owner |
| Announce new features | Feature Owner |
| Agree to scope and deliverables | Delivery Owner |
| Coordinate tracked work creation | Delivery Owner |
| Ensure team sign-off and Definition of Ready | Delivery Owner |
| Announce feature development start | Delivery Owner |

## Document Storage

Add your feature refinement document to the feature refinement documents folder:
[Feature Refinement Documents Folder](https://drive.google.com/drive/folders/1SZjUobSqm4t8etx9nVY0agPhH4Wu0IuS?usp=drive_link)
