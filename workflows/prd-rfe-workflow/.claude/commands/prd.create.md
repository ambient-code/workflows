---
description: Create a comprehensive Product Requirements Document (PRD) from discovery and requirements.
displayName: prd.create
icon: 📄
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

This command creates the final PRD document. It should be run after `/prd.requirements`.

**IMPORTANT: Agent Collaboration**

You MUST proactively invoke the following collaborating agents to ensure high-quality PRD creation:

1. **@parker-product_manager.md** - For business requirements, value proposition, and ROI justification
2. **@ryan-ux_researcher.md** - For research-informed requirements with citations from studies. Ensure all requirements reference supporting research.
3. **@terry-technical_writer.md** - For documentation quality, clarity, and structure. This agent should review the PRD for readability and completeness.
4. **@casey-content_strategist.md** (from bullpen) - For content architecture and standards

Invoke these agents throughout the PRD creation process. Work collaboratively with them to synthesize discovery and requirements into a comprehensive, well-written PRD.

1. **Load Context**:
   - Read `discovery.md` if it exists
   - Read `requirements.md` if it exists
   - Consider user input from $ARGUMENTS

2. **Create PRD**: Generate `prd.md` with comprehensive structure:

   ```markdown
   # Product Requirements Document (PRD)

   ## Document Information

   **Product/Feature**: [Name]
   **Version**: 1.0
   **Date**: [Current Date]
   **Author**: [Your name/team]
   **Status**: Draft/In Review/Approved

   ## Executive Summary

   [2-3 paragraph overview of what this PRD covers, why it matters, and what success looks like]

   ## Problem Statement

   ### Current Situation
   [What is the current state?]

   ### Problem Description
   [What problem are we solving?]

   ### Impact
   [Who is affected and how?]

   ## Goals & Objectives

   ### Business Goals
   1. [Goal 1]
   2. [Goal 2]

   ### User Goals
   1. [Goal 1]
   2. [Goal 2]

   ### Success Metrics
   | Metric | Target | Measurement Method |
   |--------|--------|-------------------|
   | [Metric 1] | [Target value] | [How to measure] |
   | [Metric 2] | [Target value] | [How to measure] |

   ## Target Users

   ### Primary Personas

   #### Persona 1: [Name/Role]
   - **Description**: [Who they are]
   - **Needs**: [What they need]
   - **Pain Points**: [Current frustrations]
   - **Goals**: [What they want to achieve]

   ## User Stories & Use Cases

   ### Epic 1: [Epic Name]

   #### User Story 1.1: [Title]
   **As a** [user type]
   **I want to** [action]
   **So that** [benefit]

   **Acceptance Criteria:**
   - [ ] [Testable criterion 1]
   - [ ] [Testable criterion 2]

   **Priority**: High/Medium/Low
   **Effort**: Small/Medium/Large

   ### Use Case Scenarios

   #### Scenario 1: [Scenario Name]
   **Actor**: [User type]
   **Preconditions**: [What must be true before]
   **Main Flow**:
   1. [Step 1]
   2. [Step 2]
   3. [Step 3]

   **Postconditions**: [Expected outcome]
   **Alternative Flows**: [What could go differently]

   ## Functional Requirements

   ### Core Features

   #### Feature 1: [Feature Name]
   **ID**: FR-001
   **Description**: [What this feature does]
   **Priority**: Must Have/Should Have/Could Have/Won't Have
   **Dependencies**: [FR-XXX, FR-YYY]

   **Detailed Requirements:**
   - REQ-001.1: [Specific requirement]
   - REQ-001.2: [Specific requirement]

   **Acceptance Criteria:**
   - [ ] [Testable criterion 1]
   - [ ] [Testable criterion 2]

   ## Non-Functional Requirements

   ### Performance Requirements
   - [Requirement with measurable targets]

   ### Security Requirements
   - [Security considerations and compliance needs]

   ### Scalability Requirements
   - [Load and growth expectations]

   ### Usability Requirements
   - [UX standards and accessibility needs]

   ### Reliability Requirements
   - [Uptime, error handling, recovery]

   ## User Experience

   ### User Flows
   [Describe key user journeys]

   ### Wireframes/Mockups
   [Reference to design artifacts if available]

   ### Design Principles
   - [Principle 1]
   - [Principle 2]

   ## Technical Considerations

   ### Constraints
   - [Technical limitation 1]
   - [Technical limitation 2]

   ### Integration Points
   - [System/API 1]: [How it integrates]
   - [System/API 2]: [How it integrates]

   ### Data Requirements
   - [Data to be stored/processed]
   - [Data migration needs]

   ## Scope

   ### In Scope
   - [What we ARE building]

   ### Out of Scope
   - [What we are NOT building]
   - [Future considerations]

   ## Assumptions & Dependencies

   ### Assumptions
   - [Assumption 1]
   - [Assumption 2]

   ### Dependencies
   - [External dependency 1]
   - [Internal dependency 2]

   ## Risks & Mitigation

   | Risk | Probability | Impact | Mitigation Strategy |
   |------|-------------|--------|---------------------|
   | [Risk 1] | High/Med/Low | High/Med/Low | [How to address] |

   ## Timeline & Milestones

   | Milestone | Target Date | Description |
   |-----------|-------------|-------------|
   | [Milestone 1] | [Date] | [What's delivered] |

   ## Success Criteria

   ### Definition of Done
   - [ ] [Criterion 1]
   - [ ] [Criterion 2]

   ### Launch Criteria
   - [ ] [What must be true to launch]

   ## Appendix

   ### Glossary
   - **[Term 1]**: [Definition]
   - **[Term 2]**: [Definition]

   ### References
   - [Related document 1]
   - [Related document 2]

   ### Revision History

   | Version | Date | Author | Changes |
   |---------|------|--------|---------|
   | 1.0 | [Date] | [Name] | Initial draft |
   ```

3. **Generate PRD Content**:
   - Consolidate information from discovery and requirements
   - Write clear, comprehensive sections
   - Ensure all requirements are captured
   - Add measurable success metrics
   - Document assumptions and risks
   - Define clear scope boundaries

4. **Validate PRD Quality**:
   - **Completeness**: All sections filled appropriately
   - **Clarity**: Clear, unambiguous language
   - **Measurability**: Success criteria are quantifiable
   - **Testability**: Requirements can be validated
   - **Consistency**: No contradictions between sections

5. **Create PRD Validation Checklist**: Generate `prd-checklist.md`:

   ```markdown
   # PRD Quality Checklist

   **Document**: prd.md
   **Date**: [Current Date]

   ## Content Completeness
   - [ ] Executive summary clearly explains the initiative
   - [ ] Problem statement is well-defined
   - [ ] Goals and success metrics are measurable
   - [ ] Target users and personas are identified
   - [ ] User stories have acceptance criteria
   - [ ] All functional requirements are documented
   - [ ] Non-functional requirements are specified
   - [ ] Scope (in/out) is clearly defined

   ## Quality Standards
   - [ ] Requirements are specific and unambiguous
   - [ ] Acceptance criteria are testable
   - [ ] Success metrics are measurable
   - [ ] Assumptions are documented
   - [ ] Dependencies are identified
   - [ ] Risks are assessed with mitigation plans
   - [ ] No technical implementation details (focus on WHAT, not HOW)

   ## Stakeholder Readiness
   - [ ] PRD is ready for review
   - [ ] All open questions are resolved
   - [ ] Document is comprehensive enough for RFE breakdown

   ## Next Steps
   - [ ] Review PRD with stakeholders
   - [ ] Get PRD approval
   - [ ] Proceed to RFE breakdown (/rfe.breakdown)
   ```

6. **Report Completion**:
   - Path to PRD document
   - Key highlights summary
   - Validation results
   - Next step: run `/rfe.breakdown` when ready

## Guidelines

- PRDs should be comprehensive but readable
- Focus on WHAT and WHY, not HOW
- Use clear, non-technical language for business sections
- Make all criteria measurable and testable
- Document what's out of scope to manage expectations
- Include visual aids (tables, diagrams) where helpful
