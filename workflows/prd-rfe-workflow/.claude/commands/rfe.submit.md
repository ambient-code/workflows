---
description: Submit RFEs to Jira for implementation planning and team assignment.
displayName: rfe.submit
icon: 🎫
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

This command submits RFEs to Jira for implementation planning. It should be run after `/rfe.breakdown` and optionally after `/rfe.prioritize`.

**IMPORTANT: Agent Collaboration**

You MUST proactively invoke the following collaborating agents to ensure proper RFE submission:

1. **@olivia-product_owner.md** (from bullpen) - For backlog prioritization, sprint planning, and ticket structure
2. **@emma-engineering_manager.md** (from bullpen) - For team assignment, capacity allocation, and delivery coordination
3. **@parker-product_manager.md** - For roadmap alignment and stakeholder communication

Invoke these agents at the start of the submission process. Work collaboratively with them to ensure tickets are properly structured, prioritized, and assigned.

1. **Load Context**:
   - Read `rfes.md` (RFE master list)
   - Read all individual RFE files from `rfe-tasks/` directory
   - Check if prioritization document exists (`prioritization.md`)
   - Consider user input from $ARGUMENTS

2. **Check Jira MCP Server Availability**:
   - Attempt to detect if Jira MCP server is available
   - If available, proceed with automated ticket creation (Step 3)
   - If not available, provide manual submission instructions (Step 4)

3. **Automated Jira Ticket Creation** (if Jira MCP available):
   
   For each RFE in the master list:
   
   a. **Read RFE File**:
      - Load `rfe-tasks/RFE-XXX-[slug].md`
      - Extract key information:
        - RFE ID and title
        - Summary
        - Priority and size
        - Acceptance criteria
        - Dependencies
        - User stories
        - Technical approach (if available)
   
   b. **Create Jira Ticket**:
      - Use Jira MCP server to create a ticket
      - Map RFE fields to Jira fields:
        - **Title**: `RFE-XXX: [RFE Title]`
        - **Description**: 
          - Summary section
          - Problem Statement
          - Proposed Solution (high-level)
          - Link to full RFE document
        - **Issue Type**: "Story" or "Task" (or as configured)
        - **Priority**: Map from RFE priority (High/Medium/Low → Jira priority levels)
        - **Labels**: Add "RFE", RFE ID, and any relevant tags
        - **Acceptance Criteria**: Include all acceptance criteria from RFE
        - **Dependencies**: Link to prerequisite RFE tickets if they exist
        - **Attachments**: Optionally attach the full RFE markdown file
      
   c. **Link Related Tickets**:
      - If dependencies exist, create links between tickets
      - Link tickets that are part of the same epic or phase
   
   d. **Create Epic or Parent Ticket** (if applicable):
      - If RFEs are grouped by epic, create or link to epic tickets
      - Set up parent-child relationships if needed
   
   e. **Report Ticket Creation**:
      - Document created ticket keys (e.g., PROJ-123, PROJ-124)
      - Create a mapping file: `jira-tickets.md` with:
        ```markdown
        # Jira Ticket Mapping
        
        | RFE ID | Jira Ticket | Title | Status |
        |--------|------------|-------|--------|
        | RFE-001 | PROJ-123 | [Title] | Created |
        | RFE-002 | PROJ-124 | [Title] | Created |
        ```

4. **Manual Submission Instructions** (if Jira MCP not available):
   
   Provide clear instructions to the user:
   
   ```markdown
   ## Manual Jira Ticket Submission
   
   The Jira MCP server is not currently available. Please manually create Jira tickets using the RFE files.
   
   ### RFE Files Location
   
   All RFE files are located in:
   ```
   artifacts/rfe-tasks/
   ```
   
   ### RFE Master List
   
   The complete list of RFEs with summaries is in:
   ```
   artifacts/rfes.md
   ```
   
   ### Steps to Create Jira Tickets
   
   1. **Open Jira** and navigate to your project board
   
   2. **For each RFE file** in `rfe-tasks/`:
      
      a. Click "Create" to create a new ticket
      
      b. **Set Ticket Fields**:
         - **Title**: Copy the RFE title (e.g., "RFE-001: [Title]")
         - **Issue Type**: Select "Story" or "Task"
         - **Priority**: Map from RFE priority
            - High → Highest/High
            - Medium → Medium
            - Low → Low/Lowest
      
      c. **Description**: Copy and paste from the RFE file:
         - Summary section
         - Problem Statement
         - Proposed Solution (Core Requirements)
         - User Stories
      
      d. **Acceptance Criteria**: Copy all acceptance criteria from the RFE file
      
      e. **Attachments**: Attach the full RFE markdown file (`RFE-XXX-[slug].md`)
      
      f. **Labels**: Add "RFE" and the RFE ID (e.g., "RFE-001")
      
      g. **Dependencies**: 
         - If the RFE has prerequisites, link to those tickets
         - Reference the "Prerequisite RFEs" section in the RFE file
      
      h. **Save** the ticket
   
   3. **Link Related Tickets**:
      - If RFEs have dependencies, create links between tickets
      - Use Jira's "Links" feature to connect prerequisite and blocking tickets
   
   4. **Create Epics** (if applicable):
      - If RFEs are grouped by epic (check `rfes.md` for phase/epic groupings)
      - Create epic tickets and link related RFE tickets to them
   
   5. **Verify Submission**:
      - Check that all RFEs from `rfes.md` have corresponding Jira tickets
      - Verify dependencies are properly linked
      - Confirm acceptance criteria are included
   
   ### Quick Reference
   
   - **Total RFEs**: Check `rfes.md` for count
   - **RFE Files**: `rfe-tasks/RFE-*.md`
   - **Prioritization**: If available, check `prioritization.md` for recommended order
   ```

5. **Validate Submission**:
   - Verify all RFEs have been submitted (check count matches master list)
   - Confirm critical RFEs (P0/high priority) are included
   - Check that dependencies are properly documented or linked

6. **Report Completion**:
   - Summary of submitted RFEs
   - Ticket keys or file locations (depending on method)
   - Next steps for the team (sprint planning, assignment, etc.)

## Guidelines

- **Jira MCP Integration**: When available, use the MCP server to automate ticket creation and ensure consistency
- **Ticket Format**: Maintain consistency in ticket titles, descriptions, and field mappings
- **Dependencies**: Always properly link dependent tickets to maintain traceability
- **Acceptance Criteria**: Include all acceptance criteria from RFE files in Jira tickets
- **Attachments**: Attach full RFE markdown files to tickets for complete context
- **Epic Organization**: Group related RFEs under epics when appropriate
- **Manual Fallback**: Provide clear, actionable instructions when automation isn't available

## Error Handling

- If Jira MCP is available but connection fails:
  - Report the error clearly
  - Provide manual submission instructions as fallback
  - Suggest checking Jira credentials or MCP server configuration

- If RFE files are missing:
  - Report which RFEs are missing
  - Suggest running `/rfe.breakdown` first if needed
  - Provide list of expected RFE files

- If ticket creation partially fails:
  - Report which tickets were created successfully
  - Report which tickets failed
  - Provide instructions for manually creating the failed tickets

