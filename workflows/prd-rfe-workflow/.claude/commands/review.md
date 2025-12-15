---
description: Review all generated artifacts and validate completeness and quality.
displayName: Review
icon: ✅
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

This command reviews all artifacts generated during the PRD-RFE workflow and validates their completeness and quality.

1. **Scan Artifacts Directory**:
   - Check for existence of key artifacts:
     - `artifacts/discovery.md` (optional)
     - `artifacts/requirements.md` (optional)
     - `artifacts/prd.md` (required)
     - `artifacts/rfes.md` (required)
     - `artifacts/rfe-tasks/*.md` (required)
     - `artifacts/prioritization.md` (recommended)

2. **Create Review Report**: Generate `artifacts/review-report.md`:

   ```markdown
   # PRD-RFE Workflow Review Report

   **Date**: [Current Date]
   **Reviewer**: Claude Assistant
   **Status**: [Complete/Incomplete/Needs Revision]

   ## Artifacts Inventory

   | Artifact | Status | Location | Quality |
   |----------|--------|----------|---------|
   | Discovery Document | ✅/❌/⚠️ | artifacts/discovery.md | Pass/Needs Work |
   | Requirements Document | ✅/❌/⚠️ | artifacts/requirements.md | Pass/Needs Work |
   | PRD | ✅/❌/⚠️ | artifacts/prd.md | Pass/Needs Work |
   | RFE Master List | ✅/❌/⚠️ | artifacts/rfes.md | Pass/Needs Work |
   | Individual RFE Tasks | ✅/❌/⚠️ | artifacts/rfe-tasks/*.md | Pass/Needs Work |
   | Prioritization | ✅/❌/⚠️ | artifacts/prioritization.md | Pass/Needs Work |

   Legend: ✅ = Present and complete | ❌ = Missing | ⚠️ = Present but incomplete

   ## Quality Assessment

   ### PRD Quality

   #### Completeness
   - [ ] Executive summary is clear and compelling
   - [ ] Problem statement is well-defined
   - [ ] Goals and success metrics are measurable
   - [ ] Target users and personas are identified
   - [ ] User stories are comprehensive
   - [ ] Functional requirements are detailed
   - [ ] Non-functional requirements are specified
   - [ ] Scope (in/out) is clearly defined
   - [ ] Assumptions and dependencies are documented
   - [ ] Risks are identified with mitigation plans

   #### Clarity
   - [ ] Language is clear and unambiguous
   - [ ] Technical jargon is minimized
   - [ ] Requirements are specific and testable
   - [ ] Success criteria are measurable
   - [ ] Document flows logically

   #### Consistency
   - [ ] No contradictions between sections
   - [ ] Terminology is consistent throughout
   - [ ] Priorities are aligned across sections

   **PRD Quality Score**: [X/15] - [Pass/Needs Improvement/Fail]

   ### RFE Breakdown Quality

   #### Coverage
   - [ ] All PRD requirements are covered by RFEs
   - [ ] Each RFE maps back to PRD requirements
   - [ ] No orphaned or redundant RFEs

   #### Sizing
   - [ ] RFEs are appropriately sized (not too large/small)
   - [ ] Effort estimates are reasonable
   - [ ] Large RFEs are justified or broken down

   #### Dependencies
   - [ ] Dependencies are clearly identified
   - [ ] No circular dependencies exist
   - [ ] Critical path is identifiable

   #### Acceptance Criteria
   - [ ] Each RFE has clear acceptance criteria
   - [ ] Criteria are testable and measurable
   - [ ] Criteria align with PRD requirements

   **RFE Quality Score**: [X/12] - [Pass/Needs Improvement/Fail]

   ### Prioritization Quality

   #### Methodology
   - [ ] Prioritization method is clearly stated
   - [ ] Method is applied consistently
   - [ ] Rationale is documented for priorities

   #### Alignment
   - [ ] Priorities align with business goals
   - [ ] High-priority items address critical user needs
   - [ ] Dependencies are respected in roadmap

   #### Roadmap
   - [ ] Implementation phases are defined
   - [ ] Each phase delivers cohesive value
   - [ ] Timeline/effort estimates are realistic

   **Prioritization Quality Score**: [X/9] - [Pass/Needs Improvement/Fail]

   ## Issues & Gaps Identified

   ### Critical Issues
   1. [Issue 1]: [Description and impact]
   2. [Issue 2]: [Description and impact]

   ### Recommendations
   1. [Recommendation 1]: [Specific action to take]
   2. [Recommendation 2]: [Specific action to take]

   ### Missing Information
   - [What's missing 1]
   - [What's missing 2]

   ## Traceability Matrix

   | PRD Requirement | Related RFEs | Priority | Status |
   |-----------------|--------------|----------|--------|
   | FR-001: [Requirement] | RFE-001, RFE-003 | High | ✅ Covered |
   | FR-002: [Requirement] | RFE-002 | Medium | ✅ Covered |
   | FR-003: [Requirement] | - | - | ❌ Not Covered |

   ## Metrics Summary

   ### Coverage Metrics
   - **Total PRD Requirements**: [Count]
   - **Requirements Covered by RFEs**: [Count] ([Percentage]%)
   - **RFEs Created**: [Count]
   - **Total Estimated Effort**: [Sum of all RFE efforts]

   ### Distribution Metrics
   - **High Priority RFEs**: [Count] ([Percentage]%)
   - **Medium Priority RFEs**: [Count] ([Percentage]%)
   - **Low Priority RFEs**: [Count] ([Percentage]%)

   ### Size Distribution
   - **Small RFEs**: [Count]
   - **Medium RFEs**: [Count]
   - **Large RFEs**: [Count]
   - **XLarge RFEs**: [Count] (⚠️ Consider breaking down)

   ## Readiness Assessment

   ### For Stakeholder Review
   - **Status**: Ready/Not Ready
   - **Blocking Issues**: [List any blockers]
   - **Recommended Actions**: [What to do before review]

   ### For Implementation
   - **Status**: Ready/Not Ready
   - **Prerequisites**: [What needs to happen first]
   - **Next Steps**: [Immediate actions]

   ## Overall Assessment

   ### Strengths
   - [Strength 1]
   - [Strength 2]

   ### Areas for Improvement
   - [Area 1]
   - [Area 2]

   ### Overall Status
   **[Complete and Ready / Needs Minor Revisions / Needs Major Revisions]**

   ### Recommendation
   [Summary recommendation: proceed, revise, or reconsider]

   ## Next Steps

   1. [Action 1]
   2. [Action 2]
   3. [Action 3]

   ## Sign-off

   **Reviewed by**: Claude Assistant
   **Date**: [Current Date]
   **Approved**: [ ] Yes [ ] No [ ] Pending Revisions
   ```

3. **Perform Detailed Quality Checks**:

   ### PRD Review
   - Read `artifacts/prd.md` completely
   - Verify all required sections are present
   - Check that success metrics are measurable
   - Ensure requirements are testable
   - Validate that scope is clearly defined
   - Look for contradictions or ambiguities

   ### RFE Review
   - Read `artifacts/rfes.md` and sample individual RFE files
   - Verify all PRD requirements are covered
   - Check that each RFE has acceptance criteria
   - Validate dependencies are documented
   - Ensure sizing is reasonable
   - Look for gaps or overlaps

   ### Prioritization Review (if exists)
   - Read `artifacts/prioritization.md`
   - Verify prioritization method is clear
   - Check alignment with business goals
   - Validate roadmap phases are logical
   - Ensure dependencies are respected

4. **Generate Traceability Report**:
   - Map each PRD requirement to covering RFEs
   - Identify any requirements not covered by RFEs
   - Identify any RFEs not traceable to PRD
   - Create matrix showing relationships

5. **Calculate Quality Scores**:
   - PRD quality score (completeness, clarity, consistency)
   - RFE quality score (coverage, sizing, dependencies)
   - Prioritization quality score (methodology, alignment, roadmap)
   - Overall workflow quality score

6. **Identify Issues and Recommendations**:
   - Flag critical gaps or problems
   - Suggest improvements
   - Recommend next steps
   - Prioritize action items

7. **Report Completion**:
   - Display summary of review findings
   - Highlight quality scores
   - List critical issues
   - Provide recommendations
   - State readiness for next phase

8. **Interactive Review** (if issues found):
   - Ask user if they want to address issues now
   - Offer to re-run specific commands to fix problems
   - Suggest which artifacts need revision

## Guidelines

- Be thorough but constructive in review
- Highlight both strengths and areas for improvement
- Provide specific, actionable recommendations
- Focus on completeness, clarity, and consistency
- Check traceability from PRD to RFEs
- Validate that all artifacts align with business goals
- Ensure documentation is ready for stakeholder review
