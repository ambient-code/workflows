# Feature Template - Red Hat Format

This template provides a standardized format for creating Feature documents that conform to Red Hat's Feature structure. Use this template when generating individual Feature files.

## Template Structure

```markdown
# Feature-XXX: [Title]

**Status**: Not Started
**Priority**: [High/Medium/Low]
**Size**: [S/M/L/XL]
**Created**: [Date]
**PRD Reference**: [Link to prd.md section]

## Summary

[One to three sentences describing the enhancement. Should clearly state what is being extended, added, or modified, and who benefits from this change. Focus on the value delivered.]

Example: "Extend the [component/feature] to [action], providing [target users] with [benefit/value]."

## Background

[Describe the current state of the system/feature. Explain what exists today and what limitations or gaps exist. Reference any relevant existing functionality.]

### Current State
- [Current feature/component description]
- [What information/functionality is currently available]
- [Existing user workflows]

### Gaps and Limitations
- [What is missing or insufficient]
- [What users cannot currently see/do]
- [Pain points with current implementation]

### Related Documentation
- [Links to refinement docs, brainstorming sessions, UXD diagrams, etc.]
- [Reference to related PRDs, user research, or technical specifications]

## Problem Statement

[Clearly articulate the problem(s) this Feature addresses. Focus on user pain points and business impact. Use specific, measurable language when possible.]

[Target User Persona] needs [capability/visibility/functionality] because [reason/impact]. The current [system/UI/feature] provides no indication of:

- [Problem 1]: [Description]
- [Problem 2]: [Description]
- [Problem 3]: [Description]

### Impact
- [User impact - how this affects daily work]
- [Business impact - efficiency, cost, risk]
- [Technical impact - scalability, performance, maintainability]

## Proposed Solution

### Core Requirements

[High-level requirements that must be met. Focus on WHAT needs to be delivered, not HOW.]

1. **Requirement 1**: [Description]
   - [Sub-requirement or detail]
   - [Sub-requirement or detail]

2. **Requirement 2**: [Description]
   - [Sub-requirement or detail]

3. **Conditional Behavior**: [If applicable, describe when features should appear/be enabled]
   - [Condition 1]: [Behavior]
   - [Condition 2]: [Behavior]

### UI/UX Enhancements

[If this Feature involves user interface changes, describe the enhancements in detail.]

#### New Components/Columns/Views
- **[Component Name]**: [Description]
  - [What it displays]
  - [How it behaves]
  - [When it appears]

#### Status Indicators
[If applicable, define status indicators and their meanings]
- 🟢 **[Status Name]**: [Meaning and when it appears]
- 🟡 **[Status Name]**: [Meaning and when it appears]
- 🔵 **[Status Name]**: [Meaning and when it appears]
- 🟠 **[Status Name]**: [Meaning and when it appears]
- ⚫ **[Status Name]**: [Meaning and when it appears]

#### Detailed View Enhancements
- **[Feature Name]**: [Description]
  - [What information is shown]
  - [How users interact with it]
  - [What actions are available]

### Technical Approach (High-Level)

[Brief technical overview - can be refined during implementation]

#### Integration Points
- [System/Component 1]: [How it integrates]
- [System/Component 2]: [How it integrates]

#### Data Considerations
- [Data models or migrations needed]
- [API endpoints or services required]
- [Caching or performance considerations]

## User Stories

[Organize user stories by persona or role. Use the standard format: "As a [persona], I want [goal] so that [benefit]."]

### As a [Persona 1]
- I want to [action] so that [benefit]
- I want to [action] so that [benefit]
- I want to [action] so that [benefit]

### As a [Persona 2]
- I want to [action] so that [benefit]
- I want to [action] so that [benefit]

### As a [Persona 3]
- I want to [action] so that [benefit]
- I want to [action] so that [benefit]

## Acceptance Criteria

[Testable, measurable criteria that define when this Feature is complete. Use checkboxes for tracking.]

- [ ] [Criterion 1 - specific and testable]
- [ ] [Criterion 2 - specific and testable]
- [ ] [Criterion 3 - specific and testable]
- [ ] [Criterion 4 - specific and testable]

## Scope

### In Scope
- [Deliverable 1]
- [Deliverable 2]
- [Deliverable 3]

### Out of Scope
- [What is explicitly NOT included in this Feature]
- [Future enhancements that may be separate Features]
- [Related features that are handled elsewhere]

## Dependencies

### Prerequisite Features
- Feature-XXX: [What must be completed first]
- Feature-YYY: [What must be completed first]

### Blocks Features
- Feature-AAA: [What depends on this Feature]
- Feature-BBB: [What depends on this Feature]

### External Dependencies
- [System/API/Service]: [Description of dependency]
- [Team/Component]: [Description of dependency]
- [Infrastructure]: [Description of dependency]

## Success Criteria

[Measurable outcomes that indicate this Feature has achieved its goals. Should align with the problem statement and user stories.]

- **Visibility**: [What users can now see/understand]
- **Performance**: [Performance requirements or improvements]
- **Usability**: [Usability goals or improvements]
- **Scalability**: [How the solution handles scale]
- **Integration**: [How well it integrates with existing systems]

## Testing Strategy

### Unit Tests
- [Key areas to unit test]
- [Components that need test coverage]

### Integration Tests
- [Integration scenarios to test]
- [API or service integration points]

### E2E/Acceptance Tests
- [End-to-end scenarios matching acceptance criteria]
- [User workflow validation]

### Performance Tests
- [Performance scenarios if applicable]
- [Load or stress testing requirements]

## Success Metrics

[Quantifiable metrics that will be tracked to measure success]

- **[Metric 1]**: [Target value] - [How it's measured]
- **[Metric 2]**: [Target value] - [How it's measured]
- **[Metric 3]**: [Target value] - [How it's measured]

## Implementation Notes

[Space for notes during implementation. Can include:]
- [Technical decisions made during implementation]
- [Design patterns or approaches used]
- [Lessons learned]

## Open Questions

[Questions that need to be resolved before or during implementation]

- [Question 1]: [Context]
- [Question 2]: [Context]

## Risks & Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| [Risk 1] | [High/Med/Low] | [High/Med/Low] | [How to address] |
| [Risk 2] | [High/Med/Low] | [High/Med/Low] | [How to address] |

## Definition of Done

[Checklist of items that must be complete for this Feature to be considered done]

- [ ] All acceptance criteria met
- [ ] Unit tests written and passing
- [ ] Integration tests written and passing
- [ ] E2E tests written and passing
- [ ] Documentation updated
- [ ] Code reviewed and approved
- [ ] Performance requirements met
- [ ] Accessibility requirements met (if applicable)
- [ ] Security review completed (if applicable)
```

## Usage Guidelines

When generating Features using this template:

1. **Summary**: Keep it concise (1-3 sentences). Focus on what's being extended/added and who benefits.

2. **Background**: Provide context about current state and gaps. Reference existing documentation when available.

3. **Problem Statement**: Be specific about pain points. Use measurable language when possible.

4. **Proposed Solution**: Focus on WHAT, not HOW. Technical details belong in Technical Approach section.

5. **User Stories**: Organize by persona. Each story should clearly state the goal and benefit.

6. **Acceptance Criteria**: Must be testable and measurable. Use specific, unambiguous language.

7. **Success Criteria**: Should align with problem statement and be measurable.

8. **Adapt as Needed**: Not all sections are required for every Feature. Omit sections that don't apply, but maintain the overall structure.

## Extensions

This template can be extended with additional sections as needed:

- **Design Mockups**: Links to Figma, Miro, or design artifacts
- **API Specifications**: If the Feature involves API changes
- **Database Schema**: If data model changes are required
- **Migration Plan**: If existing data needs to be migrated
- **Rollout Strategy**: If phased rollout is planned
- **Monitoring & Observability**: What metrics/logs will be added