---
description: Break down the PRD into actionable Request for Enhancement (RFE) items.
displayName: RFE Breakdown
icon: 🔨
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

This command breaks down the PRD into discrete RFE items. It should be run after `/prd.create`.

1. **Load Context**:
   - Read `artifacts/prd.md`
   - Understand functional requirements, user stories, and features
   - Consider user input from $ARGUMENTS

2. **Analyze PRD for RFE Extraction**:
   - Review all functional requirements
   - Review all user stories and epics
   - Identify discrete, implementable units of work
   - Group related requirements into logical RFEs

3. **Create RFE Master List**: Generate `artifacts/rfes.md`:

   ```markdown
   # Request for Enhancement (RFE) List

   **Source PRD**: [Link to prd.md]
   **Date**: [Current Date]
   **Total RFEs**: [Count]

   ## Summary

   This document breaks down the PRD into discrete, implementable RFE items. Each RFE represents a unit of work that can be independently developed, tested, and delivered.

   ## RFE Overview

   | RFE ID | Title | Epic | Priority | Size | Status |
   |--------|-------|------|----------|------|--------|
   | RFE-001 | [Title] | [Epic name] | High/Med/Low | S/M/L/XL | Not Started |

   ## Detailed RFEs

   ### RFE-001: [Title]

   **Epic**: [Parent epic from PRD]
   **Priority**: High/Medium/Low
   **Estimated Size**: Small/Medium/Large/XLarge
   **Dependencies**: [RFE-XXX, RFE-YYY]
   **Related User Stories**: [Story IDs from PRD]

   #### Description
   [Clear description of what this RFE delivers]

   #### Scope
   **In Scope:**
   - [Specific deliverable 1]
   - [Specific deliverable 2]

   **Out of Scope:**
   - [What's not included]

   #### Requirements
   - REQ-1: [Specific requirement from PRD]
   - REQ-2: [Specific requirement from PRD]

   #### Acceptance Criteria
   - [ ] [Testable criterion 1]
   - [ ] [Testable criterion 2]
   - [ ] [Testable criterion 3]

   #### Technical Notes
   [High-level technical considerations, integration points, or constraints]

   #### Testing Requirements
   - [Type of testing needed]
   - [Key scenarios to test]

   #### Success Metrics
   - [How to measure success]

   ---

   [Repeat for each RFE]

   ## RFE Grouping & Sequencing

   ### Phase 1: Foundation
   - RFE-001: [Foundation item 1]
   - RFE-002: [Foundation item 2]

   ### Phase 2: Core Features
   - RFE-003: [Core feature 1]
   - RFE-004: [Core feature 2]

   ### Phase 3: Enhancement
   - RFE-005: [Enhancement 1]

   ## Dependency Graph

   ```
   RFE-001 (Foundation)
   ├── RFE-003 (depends on 001)
   └── RFE-004 (depends on 001)
       └── RFE-006 (depends on 004)
   ```

   ## Effort Summary

   | Size | Count | RFE IDs |
   |------|-------|---------|
   | Small | X | RFE-001, RFE-003 |
   | Medium | X | RFE-002, RFE-005 |
   | Large | X | RFE-004 |
   | XLarge | X | RFE-006 |

   **Total Estimated Effort**: [Sum of all sizes]
   ```

4. **Generate Individual RFE Documents**:
   - Create `artifacts/rfe-tasks/` directory
   - For each RFE, create `artifacts/rfe-tasks/RFE-XXX-[slug].md`:

   ```markdown
   # RFE-XXX: [Title]

   **Status**: Not Started
   **Priority**: [High/Medium/Low]
   **Size**: [S/M/L/XL]
   **Created**: [Date]
   **PRD Reference**: [Link to prd.md section]

   ## Overview

   [Description of what this RFE delivers]

   ## Related User Stories

   - [User Story 1 from PRD]
   - [User Story 2 from PRD]

   ## Requirements

   ### Functional Requirements
   - FR-XXX: [Requirement from PRD]
   - FR-YYY: [Requirement from PRD]

   ### Non-Functional Requirements
   - NFR-XXX: [Performance, security, etc.]

   ## Acceptance Criteria

   - [ ] [Testable criterion 1]
   - [ ] [Testable criterion 2]
   - [ ] [Testable criterion 3]

   ## Scope

   ### In Scope
   - [What IS included]

   ### Out of Scope
   - [What is NOT included]

   ## Dependencies

   ### Prerequisite RFEs
   - RFE-XXX: [What must be done first]

   ### Blocks RFEs
   - RFE-YYY: [What depends on this]

   ### External Dependencies
   - [System/API/Team dependency]

   ## Technical Approach (High-Level)

   [Brief technical overview - can be refined during implementation]

   ### Integration Points
   - [System/Component 1]
   - [System/Component 2]

   ### Data Considerations
   - [Data models or migrations needed]

   ## Testing Strategy

   ### Unit Tests
   - [Key areas to unit test]

   ### Integration Tests
   - [Integration scenarios]

   ### E2E/Acceptance Tests
   - [End-to-end scenarios matching acceptance criteria]

   ## Success Metrics

   - [Metric 1]: [Target]
   - [Metric 2]: [Target]

   ## Implementation Notes

   [Space for notes during implementation]

   ## Open Questions

   - [Question 1]

   ## Risks & Mitigation

   | Risk | Impact | Mitigation |
   |------|--------|------------|
   | [Risk 1] | [High/Med/Low] | [How to address] |
   ```

5. **RFE Breakdown Principles**:
   - **Atomic**: Each RFE should be independently deliverable
   - **Sized Appropriately**: Not too large (>2 weeks) or too small (<2 days)
   - **Testable**: Clear acceptance criteria
   - **Traceable**: Link back to PRD requirements
   - **Sequenced**: Dependencies identified
   - **Valuable**: Each RFE delivers user/business value

6. **Size Estimation Guidelines**:
   - **Small (S)**: 1-3 days, simple feature, minimal dependencies
   - **Medium (M)**: 3-5 days, moderate complexity, some integration
   - **Large (L)**: 5-10 days, complex feature, multiple integrations
   - **XLarge (XL)**: 10+ days, should consider breaking down further

7. **Validate RFE Breakdown**:
   - All PRD requirements are covered by RFEs
   - No RFE is too large (consider splitting XL items)
   - Dependencies are acyclic (no circular dependencies)
   - Each RFE has clear acceptance criteria
   - Priorities align with business goals

8. **Report Completion**:
   - Path to RFE master list
   - Count of RFEs by priority and size
   - Total estimated effort
   - Dependency summary
   - Next step: run `/rfe.prioritize`

## Guidelines

- Break down by value delivery, not technical layers
- Each RFE should deliver something testable
- Consider dependencies when creating RFEs
- Keep RFEs focused and scoped
- Include both functional and testing requirements
- Make acceptance criteria specific and measurable
