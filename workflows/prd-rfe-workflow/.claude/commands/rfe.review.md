---
description: Review RFE artifacts for technical feasibility and implementation readiness.
displayName: rfe.review
icon: 🔧
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

This command reviews RFE artifacts (RFE master list and individual RFE documents) for technical feasibility, implementation readiness, and quality of technical planning.

1. **Load RFE Artifacts**:
   - Read `artifacts/rfes.md` (required)
   - Read individual RFE files from `artifacts/rfe-tasks/*.md`
   - Read `artifacts/prd.md` for context
   - Read `artifacts/prioritization.md` (if exists)
   - Consider user input from $ARGUMENTS

2. **Create RFE Technical Review Report**: Generate `artifacts/rfe-review-report.md`:

   ```markdown
   # RFE Technical Feasibility Review Report

   **Date**: [Current Date]
   **Reviewer**: Claude Assistant
   **Status**: [Ready/Needs Work/Blocked]

   ## Executive Summary

   [Brief overview of RFE technical feasibility and key findings]

   **Total RFEs Reviewed**: [Count]
   **Technically Feasible**: [Count]
   **Needs Clarification**: [Count]
   **High Risk**: [Count]
   **Blocked**: [Count]

   ---

   ## Technical Feasibility Assessment

   ### Overall Technical Readiness

   | Category | Score | Status |
   |----------|-------|--------|
   | Technical Clarity | X/10 | ✅/⚠️/❌ |
   | Implementation Scope | X/10 | ✅/⚠️/❌ |
   | Dependency Management | X/10 | ✅/⚠️/❌ |
   | Risk Assessment | X/10 | ✅/⚠️/❌ |
   | Resource Requirements | X/10 | ✅/⚠️/❌ |
   | Testing Strategy | X/10 | ✅/⚠️/❌ |

   **Overall Technical Feasibility Score**: X/60 ([Percentage]%)

   ### Scoring Legend
   - ✅ Strong (8-10): Ready for implementation
   - ⚠️ Moderate (5-7): Needs clarification or planning
   - ❌ Weak (0-4): Significant concerns or blockers

   ---

   ## Per-RFE Technical Analysis

   ### RFE-001: [Title]

   **Technical Feasibility**: ✅ Feasible / ⚠️ Needs Work / ❌ High Risk / 🚫 Blocked

   #### Technical Clarity
   - **Score**: X/10
   - **Assessment**: [Is the technical approach clear? Are integration points identified?]
   - **Gaps**: [What technical details are missing?]
   - **Recommendations**: [What needs to be clarified?]

   #### Scope & Complexity
   - **Score**: X/10
   - **Estimated Complexity**: Low / Medium / High / Very High
   - **Assessment**: [Is the scope well-defined? Is sizing appropriate?]
   - **Concerns**: [Scope creep risks, underestimation issues]
   - **Recommendations**: [Should it be split? Combined? Rescoped?]

   #### Dependencies & Integration
   - **Score**: X/10
   - **Internal Dependencies**: [List RFE dependencies and their status]
   - **External Dependencies**: [APIs, services, libraries, teams]
   - **Assessment**: [Are all dependencies identified and available?]
   - **Risks**: [Dependency-related risks]
   - **Recommendations**: [How to handle dependencies]

   #### Technical Risks
   - **Score**: X/10
   - **Identified Risks**:
     1. [Risk 1]: [Description, likelihood, impact]
     2. [Risk 2]: [Description, likelihood, impact]
   - **Mitigation Strategies**: [How to address each risk]
   - **Showstoppers**: [Any blocking technical issues]
   - **Recommendations**: [Risk mitigation steps]

   #### Resource Requirements
   - **Score**: X/10
   - **Skills Needed**: [Technical skills/expertise required]
   - **Infrastructure**: [Servers, databases, services needed]
   - **Third-party Services**: [External services/APIs required]
   - **Assessment**: [Are resources available and accessible?]
   - **Gaps**: [Missing resources or capabilities]
   - **Recommendations**: [Resource acquisition/allocation needs]

   #### Testing Strategy
   - **Score**: X/10
   - **Test Coverage**: [Unit, integration, E2E plans documented?]
   - **Test Complexity**: [How difficult to test? Special environments needed?]
   - **Assessment**: [Is testing approach comprehensive and realistic?]
   - **Gaps**: [Missing test scenarios or strategies]
   - **Recommendations**: [Testing improvements needed]

   #### Implementation Approach
   - **Suggested Architecture**: [High-level technical architecture]
   - **Key Components**: [Main technical components to build]
   - **Integration Points**: [Where this connects to existing systems]
   - **Data Flow**: [How data moves through the system]
   - **Technical Considerations**: [Performance, security, scalability notes]

   #### Effort Estimate Validation
   - **Current Estimate**: [S/M/L/XL from RFE]
   - **Validated Estimate**: [Revised estimate based on technical review]
   - **Confidence Level**: High / Medium / Low
   - **Justification**: [Why this estimate is appropriate]
   - **Recommendation**: [Keep estimate / Revise to X / Split into multiple RFEs]

   #### Readiness Assessment
   - **Ready for Implementation**: Yes / No / With Conditions
   - **Blocking Issues**: [List any blockers]
   - **Prerequisites**: [What must be done first]
   - **Next Steps**: [Actions needed before starting implementation]

   ---

   [Repeat for each RFE]

   ---

   ## Cross-RFE Technical Analysis

   ### Architecture Coherence
   - **Assessment**: [Do RFEs work together cohesively? Any architectural conflicts?]
   - **Concerns**: [Inconsistencies, overlaps, gaps in overall architecture]
   - **Recommendations**: [Architectural improvements needed]

   ### Dependency Graph Validation
   - **Circular Dependencies**: [Any found? How to resolve?]
   - **Critical Path**: [What's the longest dependency chain?]
   - **Parallel Work Opportunities**: [Which RFEs can be done concurrently?]
   - **Bottlenecks**: [RFEs that block many others]
   - **Recommendations**: [Resequencing or restructuring suggestions]

   ### Technology Stack Alignment
   - **Technologies Used**: [List all technologies across RFEs]
   - **Consistency**: [Are tech choices aligned? Any conflicts?]
   - **New Technologies**: [Any new tech being introduced? Training needed?]
   - **Concerns**: [Tech stack fragmentation, version conflicts, etc.]
   - **Recommendations**: [Standardization or consolidation needed]

   ### Resource Capacity Analysis
   - **Skill Gaps**: [Technical skills needed but not available]
   - **Infrastructure Needs**: [New infrastructure requirements]
   - **Third-party Dependencies**: [External services/APIs needed]
   - **Bottleneck Resources**: [Scarce resources needed by multiple RFEs]
   - **Recommendations**: [Resource acquisition or allocation strategy]

   ### Risk Aggregation
   - **High-Risk RFEs**: [Count and list]
   - **Common Risk Patterns**: [Risks appearing across multiple RFEs]
   - **Systemic Risks**: [Risks to overall project success]
   - **Cumulative Risk**: [Overall project risk level: Low/Medium/High/Very High]
   - **Recommendations**: [Risk mitigation priorities]

   ---

   ## Critical Issues & Blockers

   ### Blocking Issues (Must Resolve Before Starting)
   1. **[Issue 1]**
      - **Affected RFEs**: [List]
      - **Description**: [What's blocking]
      - **Impact**: [High/Medium/Low]
      - **Resolution**: [How to resolve]
      - **Owner**: [Who needs to resolve]

   2. **[Issue 2]**
      - **Affected RFEs**: [List]
      - **Description**: [What's blocking]
      - **Impact**: [High/Medium/Low]
      - **Resolution**: [How to resolve]
      - **Owner**: [Who needs to resolve]

   ### High-Priority Issues (Address Soon)
   1. **[Issue 1]**: [Description and recommended action]
   2. **[Issue 2]**: [Description and recommended action]

   ### Medium-Priority Issues (Address Eventually)
   1. **[Issue 1]**: [Description and recommended action]
   2. **[Issue 2]**: [Description and recommended action]

   ---

   ## Feasibility by Priority Tier

   ### High-Priority RFEs
   - **Total**: [Count]
   - **Technically Ready**: [Count]
   - **Needs Work**: [Count]
   - **Blocked**: [Count]
   - **Assessment**: [Can high-priority work begin?]

   ### Medium-Priority RFEs
   - **Total**: [Count]
   - **Technically Ready**: [Count]
   - **Needs Work**: [Count]
   - **Blocked**: [Count]
   - **Assessment**: [Technical state of medium-priority work]

   ### Low-Priority RFEs
   - **Total**: [Count]
   - **Technically Ready**: [Count]
   - **Needs Work**: [Count]
   - **Blocked**: [Count]
   - **Assessment**: [Technical state of low-priority work]

   ---

   ## Implementation Roadmap Validation

   ### Phase 1 Feasibility
   - **RFEs in Phase**: [List]
   - **Technical Readiness**: [Assessment]
   - **Blocking Issues**: [Any blockers?]
   - **Parallel Work**: [Which can run concurrently?]
   - **Recommendation**: [Ready to start / Needs preparation]

   ### Phase 2 Feasibility
   - **RFEs in Phase**: [List]
   - **Technical Readiness**: [Assessment]
   - **Dependencies from Phase 1**: [Properly sequenced?]
   - **Recommendation**: [Assessment]

   ### Phase 3+ Feasibility
   - **RFEs in Phase**: [List]
   - **Technical Readiness**: [Assessment]
   - **Long-term Risks**: [Any concerns?]
   - **Recommendation**: [Assessment]

   ---

   ## Recommendations

   ### Immediate Actions (Before Implementation Starts)
   1. **[Action 1]**: [Specific technical task]
      - **Priority**: High/Medium/Low
      - **Effort**: [Estimate]
      - **Owner**: [Who should do this]

   2. **[Action 2]**: [Specific technical task]
      - **Priority**: High/Medium/Low
      - **Effort**: [Estimate]
      - **Owner**: [Who should do this]

   ### RFE Modifications Recommended
   1. **RFE-XXX**: [Split into smaller RFEs / Merge with RFE-YYY / Rescope / Reprioritize]
      - **Reason**: [Why this change is needed]
      - **Impact**: [Effect on timeline/scope]

   2. **RFE-YYY**: [Modification recommended]
      - **Reason**: [Why this change is needed]
      - **Impact**: [Effect on timeline/scope]

   ### Technical Debt Considerations
   - **Shortcuts Identified**: [Quick wins that may create tech debt]
   - **Debt Acceptance**: [Which shortcuts are acceptable given constraints?]
   - **Mitigation Plan**: [How to address tech debt later]

   ### Prototype/Spike Recommendations
   - **[Technology/Approach 1]**: [Why a spike is needed before committing]
   - **[Technology/Approach 2]**: [Why a prototype would reduce risk]

   ---

   ## Overall Assessment

   **Technical Feasibility Rating**: [Strong/Moderate/Weak/Blocked]

   **Summary**: [Overall technical assessment - can this project be implemented successfully?]

   **Confidence Level**: [High/Medium/Low confidence in technical success]

   **Key Strengths**:
   - [Technical strength 1]
   - [Technical strength 2]

   **Key Concerns**:
   - [Technical concern 1]
   - [Technical concern 2]

   **Go/No-Go Recommendation**: [Proceed / Proceed with Conditions / Major Rework Needed / Do Not Proceed]

   **Conditions for Proceeding** (if applicable):
   1. [Condition 1 that must be met]
   2. [Condition 2 that must be met]

   ---

   ## Next Steps

   ### If Ready to Proceed
   1. [Action 1]
   2. [Action 2]
   3. [Action 3]

   ### If Rework Needed
   1. [What needs to be reworked]
   2. [Which commands to re-run]
   3. [Additional planning required]

   ### If Blocked
   1. [What needs to be unblocked]
   2. [Who needs to be involved]
   3. [Timeline for resolution]

   ---

   ## Sign-off

   **Reviewed by**: Claude Assistant
   **Date**: [Current Date]
   **Technical Recommendation**: [Proceed / Conditional Proceed / Rework / Block]
   ```

3. **Perform Technical Feasibility Analysis**:

   For each RFE, systematically evaluate:

   - **Technical Clarity**: How well-defined is the technical approach?
   - **Scope Assessment**: Is the scope realistic and well-bounded?
   - **Dependencies**: Are all technical dependencies identified and manageable?
   - **Risks**: What could go wrong technically? How severe?
   - **Resources**: Are the necessary skills, infrastructure, and services available?
   - **Testing**: Can this be tested effectively? Is the test strategy sound?

4. **Score Each RFE**:
   - Evaluate each category on a 0-10 scale
   - Aggregate scores for overall technical feasibility
   - Identify RFEs that are ready vs. need work vs. blocked

5. **Validate Dependencies**:
   - Check for circular dependencies
   - Identify critical path
   - Find opportunities for parallel work
   - Flag dependency risks

6. **Assess Technical Risks**:
   - Identify technical risks in each RFE
   - Look for common risk patterns
   - Evaluate cumulative/systemic risks
   - Propose mitigation strategies

7. **Validate Effort Estimates**:
   - Review sizing estimates against technical complexity
   - Flag underestimated or overestimated RFEs
   - Recommend estimate adjustments
   - Suggest splitting overly large RFEs

8. **Evaluate Implementation Readiness**:
   - Determine which RFEs are ready to start
   - Identify blocking issues
   - List prerequisites for each RFE
   - Provide go/no-go recommendation

9. **Report Findings**:
   - Display technical feasibility scores
   - Highlight critical technical issues
   - List blocked RFEs
   - Provide actionable technical recommendations
   - State readiness for implementation

10. **Interactive Follow-up**:
    - If issues found, ask if user wants to address them
    - Suggest technical planning tasks (spikes, prototypes, research)
    - Offer to help refine RFE technical details
    - Recommend re-running `/rfe.breakdown` if major restructuring needed

## Guidelines

- Focus on technical feasibility and implementation readiness
- Be realistic about technical challenges and risks
- Identify skill gaps, resource needs, and infrastructure requirements
- Check that technical approaches are sound and well-thought-out
- Validate that dependencies are manageable
- Ensure testing strategies are comprehensive
- Flag underestimated complexity early
- Provide constructive technical guidance
- Recommend spikes or prototypes for high-risk areas
- Make clear technical recommendations for each RFE
- Balance thoroughness with pragmatism
- Consider both immediate implementation and long-term maintainability
