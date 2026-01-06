---
description: Break down the PRD into actionable Request for Enhancement (RFE) items.
displayName: rfe.breakdown
icon: 🔨
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

This command breaks down the PRD into discrete RFE items. It should be run after `/prd.create`.

**IMPORTANT: Agent Collaboration**

You MUST proactively invoke the following collaborating agents to ensure comprehensive RFE breakdown:

1. **@olivia-product_owner.md** (from bullpen) - For backlog management, story decomposition, and acceptance criteria definition
2. **@stella-staff_engineer.md** - For technical scoping, effort estimation, and complexity assessment
3. **@archie-architect.md** (from bullpen) - For system design, dependencies, and architectural coordination
4. **@neil-test_engineer.md** (from bullpen) - For testability assessment, automation requirements, and cross-component impact analysis

Invoke these agents at the start of the breakdown process. Work collaboratively with them to decompose the PRD into well-scoped, technically feasible RFEs with proper sizing and dependencies.

1. **Load Context**:
   - Read `prd.md`
   - Understand functional requirements, user stories, and features
   - Consider user input from $ARGUMENTS

2. **Analyze PRD for RFE Extraction**:
   - Review all functional requirements
   - Review all user stories and epics
   - Identify discrete, implementable units of work
   - Group related requirements into logical RFEs

3. **Create RFE Master List**: Generate `rfes.md`:

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
   - Create `rfe-tasks/` directory (if it doesn't exist)
   - **IMPORTANT**: Create individual RFE files for ALL RFEs identified in the master list, not just a sample
   - **TEMPLATE**: Use the Red Hat RFE format template at `.claude/templates/rfe-template.md` as a guide
   - For EACH RFE in the breakdown, create `rfe-tasks/RFE-XXX-[slug].md` following the template structure:

   ```markdown
   # RFE-XXX: [Title]

   **Status**: Not Started
   **Priority**: [High/Medium/Low]
   **Size**: [S/M/L/XL]
   **Created**: [Date]
   **PRD Reference**: [Link to prd.md section]

   ## Summary

   [One to three sentences describing the enhancement. Should clearly state what is being extended, added, or modified, and who benefits from this change. Focus on the value delivered.]

   ## Background

   [Describe the current state of the system/feature. Explain what exists today and what limitations or gaps exist. Reference any relevant existing functionality.]

   ### Current State
   - [Current feature/component description]
   - [What information/functionality is currently available]

   ### Gaps and Limitations
   - [What is missing or insufficient]
   - [What users cannot currently see/do]
   - [Pain points with current implementation]

   ## Problem Statement

   [Clearly articulate the problem(s) this RFE addresses. Focus on user pain points and business impact. Use specific, measurable language when possible.]

   [Target User Persona] needs [capability/visibility/functionality] because [reason/impact]. The current [system/UI/feature] provides no indication of:

   - [Problem 1]: [Description]
   - [Problem 2]: [Description]

   ## Proposed Solution

   ### Core Requirements

   [High-level requirements that must be met. Focus on WHAT needs to be delivered, not HOW.]

   1. **Requirement 1**: [Description]
   2. **Requirement 2**: [Description]

   ### UI/UX Enhancements

   [If this RFE involves user interface changes, describe the enhancements in detail.]

   #### New Components/Columns/Views
   - **[Component Name]**: [Description]

   #### Status Indicators
   [If applicable, define status indicators and their meanings]

   ### Technical Approach (High-Level)

   [Brief technical overview - can be refined during implementation]

   #### Integration Points
   - [System/Component 1]: [How it integrates]

   #### Data Considerations
   - [Data models or migrations needed]

   ## User Stories

   [Organize user stories by persona or role. Use the standard format: "As a [persona], I want [goal] so that [benefit]."]

   ### As a [Persona 1]
   - I want to [action] so that [benefit]
   - I want to [action] so that [benefit]

   ### As a [Persona 2]
   - I want to [action] so that [benefit]

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

   ## Success Criteria

   [Measurable outcomes that indicate this RFE has achieved its goals. Should align with the problem statement and user stories.]

   - **Visibility**: [What users can now see/understand]
   - **Performance**: [Performance requirements or improvements]
   - **Usability**: [Usability goals or improvements]
   - **Scalability**: [How the solution handles scale]
   - **Integration**: [How well it integrates with existing systems]

   ## Success Metrics

   [Quantifiable metrics that will be tracked to measure success]

   - **[Metric 1]**: [Target value] - [How it's measured]
   - **[Metric 2]**: [Target value] - [How it's measured]

   ## Implementation Notes

   [Space for notes during implementation]

   ## Open Questions

   - [Question 1]

   ## Risks & Mitigation

   | Risk | Impact | Mitigation |
   |------|--------|------------|
   | [Risk 1] | [High/Med/Low] | [How to address] |
   ```

   **CRITICAL**: You MUST create individual RFE files for EVERY RFE identified in the master list. Do not create only a sample file. Each RFE from the master list must have its own corresponding file in the `rfe-tasks/` directory.

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
   - **VERIFY**: Every RFE in the master list has a corresponding individual file in `rfe-tasks/`

8. **Report Completion**:
   - Path to RFE master list (`rfes.md`)
   - Path to individual RFE files directory (`rfe-tasks/`)
   - Count of RFEs by priority and size
   - Total estimated effort
   - Dependency summary
   - Confirmation that ALL individual RFE files have been created (not just a sample)
   - Next step: run `/rfe.prioritize`

## Guidelines

- **Use the Red Hat RFE Template**: Reference `.claude/templates/rfe-template.md` when creating individual RFE files to ensure consistency with Red Hat's RFE format
- Break down by value delivery, not technical layers
- Each RFE should deliver something testable
- Consider dependencies when creating RFEs
- Keep RFEs focused and scoped
- Include both functional and testing requirements
- Make acceptance criteria specific and measurable
- Follow the template structure: Summary → Background → Problem Statement → Proposed Solution → User Stories → Acceptance Criteria → Success Criteria
- Adapt template sections as needed - not all sections are required for every RFE, but maintain the overall structure
