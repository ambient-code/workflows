---
description: Gather and document detailed product requirements.
displayName: Requirements
icon: 📋
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

This command gathers detailed requirements based on the discovery phase. It should be run after `/prd.discover`.

1. **Load Context**:
   - Read `artifacts/discovery.md` if it exists
   - Consider user input from $ARGUMENTS

2. **Create Requirements Document**: Generate `artifacts/requirements.md`:

   ```markdown
   # Product Requirements: [Product/Feature Name]

   **Date**: [Current Date]
   **Status**: In Progress
   **Related**: [Link to discovery.md]

   ## Business Requirements

   ### Business Goals
   - [Goal 1]
   - [Goal 2]

   ### Success Criteria
   - [Measurable criterion 1]
   - [Measurable criterion 2]

   ### Constraints
   - [Constraint 1]
   - [Constraint 2]

   ## User Requirements

   ### User Stories

   #### Story 1: [Title]
   **As a** [user type]
   **I want to** [action]
   **So that** [benefit]

   **Acceptance Criteria:**
   - [ ] [Criterion 1]
   - [ ] [Criterion 2]

   ### User Flows

   #### Flow 1: [Flow Name]
   1. [Step 1]
   2. [Step 2]
   3. [Expected outcome]

   ## Functional Requirements

   ### Core Features

   #### FR-1: [Feature Name]
   **Description**: [What the feature does]
   **Priority**: [High/Medium/Low]
   **Dependencies**: [Other requirements]

   **Acceptance Criteria:**
   - [ ] [Testable criterion 1]
   - [ ] [Testable criterion 2]

   ## Non-Functional Requirements

   ### Performance
   - [Requirement 1]

   ### Security
   - [Requirement 1]

   ### Scalability
   - [Requirement 1]

   ### Accessibility
   - [Requirement 1]

   ## Out of Scope

   - [What we're NOT building]
   - [Features for future consideration]

   ## Assumptions & Dependencies

   ### Assumptions
   - [Assumption 1]

   ### Dependencies
   - [Dependency 1]

   ## Open Issues

   - [Issue 1]: [Status]
   ```

3. **Gather Requirements**:
   - Transform user needs into specific requirements
   - Write clear, testable acceptance criteria
   - Prioritize requirements (MoSCoW method: Must have, Should have, Could have, Won't have)
   - Identify dependencies and constraints

4. **Validate Requirements**:
   - Check that each requirement is:
     - Specific and unambiguous
     - Testable and verifiable
     - Achievable and realistic
     - Relevant to user/business goals
   - Ensure acceptance criteria are measurable

5. **Ask for Clarifications** (if needed):
   - Maximum 3-5 critical questions
   - Focus on ambiguous or missing information
   - Present options when multiple approaches are valid

6. **Report Completion**:
   - Path to requirements document
   - Summary of key requirements
   - Readiness assessment for PRD creation
   - Next step: run `/prd.create`

## Guidelines

- Requirements should be solution-agnostic (focus on WHAT, not HOW)
- Each requirement must be testable
- Use measurable success criteria
- Clearly define what's in scope and out of scope
- Document all assumptions
