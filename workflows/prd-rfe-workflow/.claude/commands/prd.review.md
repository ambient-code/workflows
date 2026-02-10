---
description: Review PRD artifacts for completeness in key product discovery areas.
displayName: prd.review
icon: ✅
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

This command reviews PRD artifacts (discovery, requirements, and PRD documents) for completeness across critical product discovery categories.

**IMPORTANT: Agent Collaboration**

You MUST proactively invoke the following collaborating agents to ensure comprehensive PRD review:

1. **@steve-ux_designer.md** - For UX assessment and to determine if a prototype is needed for validation
2. **@aria-ux_architect.md** (from bullpen) - For holistic UX strategy validation and journey alignment
3. **@olivia-product_owner.md** (from bullpen) - For story readiness and acceptance criteria validation
4. **@archie-architect.md** (from bullpen) - For technical feasibility and architecture alignment

Invoke these agents at the start of the review process. Work collaboratively with them to assess quality, completeness, and feasibility from multiple perspectives.

1. **Load PRD Artifacts**:
   - Read `discovery.md` (if exists)
   - Read `rfe.md` (if exists)
   - Read `prd.md` (required)
   - Consider user input from $ARGUMENTS

2. **Create PRD Review Report**: Generate `prd-review-report.md`:

   ```markdown
   # PRD Completeness Review Report

   **Date**: [Current Date]
   **Reviewer**: Claude Assistant
   **Status**: [Complete/Incomplete/Needs Revision]

   ## Executive Summary

   [Brief overview of PRD completeness and key findings]

   ## Completeness Assessment

   ### 1. Product/Feature Definition

   **Question**: What product or feature are you looking to build?

   - **Status**: ✅ Complete / ⚠️ Partial / ❌ Missing
   - **Found In**: [Document section references]
   - **Assessment**: [Is the product/feature clearly defined? Is it specific enough?]
   - **Gaps**: [What's missing or unclear]
   - **Recommendations**: [Specific improvements needed]

   ---

   ### 2. Core Problem Statement

   **Question**: What's the core problem you're trying to solve?

   - **Status**: ✅ Complete / ⚠️ Partial / ❌ Missing
   - **Found In**: [Document section references]
   - **Assessment**: [Is the problem clearly articulated? Is it validated?]
   - **Gaps**: [What's missing or unclear]
   - **Recommendations**: [Specific improvements needed]

   **Question**: What prompted this idea or initiative?

   - **Status**: ✅ Complete / ⚠️ Partial / ❌ Missing
   - **Found In**: [Document section references]
   - **Assessment**: [Is the origin/catalyst documented?]
   - **Gaps**: [What's missing or unclear]
   - **Recommendations**: [Specific improvements needed]

   ---

   ### 3. Target Users

   **Question**: Who are the target users?

   - **Status**: ✅ Complete / ⚠️ Partial / ❌ Missing
   - **Found In**: [Document section references]
   - **Assessment**: [Are user personas clearly defined?]
   - **Gaps**: [What's missing or unclear]
   - **Recommendations**: [Specific improvements needed]

   **Question**: What roles, industries, or demographics do they represent?

   - **Status**: ✅ Complete / ⚠️ Partial / ❌ Missing
   - **Found In**: [Document section references]
   - **Assessment**: [Are user characteristics well-documented?]
   - **Gaps**: [What's missing or unclear]
   - **Recommendations**: [Specific improvements needed]

   **Question**: How many users are we potentially serving?

   - **Status**: ✅ Complete / ⚠️ Partial / ❌ Missing
   - **Found In**: [Document section references]
   - **Assessment**: [Is the user base size estimated?]
   - **Gaps**: [What's missing or unclear]
   - **Recommendations**: [Specific improvements needed]

   ---

   ### 4. Business Goals

   **Question**: What are the business goals?

   - **Status**: ✅ Complete / ⚠️ Partial / ❌ Missing
   - **Found In**: [Document section references]
   - **Assessment**: [Are business objectives clearly stated?]
   - **Gaps**: [What's missing or unclear]
   - **Recommendations**: [Specific improvements needed]

   **Question**: What does success look like for the organization?

   - **Status**: ✅ Complete / ⚠️ Partial / ❌ Missing
   - **Found In**: [Document section references]
   - **Assessment**: [Is success clearly defined?]
   - **Gaps**: [What's missing or unclear]
   - **Recommendations**: [Specific improvements needed]

   **Question**: Are there specific business metrics or outcomes you're targeting?

   - **Status**: ✅ Complete / ⚠️ Partial / ❌ Missing
   - **Found In**: [Document section references]
   - **Assessment**: [Are metrics measurable and specific?]
   - **Gaps**: [What's missing or unclear]
   - **Recommendations**: [Specific improvements needed]

   ---

   ### 5. Competitive Landscape

   **Question**: What's the competitive landscape?

   - **Status**: ✅ Complete / ⚠️ Partial / ❌ Missing
   - **Found In**: [Document section references]
   - **Assessment**: [Is competitive analysis thorough?]
   - **Gaps**: [What's missing or unclear]
   - **Recommendations**: [Specific improvements needed]

   **Question**: Are there existing solutions that address this problem?

   - **Status**: ✅ Complete / ⚠️ Partial / ❌ Missing
   - **Found In**: [Document section references]
   - **Assessment**: [Are competitors/alternatives documented?]
   - **Gaps**: [What's missing or unclear]
   - **Recommendations**: [Specific improvements needed]

   **Question**: What would differentiate your solution?

   - **Status**: ✅ Complete / ⚠️ Partial / ❌ Missing
   - **Found In**: [Document section references]
   - **Assessment**: [Is differentiation strategy clear?]
   - **Gaps**: [What's missing or unclear]
   - **Recommendations**: [Specific improvements needed]

   ---

   ### 6. Constraints & Considerations

   **Question**: What constraints should we consider?

   - **Status**: ✅ Complete / ⚠️ Partial / ❌ Missing
   - **Found In**: [Document section references]
   - **Assessment**: [Are constraints documented?]
   - **Gaps**: [What's missing or unclear]
   - **Recommendations**: [Specific improvements needed]

   **Sub-questions assessed**:
   - Timeline constraints: ✅ / ⚠️ / ❌
   - Budget constraints: ✅ / ⚠️ / ❌
   - Technical constraints: ✅ / ⚠️ / ❌
   - Regulatory/compliance constraints: ✅ / ⚠️ / ❌
   - Other limitations: ✅ / ⚠️ / ❌

   ---

   ## Completeness Score

   ### Category Scores

   | Category | Score | Status |
   |----------|-------|--------|
   | Product/Feature Definition | X/1 | ✅/⚠️/❌ |
   | Core Problem Statement | X/2 | ✅/⚠️/❌ |
   | Target Users | X/3 | ✅/⚠️/❌ |
   | Business Goals | X/3 | ✅/⚠️/❌ |
   | Competitive Landscape | X/3 | ✅/⚠️/❌ |
   | Constraints & Considerations | X/5 | ✅/⚠️/❌ |

   **Overall Completeness Score**: X/17 ([Percentage]%)

   ### Scoring Legend
   - ✅ Complete: Information is present, clear, and comprehensive
   - ⚠️ Partial: Information is present but lacks detail or clarity
   - ❌ Missing: Information is absent or insufficient

   ---

   ## Critical Gaps

   ### High Priority (Must Address)
   1. [Gap 1]: [Why it's critical and what's needed]
   2. [Gap 2]: [Why it's critical and what's needed]

   ### Medium Priority (Should Address)
   1. [Gap 1]: [Why it's important and what's needed]
   2. [Gap 2]: [Why it's important and what's needed]

   ### Low Priority (Nice to Have)
   1. [Gap 1]: [Why it's beneficial and what's needed]

   ---

   ## Strengths

   - [Strength 1]: [What's well-documented]
   - [Strength 2]: [What's well-documented]

   ---

   ## Recommendations

   ### Immediate Actions
   1. [Action 1]: [Specific task to complete]
   2. [Action 2]: [Specific task to complete]

   ### Follow-up Actions
   1. [Action 1]: [Specific task to complete]
   2. [Action 2]: [Specific task to complete]

   ---

   ## Overall Assessment

   **Readiness Status**: [Ready for Feature Breakdown / Needs Minor Revisions / Needs Major Revisions]

   **Summary**: [Overall assessment of PRD completeness and readiness]

   **Next Steps**:
   - If Ready: Proceed to `/rfe.breakdown`
   - If Needs Revision: [List which commands to re-run]

   ---

   ## Sign-off

   **Reviewed by**: Claude Assistant
   **Date**: [Current Date]
   **Recommendation**: [Proceed / Revise / Reconsider]
   ```

3. **Perform Detailed Analysis**:

   For each category, systematically search through all PRD artifacts:

   - **Product/Feature Definition**: Look for product vision, feature descriptions, value proposition
   - **Core Problem**: Search for problem statement, user pain points, catalyst/trigger
   - **Target Users**: Find personas, user roles, demographics, market size
   - **Business Goals**: Identify objectives, success definitions, KPIs, metrics
   - **Competitive Landscape**: Look for competitor analysis, alternatives, differentiation strategy
   - **Constraints**: Find timeline, budget, technical, regulatory, or other limitations

4. **Score Each Question**:
   - Give 1 point for ✅ Complete
   - Give 0.5 points for ⚠️ Partial
   - Give 0 points for ❌ Missing
   - Calculate percentage score

5. **Identify Gaps**:
   - List what information is missing or incomplete
   - Prioritize gaps by impact (High/Medium/Low)
   - Provide specific recommendations for addressing each gap

6. **Assess Readiness**:
   - Determine if PRD is ready for Feature breakdown
   - Score threshold: >80% = Ready, 60-80% = Needs Minor Revisions, <60% = Needs Major Revisions
   - Provide clear next steps

7. **Report Findings**:
   - Display completeness score
   - Highlight critical gaps
   - List strengths
   - Provide actionable recommendations
   - State readiness for next phase

8. **Interactive Follow-up**:
   - If gaps found, ask if user wants to address them now
   - Suggest which commands to re-run (e.g., `/prd.discover`, `/prd.rfe`, `/prd.create`)
   - Offer to help fill specific gaps

## Guidelines

- Focus on completeness, not perfection
- Be specific about what's missing and where to add it
- Prioritize gaps by business impact
- Check all artifacts (discovery, requirements, PRD) for information
- Cross-reference between documents
- Provide constructive, actionable feedback
- Recognize what's well-documented
- Make clear recommendations for next steps
