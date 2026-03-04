---
description: Review Feature artifacts for technical feasibility and implementation readiness.
displayName: feature.review
icon: 🔧
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

This command reviews Feature artifacts (Feature master list and individual Feature documents) for technical feasibility, implementation readiness, and quality of technical planning.

**IMPORTANT: Agent Collaboration**

You MUST proactively invoke the following collaborating agents to ensure comprehensive Feature review:

1. **@stella-staff_engineer.md** - For technical feasibility, implementation complexity, and risk assessment
2. **@archie-architect.md** (from bullpen) - For architecture alignment and system-level implications
3. **@neil-test_engineer.md** (from bullpen) - For testing requirements, automation strategy, and cross-team impact analysis
4. **@emma-engineering_manager.md** (from bullpen) - For team capacity planning and delivery coordination
5. **@olivia-product_owner.md** (from bullpen) - For acceptance criteria validation and scope negotiation

Invoke these agents at the start of the review process. Work collaboratively with them to validate technical approach, assess testability, check capacity, and ensure architecture alignment.

1. **Load Feature Artifacts**:
   - Read `features.md` (required)
   - Read individual Feature files from `feature-tasks/*.md`
   - Read `prd.md` for context
   - Read `prioritization.md` (if exists)
   - Consider user input from $ARGUMENTS

2. **Create Feature Technical Review Report**: Generate `feature-review-report.md`:

   ```markdown
   # Feature Technical Feasibility Review Report

   **Date**: [Current Date]
   **Reviewer**: Claude Assistant
   **Status**: [Ready/Needs Work/Blocked]

   ## Executive Summary

   [Brief overview of Feature technical feasibility and key findings]

   **Total Features Reviewed**: [Count]
   **Ready for Implementation**: [Count]
   **Need Further Work**: [Count]
   **Blocked/High Risk**: [Count]

   **Overall Assessment**: [Ready/Needs Work/Not Ready]

   ## Feature Review Summary

   | Feature ID | Title | Status | Technical Risk | Effort Estimate | Notes |
   |------------|-------|--------|----------------|------------------|-------|
   | Feature-001 | [Title] | ✅ Ready | Low | 3-5 days | Clear requirements |
   | Feature-002 | [Title] | ⚠️ Needs Work | Medium | 5-8 days | Dependency unclear |
   | Feature-003 | [Title] | ❌ Blocked | High | Unknown | Missing technical spec |

   ## Detailed Feature Reviews

   ### Feature-001: [Title] - ✅ READY

   **Technical Feasibility**: ✅ Feasible
   **Architecture Impact**: ✅ Minimal
   **Testing Complexity**: ✅ Straightforward
   **Team Capacity**: ✅ Within current skills
   **Effort Estimate**: 3-5 days
   **Risk Level**: Low

   #### Requirements Quality
   - ✅ Clear functional requirements
   - ✅ Well-defined acceptance criteria
   - ✅ User stories are testable
   - ✅ Success metrics defined

   #### Technical Assessment
   - ✅ Existing architecture supports this feature
   - ✅ No new infrastructure required
   - ✅ Standard implementation patterns apply
   - ✅ No major integration challenges

   #### Testing Strategy
   - ✅ Unit tests: Clear approach identified
   - ✅ Integration tests: Standard patterns apply
   - ✅ E2E tests: Scenarios well-defined
   - ✅ Performance impact: Minimal

   #### Dependencies & Risks
   - ✅ No blocking dependencies
   - ✅ All required APIs/services available
   - ✅ No cross-team coordination required
   - ✅ Risk mitigation strategies clear

   #### Recommendations
   - **Go/No-Go**: ✅ GO - Ready for implementation
   - **Priority**: Can proceed with current priority
   - **Team Assignment**: Can be assigned to current team
   - **Next Steps**: Begin implementation planning

   ---

   ### Feature-002: [Title] - ⚠️ NEEDS WORK

   **Technical Feasibility**: ⚠️ Feasible with concerns
   **Architecture Impact**: ⚠️ Moderate
   **Testing Complexity**: ⚠️ Requires additional planning
   **Team Capacity**: ⚠️ Requires skill development
   **Effort Estimate**: 5-8 days (was 3-5)
   **Risk Level**: Medium

   #### Requirements Issues
   - ⚠️ Some acceptance criteria need clarification
   - ✅ Functional requirements clear
   - ⚠️ Edge cases not fully defined
   - ✅ Success metrics adequate

   #### Technical Concerns
   - ⚠️ Integration complexity higher than estimated
   - ⚠️ Performance implications need assessment
   - ✅ Architecture pattern is appropriate
   - ⚠️ Data migration considerations unclear

   #### Testing Challenges
   - ⚠️ Complex integration test scenarios
   - ✅ Unit testing approach clear
   - ⚠️ E2E testing may require test environment changes
   - ⚠️ Performance testing strategy needed

   #### Dependencies & Risks
   - ⚠️ Dependency on Feature-001 completion
   - ⚠️ External API reliability concerns
   - ✅ Team skills adequate with training
   - ⚠️ Timeline may slip without risk mitigation

   #### Recommendations
   - **Go/No-Go**: ⚠️ CONDITIONAL GO - Address concerns first
   - **Required Actions**:
     1. Clarify acceptance criteria with PM
     2. Conduct technical spike for integration approach
     3. Define performance testing strategy
     4. Validate external API reliability
   - **Revised Effort**: 5-8 days
   - **Next Steps**: Complete required actions, then reassess

   ---

   ### Feature-003: [Title] - ❌ BLOCKED

   **Technical Feasibility**: ❌ Requires significant investigation
   **Architecture Impact**: ❌ Major changes required
   **Testing Complexity**: ❌ Unclear approach
   **Team Capacity**: ❌ Skills gap identified
   **Effort Estimate**: Unknown - needs technical design
   **Risk Level**: High

   #### Critical Issues
   - ❌ Requirements lack technical detail
   - ❌ Architecture pattern unclear
   - ❌ No clear implementation approach
   - ❌ Success criteria not measurable

   #### Technical Blockers
   - ❌ Major architectural changes required
   - ❌ New technology/framework needed
   - ❌ Cross-team dependencies not resolved
   - ❌ Performance requirements unclear

   #### Testing Gaps
   - ❌ Testing approach undefined
   - ❌ Test automation strategy missing
   - ❌ Complex integration scenarios
   - ❌ Performance testing requirements unclear

   #### Capacity Concerns
   - ❌ Team lacks required skills
   - ❌ Training/hiring required
   - ❌ Timeline unrealistic
   - ❌ Resource allocation unclear

   #### Recommendations
   - **Go/No-Go**: ❌ NO GO - Major work required before implementation
   - **Required Actions**:
     1. Conduct technical design session
     2. Define architecture approach
     3. Assess team skill gaps
     4. Create detailed technical specification
     5. Re-estimate effort after design complete
   - **Timeline Impact**: 2-3 weeks for prerequisite work
   - **Next Steps**: Schedule technical design workshop

   ## Overall Assessment

   ### Implementation Readiness
   - **Ready to Start**: Feature-001
   - **Needs Work**: Feature-002 (1-2 weeks additional planning)
   - **Not Ready**: Feature-003 (requires technical design)

   ### Architecture Implications
   - **Minimal Impact**: Feature-001
   - **Moderate Impact**: Feature-002 (integration complexity)
   - **Major Impact**: Feature-003 (architectural changes required)

   ### Risk Summary
   | Risk Category | Low Risk | Medium Risk | High Risk |
   |---------------|----------|-------------|-----------|
   | Technical Complexity | Feature-001 | Feature-002 | Feature-003 |
   | Team Capacity | Feature-001 | Feature-002 | Feature-003 |
   | External Dependencies | Feature-001, Feature-002 | | Feature-003 |
   | Timeline Risk | Feature-001 | Feature-002 | Feature-003 |

   ### Effort Estimate Adjustments
   | Feature ID | Original Estimate | Reviewed Estimate | Confidence |
   |------------|-------------------|-------------------|------------|
   | Feature-001 | 3-5 days | 3-5 days | High |
   | Feature-002 | 3-5 days | 5-8 days | Medium |
   | Feature-003 | 5-7 days | Unknown | Low |

   ## Recommendations

   ### Immediate Actions
   1. **Proceed with Feature-001**: Ready for implementation
   2. **Address Feature-002 concerns**: Complete prerequisite work
   3. **Block Feature-003**: Requires technical design before proceeding

   ### Prioritization Adjustments
   - **No change needed**: Feature-001 priority remains appropriate
   - **Consider deferring**: Feature-002 until concerns addressed
   - **Defer to Phase 2**: Feature-003 until technical design complete

   ### Resource Planning
   - **Current team capacity**: Sufficient for Feature-001
   - **Additional planning time**: Required for Feature-002
   - **Technical design resources**: Required for Feature-003

   ### Quality Assurance
   - **Testing strategy**: Adequate for ready Features
   - **Automation requirements**: Identified for complex Features
   - **Performance testing**: Plan for Features with performance impact

   ## Next Steps

   - [ ] Schedule implementation for ready Features
   - [ ] Create action plans for Features needing work
   - [ ] Schedule technical design sessions for blocked Features
   - [ ] Update prioritization based on review findings
   - [ ] Communicate findings to product management
   ```

3. **Generate Individual Feature Review Comments**:
   - For each Feature that needs work, add specific technical comments to the individual Feature files
   - Update the "Implementation Notes" section with technical concerns
   - Add specific action items to the "Open Questions" section

4. **Review Quality Validation**:
   - All high-priority Features have been technically reviewed
   - Implementation blockers are identified and documented
   - Effort estimates are validated by engineering
   - Testing strategies are defined for each Feature
   - Architecture implications are understood

5. **Report Completion**:
   - Path to Feature technical review report
   - Summary of ready vs. not-ready Features
   - Updated effort estimates based on technical review
   - Recommended prioritization adjustments
   - Next steps for addressing technical concerns

## Review Criteria

### Technical Feasibility
- Architecture patterns are appropriate
- Implementation approach is clear
- No major technical unknowns
- Team has required skills

### Requirements Quality
- Acceptance criteria are testable
- User stories are implementable
- Success metrics are measurable
- Edge cases are considered

### Testing Strategy
- Unit testing approach is clear
- Integration testing is planned
- E2E scenarios are defined
- Performance testing needs identified

### Implementation Readiness
- Dependencies are resolved
- API contracts are defined
- Data requirements are clear
- Infrastructure needs understood