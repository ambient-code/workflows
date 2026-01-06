---
description: Run the complete PRD-RFE workflow automatically from discovery to Jira submission, only pausing for critical questions.
displayName: rfe.speedrun
icon: ⚡
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty). The user input should contain the initial product idea or problem statement.

## Outline

This command automates the entire PRD-RFE workflow from discovery through Jira submission. It runs each phase sequentially, making intelligent decisions and only pausing to ask simplified, critical questions when absolutely necessary.

**Workflow Phases (in order)**:
1. `/prd.discover` - Product discovery
2. `/prd.requirements` - Requirements gathering
3. `/prd.create` - PRD creation
4. `/prd.review` - PRD review
5. `/prd.revise` - PRD revision (if needed, based on review)
6. `/rfe.breakdown` - RFE breakdown
7. `/rfe.review` - RFE review
8. `/rfe.revise` - RFE revision (if needed, based on review)
9. `/rfe.prioritize` - RFE prioritization
10. `/rfe.submit` - RFE submission to Jira

## Execution Strategy

### Phase 1: Discovery (`/prd.discover`)

1. **Execute Discovery**:
   - Run the discovery phase using the user's initial input
   - Invoke collaborating agents: @parker-product_manager.md, @ryan-ux_researcher.md, @aria-ux_architect.md
   - Generate `discovery.md`
   - Make reasonable assumptions when information is missing
   - Only ask questions if critical information is completely absent

2. **Critical Questions (only if needed)**:
   - "Who are the primary users?" (if not inferable from context)
   - "What is the main problem being solved?" (if not clear from input)
   - Maximum 2-3 questions total

3. **Proceed automatically** to requirements phase

### Phase 2: Requirements (`/prd.requirements`)

1. **Execute Requirements Gathering**:
   - Read `discovery.md`
   - Invoke collaborating agents: @parker-product_manager.md, @ryan-ux_researcher.md, @olivia-product_owner.md, @aria-ux_architect.md
   - Generate `requirements.md`
   - Use discovery insights to create requirements
   - Apply MoSCoW prioritization automatically

2. **Critical Questions (only if needed)**:
   - "Are there any specific technical constraints?" (if not mentioned)
   - "What is the target timeline?" (if critical for prioritization)
   - Maximum 1-2 questions total

3. **Proceed automatically** to PRD creation

### Phase 3: PRD Creation (`/prd.create`)

1. **Execute PRD Creation**:
   - Read `discovery.md` and `requirements.md`
   - Invoke collaborating agents: @parker-product_manager.md, @ryan-ux_researcher.md, @terry-technical_writer.md, @casey-content_strategist.md
   - Generate `prd.md` and `prd-checklist.md`
   - Synthesize all information into comprehensive PRD
   - Make reasonable assumptions for missing details

2. **No questions** - proceed directly to review

### Phase 4: PRD Review (`/prd.review`)

1. **Execute PRD Review**:
   - Read `prd.md`
   - Invoke collaborating agents: @steve-ux_designer.md, @aria-ux_architect.md, @olivia-product_owner.md, @archie-architect.md
   - Generate `prd-review-report.md`
   - Assess quality, completeness, and feasibility
   - Determine if prototype is needed

2. **Critical Questions (only if needed)**:
   - "Is a prototype needed before proceeding?" (if unclear from review)
   - Maximum 1 question

3. **Decision Point**: 
   - If review identifies critical issues → proceed to revision
   - If review is satisfactory → proceed to RFE breakdown

### Phase 5: PRD Revision (`/prd.revise`) - Conditional

1. **Only execute if review identified critical issues**:
   - Read `prd-review-report.md`
   - Invoke collaborating agents: @parker-product_manager.md, @terry-technical_writer.md
   - Update `prd.md` based on review feedback
   - Address all critical issues automatically
   - Make reasonable decisions on non-critical feedback

2. **No questions** - proceed to RFE breakdown

### Phase 6: RFE Breakdown (`/rfe.breakdown`)

1. **Execute RFE Breakdown**:
   - Read `prd.md`
   - Invoke collaborating agents: @olivia-product_owner.md, @stella-staff_engineer.md, @archie-architect.md, @neil-test_engineer.md
   - Generate `rfes.md` and individual RFE files in `rfe-tasks/`
   - Break down PRD into implementable RFEs
   - Size RFEs appropriately
   - Identify dependencies automatically

2. **No questions** - proceed to RFE review

### Phase 7: RFE Review (`/rfe.review`)

1. **Execute RFE Review**:
   - Read `rfes.md` and RFE files
   - Invoke collaborating agents: @stella-staff_engineer.md, @archie-architect.md, @neil-test_engineer.md, @emma-engineering_manager.md, @olivia-product_owner.md
   - Review all RFEs for technical feasibility, testability, and capacity
   - Assess architecture alignment
   - Identify any critical blockers

2. **Critical Questions (only if needed)**:
   - "Are there any team capacity constraints?" (if not already known)
   - Maximum 1 question

3. **Decision Point**:
   - If review identifies critical issues → proceed to revision
   - If review is satisfactory → proceed to prioritization

### Phase 8: RFE Revision (`/rfe.revise`) - Conditional

1. **Only execute if review identified critical issues**:
   - Read review feedback
   - Invoke collaborating agents: @olivia-product_owner.md, @stella-staff_engineer.md, @neil-test_engineer.md
   - Update RFE files based on review feedback
   - Address technical concerns and refine scope

2. **No questions** - proceed to prioritization

### Phase 9: Prioritization (`/rfe.prioritize`)

1. **Execute Prioritization**:
   - Read `rfes.md` and `prd.md`
   - Invoke collaborating agents: @parker-product_manager.md, @olivia-product_owner.md, @emma-engineering_manager.md
   - Apply RICE or MoSCoW framework automatically
   - Generate `prioritization.md` and optionally `roadmap-visual.md`
   - Create implementation roadmap

2. **Critical Questions (only if needed)**:
   - "What is the target release date?" (if critical for roadmap)
   - "Are there any business-critical deadlines?" (if not mentioned)
   - Maximum 1-2 questions

3. **Proceed automatically** to submission

### Phase 10: RFE Submission (`/rfe.submit`)

1. **Execute Submission**:
   - Read `rfes.md` and all RFE files
   - Invoke collaborating agents: @olivia-product_owner.md, @emma-engineering_manager.md, @parker-product_manager.md
   - Check for Jira MCP availability
   - If available: Create Jira tickets automatically
   - If not available: Generate manual submission instructions
   - Create `jira-tickets.md` (if Jira MCP available)

2. **No questions** - complete workflow

## Guidelines

### Question Strategy
- **Minimize questions**: Only ask when information is absolutely critical and cannot be reasonably inferred
- **Batch questions**: If multiple questions are needed, ask them all at once
- **Use defaults**: Make reasonable assumptions and proceed when possible
- **Context-aware**: Use information from previous phases to answer questions automatically

### Decision Making
- **Auto-proceed**: Move to next phase automatically unless critical blocker identified
- **Smart defaults**: Use industry best practices and common patterns
- **Review thresholds**: Only trigger revision phases if critical issues are found
- **Prioritization**: Use RICE framework by default, fall back to MoSCoW if data insufficient

### Error Handling
- **Missing artifacts**: If a required artifact is missing, generate it with best available information
- **Agent unavailability**: Proceed with available agents, note limitations
- **Jira MCP unavailable**: Provide clear manual submission instructions
- **Critical blockers**: If a phase cannot proceed, pause and ask user, then continue

### Progress Reporting
After each phase, provide a brief status update:
- Phase completed
- Key decisions made
- Artifacts created
- Next phase starting

At completion, provide a comprehensive summary:
- All artifacts created
- Total RFEs generated
- Jira tickets created (or manual submission instructions)
- Next steps for the team

## Completion Report Template

```markdown
# Speedrun Workflow Complete ✅

## Summary
Successfully completed PRD-RFE workflow from discovery to Jira submission.

## Artifacts Created
- discovery.md
- requirements.md
- prd.md
- prd-checklist.md
- prd-review-report.md
- rfes.md
- rfe-tasks/ (X individual RFE files)
- prioritization.md
- jira-tickets.md (or manual submission instructions)

## Statistics
- Total RFEs: X
- High Priority: X
- Medium Priority: X
- Low Priority: X

## Jira Status
- [ ] Tickets created automatically (X tickets)
- [ ] Manual submission required (see jira-tickets.md for instructions)

## Next Steps
1. Review generated artifacts
2. [If manual submission] Create Jira tickets using provided instructions
3. Share PRD and RFEs with stakeholders
4. Begin sprint planning with prioritized RFEs
```

## Usage Notes

- This command is designed for experienced users who want to quickly generate a complete PRD and RFE set
- It makes reasonable assumptions throughout to minimize interruptions
- Users can always run individual commands later to refine specific phases
- All artifacts are saved and can be reviewed/revised after speedrun completion
- The workflow can be paused at any critical question if user needs to gather information

