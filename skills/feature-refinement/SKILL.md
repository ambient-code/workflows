---
name: feature-refinement
description: Guides users through the complete feature refinement process for Red Hat AI products (RHOAI, RHAIIS, RHEL AI). Creates a structured feature refinement document with all required sections including feature overview, requirements, dependencies, team plans, and approval tracking. Use when users need to refine, document, or plan a new product feature.
---

# Feature Refinement Skill

This skill helps you create a comprehensive feature refinement document following Red Hat AI's template and process.

## When to Use This Skill

Use this skill when:
- Creating a new feature refinement document for RHOAI, RHAIIS, or RHEL AI
- Documenting feature requirements and acceptance criteria
- Planning cross-team feature delivery
- Preparing features for engineering review

## Feature Refinement Process

### Step 1: Gather Initial Information

Ask the user for the following information to populate the feature refinement document:

**Required Information:**
1. **Feature Jira Link** - Link to the STRAT feature (XXXSTRAT-####)
2. **Feature Title** - Name of the feature for the document title
3. **Product** - RHOAI (managed or self-managed), RHAIIS, or RHEL AI
4. **Feature Owner** - Person responsible for requirements (typically Product Manager)
5. **Delivery Owner** - Person responsible for delivery (typically Engineering Manager or Staff Architect)

**Optional Information:**
- Slack Channel/Thread for discussion
- RFE Council Reviewer

### Step 2: Define Feature Details

Work with the user to complete each section. Ask clarifying questions as needed:

#### Feature Overview
- Who benefits from this feature (persona/user role)?
- What is the current state vs. the desired state with this feature?
- High-level user narrative: How and when would users use this functionality?

#### The Why
- Why now? What business value does this bring?
- What types of customers will benefit?
- What supporting data exists?
- If assumptive (not data-driven), what are the success metrics?

#### High Level Requirements
Format as user stories:
- As a [user role/persona]
- I want [capability/feature]
- So that [benefit/business value]

Focus only on mandatory requirements for initial release.

#### Non-Functional Requirements
Consider:
- Performance parameters
- Security concerns
- Disconnected environment requirements
- User expectations
- Upgrade considerations from previous releases

#### Out-of-Scope
Define clear boundaries - what is NOT included in this feature.

#### Acceptance Criteria
Format as Given-When-Then:
- Given [context or precondition]
- When [action taken]
- Then [expected outcome]

#### Risks & Assumptions
- **Risks**: Potential blockers or threats to delivery
- **Assumptions**: Conditions believed true but needing validation

#### Supporting Documentation
Gather links to:
- Designs and wireframes
- Workflows and user flows
- Discovery notes
- Technical documentation

### Step 3: Verify Prerequisites & Dependencies

Check and document the following:

#### New Feature/Component Prerequisites

1. **ODH/RHOAI Build Process Onboarding**
   - Will this require a new container image or component? (YES/NO)
   - If YES, reference onboarding epics:
     - DevPreview: RHOAIENG-31244
     - TechPreview: RHOAIENG-31290
     - GA: RHOAIENG-31303
   - Email: team-ai-core-platform@redhat.com for questions

2. **License Validation**
   - Will this bring in new upstream projects/sub-projects? (YES/NO)
   - If YES: Verify licensing (preference: Apache 2.0)
   - If non-Apache: Post justification in forum-openshift-ai-architecture

3. **Accelerator/Package Support**
   - Does this require AIPCC team support? (YES/NO)
   - New/updated package requests? Follow AIPCC-1 instructions
   - Which accelerators should be supported?
   - Create AIPCC Feature and link with "depends on"

4. **Architecture Review Check**
   - Does feature have "requires_architecture_review" label? (YES/NO)
   - Does RFE indicate "Requires architecture review: YES"? (YES/NO)
   - If YES to either: Must be reviewed at OpenShift AI Architecture Forum before commitment

5. **Additional Dependencies**
   - Document any other prerequisites needed

### Step 4: Create High-Level Delivery Plan

Build a table with the following for each team involved:

| Team | Start Date | Work to Deliver (EPIC) | Team Dependencies | T-Shirt Size | Approval/Comments |
|------|------------|------------------------|-------------------|--------------|-------------------|

**T-Shirt Size Scale:**
- XS: < 1 sprint
- S: 1 sprint (3 weeks)
- M: 2 sprints (6 weeks)
- L: 3 sprints (9 weeks) - Consider breaking down
- XL: 4 sprints (12 weeks) - Too big, must break down

**Note:** Always include team-ai-core-platform - they confirm if support is needed.

### Step 5: Documentation and UXD Engagement

**Documentation Team:**
- Add "Documentation" component to Jira feature
- Set "Product Documentation Required" to Yes
- Add docs team to delivery plan table
- Review [Docs Intake Process](https://docs.google.com/document/d/1G_LKipII0DMX3UxpkxVEpgM9Pk5tHcfZdvnkjn9E1mI/edit?tab=t.0)
- Flag for Release Notes if needed

**UXD Team:**
- Add "UXD" component to Jira feature
- Add UXD team to delivery plan table
- Contact: Jenn Giardino (jgiardin@redhat.com) or Beau Morley (bmorley@redhat.com)

### Step 6: Generate Document

Create a Google Doc or Markdown file with the complete feature refinement document using the gathered information.

**Document Status Flow:**
1. Start: "Not started"
2. During refinement: "In Progress"
3. After approval: "Approved" (set to Read-Only)

### Step 7: Feature Owner Next Steps

Remind the user of these follow-up actions:

1. **Link & Share:**
   - Link document in Jira Feature
   - Create public Slack channel for collaboration (optional)
   - Announce via email to all stakeholder teams

2. **Email Distribution List:**
   - All teams for impacted components
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

3. **Schedule Review Meeting:**
   - Review with all delivery teams
   - Answer questions and discuss risks/concerns
   - Use document comments or Slack for questions

4. **Finalize:**
   - Complete team reviews and delivery plan
   - Verify all components listed in Jira
   - Ensure EPICs have Parent Link to Feature
   - Address all comments
   - Get team approvals (Approval/Comments column)
   - Update document status to "Approved"
   - Set to Read-Only

## Key Roles & Responsibilities

**Feature Owner (typically Product Manager):**
- Define and clarify requirements
- Communicate the "why" behind the work
- Set up review meetings
- Manage stakeholder expectations
- Act as primary stakeholder contact
- Announce new features

**Delivery Owner (typically Engineering Manager/Staff Architect):**
- Agree to scope and deliverables
- Coordinate tracked work creation for all teams
- Ensure team sign-off and Definition of Ready
- Announce feature development start

## Tips for Success

- Be clear and specific in requirements
- Use the suggested formats (user stories, Given-When-Then)
- Break down large features (> 3 sprints)
- Verify all prerequisites early
- Engage documentation and UX teams early
- Get explicit team approvals before marking "Approved"
- Link all related epics properly in Jira
- Keep stakeholders informed throughout

## Output Format

Generate the feature refinement document in a structured format (Google Doc template or Markdown) with all sections populated based on the user's input. Use tables where specified in the template.
