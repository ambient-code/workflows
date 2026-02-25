---
description: Submit Features to Jira for implementation planning and team assignment.
displayName: feature.submit
icon: 🎫
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

This command submits Features to Jira for implementation planning. It should be run after `/feature.breakdown` and optionally after `/feature.prioritize`.

**IMPORTANT: Agent Collaboration**

You MUST proactively invoke the following collaborating agents to ensure proper Feature submission:

1. **@olivia-product_owner.md** (from bullpen) - For backlog prioritization, sprint planning, and ticket structure
2. **@emma-engineering_manager.md** (from bullpen) - For team assignment, capacity allocation, and delivery coordination
3. **@parker-product_manager.md** - For roadmap alignment and stakeholder communication

Invoke these agents at the start of the submission process. Work collaboratively with them to ensure tickets are properly structured, prioritized, and assigned.

1. **Load Context**:
   - Read `features.md` (Feature master list)
   - Read all individual Feature files from `feature-tasks/` directory
   - Check if prioritization document exists (`prioritization.md`)
   - Consider user input from $ARGUMENTS

2. **Check Jira MCP Server Availability**:
   - Attempt to detect if Jira MCP server is available
   - If available, proceed with automated ticket creation (Step 3)
   - If not available, provide manual submission instructions (Step 4)

3. **Automated Jira Ticket Creation** (if Jira MCP available):

   For each Feature in the master list:

   a. **Read Feature File**:
      - Load `feature-tasks/Feature-XXX-[slug].md`
      - Extract key information:
        - Feature ID and title
        - Summary
        - Priority and size
        - Acceptance criteria
        - Dependencies
        - Technical notes

   b. **Create Jira Ticket**:
      ```json
      {
        "summary": "Feature-XXX: [Title from Feature]",
        "description": {
          "type": "doc",
          "content": [
            {
              "type": "paragraph",
              "content": [
                {"type": "text", "text": "[Feature Summary]"}
              ]
            },
            {
              "type": "heading",
              "attrs": {"level": 2},
              "content": [{"type": "text", "text": "Problem Statement"}]
            },
            {
              "type": "paragraph",
              "content": [
                {"type": "text", "text": "[Problem statement from Feature]"}
              ]
            },
            {
              "type": "heading",
              "attrs": {"level": 2},
              "content": [{"type": "text", "text": "Acceptance Criteria"}]
            },
            {
              "type": "bulletList",
              "content": [
                {
                  "type": "listItem",
                  "content": [
                    {
                      "type": "paragraph",
                      "content": [{"type": "text", "text": "[Criterion 1]"}]
                    }
                  ]
                }
              ]
            },
            {
              "type": "heading",
              "attrs": {"level": 2},
              "content": [{"type": "text", "text": "Technical Notes"}]
            },
            {
              "type": "paragraph",
              "content": [
                {"type": "text", "text": "[Technical approach and considerations]"}
              ]
            }
          ]
        },
        "priority": "[High/Medium/Low based on Feature priority]",
        "labels": ["feature", "prd-derived", "[size]", "[epic-name]"],
        "customFields": {
          "Story Points": "[Convert S=1, M=3, L=5, XL=8]",
          "Epic Link": "[Epic from PRD if available]",
          "Team": "[Team assignment if specified]"
        }
      }
      ```

   c. **Link Dependencies**:
      - For each dependency listed in Feature file
      - Find corresponding Jira ticket
      - Create "blocks"/"blocked by" link

   d. **Attach Feature File**:
      - Attach the complete Feature markdown file to ticket
      - This provides full technical specification for implementation

4. **Manual Submission Instructions** (if no Jira MCP):

   Generate `jira-submission-guide.md`:

   ```markdown
   # Jira Ticket Creation Guide

   **Features Ready for Submission**: [Count]
   **Source Documents**: features.md, feature-tasks/*.md

   ## Quick Setup

   1. **Create Epic** (if not exists):
      - **Summary**: [PRD Title]
      - **Description**: Link to PRD and overview
      - **Labels**: epic, prd

   2. **Set up Components/Labels**:
      - Labels: feature, prd-derived, [team-name]
      - Components: [relevant product areas]

   ## Individual Ticket Creation

   ### Feature-001: [Title]

   **Create New Story/Task in Jira**:

   **Summary**: Feature-001: [Feature Title]

   **Description**:
   ```
   ## Summary
   [Feature summary from Feature file]

   ## Problem Statement
   [Problem statement from Feature file]

   ## Acceptance Criteria
   - [ ] [Criterion 1]
   - [ ] [Criterion 2]
   - [ ] [Criterion 3]

   ## Technical Notes
   [Technical approach and considerations]

   ## Dependencies
   - Blocks: [List of dependent Feature IDs]
   - Depends on: [List of prerequisite Feature IDs]

   ## Reference
   Feature File: feature-tasks/Feature-001-[slug].md
   PRD: prd.md
   ```

   **Fields to Set**:
   - **Priority**: [High/Medium/Low]
   - **Story Points**: [S=1, M=3, L=5, XL=8]
   - **Epic Link**: [Epic key]
   - **Labels**: feature, prd-derived, [size], [team]
   - **Assignee**: [Team/Individual if known]
   - **Sprint**: [Current/Future sprint if planned]

   **Attachments**:
   - Upload: feature-tasks/Feature-001-[slug].md

   ---

   [Repeat for each Feature]

   ## Dependency Linking

   After all tickets are created:

   1. **Feature-001** (Foundation):
      - Link as "blocks" → Feature-003, Feature-004

   2. **Feature-003** (Depends on 001):
      - Link as "is blocked by" → Feature-001

   3. **Feature-005** (Depends on 003):
      - Link as "is blocked by" → Feature-003

   ## Backlog Organization

   ### Sprint Planning Order

   **Sprint 1**: Foundation Features
   - Feature-001 (High priority, no dependencies)
   - Feature-002 (Medium priority, independent)

   **Sprint 2**: Core Features
   - Feature-003 (Depends on Feature-001)
   - Feature-004 (Independent, medium priority)

   **Sprint 3**: Enhancement Features
   - Feature-005 (Depends on Feature-003)
   - Feature-006 (Low priority)

   ## Team Assignment

   Based on feature complexity and team skills:

   - **Frontend Team**: Feature-001, Feature-004 (UI-heavy)
   - **Backend Team**: Feature-002, Feature-003 (API/service work)
   - **Full-Stack Team**: Feature-005 (mixed requirements)

   ## Estimation Validation

   Review and adjust story points during planning poker:

   | Feature | Initial Estimate | Team Estimate | Notes |
   |---------|------------------|---------------|-------|
   | Feature-001 | 3 | [TBD] | [Team feedback] |
   | Feature-002 | 5 | [TBD] | [Team feedback] |
   ```

5. **Create Feature-to-Jira Mapping Document**: Generate `jira-tickets.md`:

   ```markdown
   # Feature to Jira Ticket Mapping

   **Created**: [Date]
   **Method**: [Automated/Manual]
   **Total Features**: [Count]

   ## Ticket Mapping

   | Feature ID | Jira Ticket | Title | Priority | Status |
   |------------|-------------|-------|----------|--------|
   | Feature-001 | [PROJ-123] | [Feature Title] | High | Created |
   | Feature-002 | [PROJ-124] | [Feature Title] | Medium | Created |
   | Feature-003 | [PROJ-125] | [Feature Title] | High | Created |

   ## Epic Mapping

   | Epic Name | Jira Epic | Features Included |
   |-----------|-----------|-------------------|
   | [Epic 1] | [PROJ-100] | Feature-001, Feature-002 |
   | [Epic 2] | [PROJ-101] | Feature-003, Feature-004 |

   ## Dependency Links

   | Feature | Blocks | Blocked By |
   |---------|--------|------------|
   | Feature-001 | Feature-003, Feature-004 | None |
   | Feature-003 | Feature-005 | Feature-001 |

   ## Next Steps

   - [ ] Review tickets with development team
   - [ ] Validate story point estimates
   - [ ] Assign to appropriate team members
   - [ ] Schedule for upcoming sprints
   - [ ] Set up automated notifications
   - [ ] Create sprint goals aligned with Feature priorities
   ```

6. **Validation and Quality Check**:
   - Verify all Features from master list have corresponding tickets/instructions
   - Check that dependencies are properly linked
   - Ensure ticket descriptions contain all necessary information
   - Validate priority alignment with prioritization document

7. **Report Completion**:
   - Summary of tickets created/instructions provided
   - Path to Jira mapping document
   - Next steps for development team
   - Recommended sprint planning approach

## Submission Guidelines

### Ticket Quality Standards
- **Summary**: Clear, action-oriented feature description
- **Description**: Includes problem statement, acceptance criteria, and technical notes
- **Acceptance Criteria**: Testable, specific, measurable
- **Dependencies**: All blocking/blocked relationships mapped
- **Attachments**: Complete Feature specification file attached

### Priority Mapping
- **High Priority**: Critical path features, MVP requirements
- **Medium Priority**: Important but not blocking features
- **Low Priority**: Nice-to-have features for later phases

### Story Point Guidelines
- **1 Point (S)**: Simple feature, 1-3 days, minimal integration
- **3 Points (M)**: Moderate feature, 3-5 days, some complexity
- **5 Points (L)**: Complex feature, 5-8 days, significant integration
- **8 Points (XL)**: Very complex, 8+ days, consider breaking down

### Label Standards
- **feature**: Identifies ticket as feature (vs. bug/task)
- **prd-derived**: Indicates ticket originated from PRD process
- **[size]**: s, m, l, xl for quick size identification
- **[team]**: frontend, backend, fullstack, etc.
- **[epic-name]**: Short epic identifier for grouping