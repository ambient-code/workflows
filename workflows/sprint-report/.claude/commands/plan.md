# /plan - Create Implementation Plan or Specification

## Purpose
Create a detailed implementation plan or specification based on requirements and analysis. This command generates a structured document that serves as a blueprint for implementation.

## Prerequisites
- Workspace initialized (run `/init` if not done)
- Analysis completed (recommended: run `/analyze` first)

## Arguments
- `description` (required): What you want to plan or specify

## Process

1. **Review context**
   - Read any existing analysis documents
   - Review relevant code and documentation
   - Understand requirements and constraints

2. **Define scope and objectives**
   - Clarify what will be built or changed
   - Set clear success criteria
   - Identify what is out of scope

3. **Design the solution**
   - Define the technical approach
   - Identify components and their responsibilities
   - Plan data models, APIs, or interfaces
   - Consider error handling and edge cases

4. **Break down the work**
   - List major implementation phases
   - Identify dependencies between components
   - Estimate complexity or effort

5. **Plan for quality**
   - Define testing strategy
   - Plan for security and performance
   - Consider monitoring and observability

6. **Document the plan**
   - Create a comprehensive specification or plan document
   - Include diagrams where helpful
   - Reference related analysis and requirements

## Output
- Creates plan document: `artifacts/plans/<feature-name>/plan.md`
- May create supporting documents (diagrams, schemas, etc.)
- Updates workflow state in `.workflow-config.json`

## Usage Examples

```
/plan user authentication with OAuth2
```

```
/plan database migration to PostgreSQL
```

```
/plan refactor payment processing module
```

## Output Format

The plan document includes:

```markdown
# Plan: [Feature/Project Name]

## Executive Summary
Brief overview of the plan

## Objectives
- What we aim to achieve
- Success criteria
- Metrics for success

## Scope
### In Scope
- What will be implemented

### Out of Scope
- What will not be included

## Technical Approach

### Architecture
- High-level design
- Components and their responsibilities
- Integration points

### Data Model
- Database schema changes
- Data structures
- APIs and interfaces

### Implementation Phases
1. Phase 1: [Name]
   - Tasks and deliverables
   - Dependencies
   - Estimated effort

2. Phase 2: [Name]
   - Tasks and deliverables
   - Dependencies
   - Estimated effort

## Technical Decisions

### Decision 1: [Topic]
- **Options Considered**: A, B, C
- **Chosen Approach**: B
- **Rationale**: Why B is preferred
- **Trade-offs**: What we gain and lose

## Quality Assurance

### Testing Strategy
- Unit tests
- Integration tests
- End-to-end tests

### Security Considerations
- Authentication/authorization
- Data validation
- Security scanning

### Performance
- Expected performance characteristics
- Optimization strategies

## Implementation Guidelines
- Coding standards to follow
- Patterns to use
- Anti-patterns to avoid

## Dependencies
- External libraries or services
- Internal systems or modules
- Infrastructure requirements

## Risks and Mitigations
- Risk 1: [Description] → Mitigation: [Strategy]
- Risk 2: [Description] → Mitigation: [Strategy]

## Timeline and Milestones
- Milestone 1: [Date] - [Deliverable]
- Milestone 2: [Date] - [Deliverable]

## References
- Related analysis documents
- External documentation
- Similar implementations
```

## Notes
- The plan should be detailed enough to guide implementation
- Plans can be iterative—update them as you learn more
- Use this as a living document throughout implementation
- Reference the plan when running `/execute`
