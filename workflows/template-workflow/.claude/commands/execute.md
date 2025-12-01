# /execute - Execute Implementation

## Purpose
Execute the implementation based on the plan or specification. This command guides you through actually building the solution, writing code, creating tests, and generating necessary artifacts.

## Prerequisites
- Workspace initialized (run `/init` if not done)
- Plan created (recommended: run `/plan` first)

## Arguments
- `description` (required): What you want to implement or build

## Process

1. **Review the plan**
   - Read the implementation plan or specification
   - Understand the technical approach and phases
   - Identify the current phase or task

2. **Set up implementation tracking**
   - Create a task list for the work ahead
   - Mark current task as in progress

3. **Implement the solution**
   - Write code following the plan
   - Apply coding standards and best practices
   - Add inline documentation and comments
   - Handle error cases and edge conditions

4. **Create or update tests**
   - Write unit tests for new functionality
   - Add integration tests where needed
   - Ensure test coverage meets standards
   - Run tests and fix any failures

5. **Update documentation**
   - Update API documentation
   - Add usage examples
   - Update README files
   - Create migration guides if needed

6. **Verify the implementation**
   - Run all tests
   - Perform manual testing
   - Check for security vulnerabilities
   - Validate performance

7. **Document the implementation**
   - Create an implementation summary
   - Note any deviations from the plan
   - Document design decisions made during implementation
   - List follow-up items or technical debt

## Output
- Implementation artifacts: `artifacts/implementation/<feature-name>/`
- Test files: In appropriate test directories
- Documentation: `artifacts/docs/<feature-name>/`
- Implementation summary: `artifacts/implementation/<feature-name>/summary.md`
- Updates workflow state in `.workflow-config.json`

## Usage Examples

```
/execute user authentication system
```

```
/execute phase 1 of database migration
```

```
/execute payment processing refactoring
```

## Output Format

### Implementation Summary Document

```markdown
# Implementation Summary: [Feature/Project Name]

## Overview
Brief description of what was implemented

## Implementation Details

### Files Created
- `path/to/file1.ts` - Description
- `path/to/file2.ts` - Description

### Files Modified
- `path/to/file3.ts:123-145` - Description of changes
- `path/to/file4.ts:67-89` - Description of changes

### Key Components

#### Component 1: [Name]
- **Purpose**: What it does
- **Location**: `path/to/component.ts`
- **Key Methods/Functions**:
  - `functionName()` - Description

#### Component 2: [Name]
- **Purpose**: What it does
- **Location**: `path/to/component.ts`
- **Key Methods/Functions**:
  - `functionName()` - Description

## Testing

### Tests Created
- `path/to/test1.test.ts` - Unit tests for Component 1
- `path/to/test2.test.ts` - Integration tests for Feature X

### Test Coverage
- Component 1: 95%
- Component 2: 87%
- Overall: 91%

### Test Results
```
✓ All tests passing (45 tests)
✓ No security vulnerabilities detected
✓ Performance benchmarks met
```

## Design Decisions

### Decision 1: [Topic]
- **Context**: The situation requiring a decision
- **Decision**: What was chosen
- **Rationale**: Why this approach
- **Alternatives**: What was considered but not chosen

## Deviations from Plan
- **Deviation 1**: Description and justification
- **Deviation 2**: Description and justification

## Challenges and Solutions
- **Challenge 1**: What the issue was → **Solution**: How it was resolved
- **Challenge 2**: What the issue was → **Solution**: How it was resolved

## Follow-up Items
- [ ] Technical debt item 1
- [ ] Future enhancement 1
- [ ] Documentation to update

## Verification Checklist
- [x] All tests passing
- [x] Code reviewed
- [x] Security scan completed
- [x] Performance validated
- [x] Documentation updated
- [x] Migration guide created (if applicable)

## How to Use

### Setup
```bash
# Installation or setup commands
npm install
```

### Basic Usage
```typescript
// Example code showing how to use the implemented feature
import { NewFeature } from './path/to/feature';

const feature = new NewFeature();
feature.doSomething();
```

### Configuration
```json
{
  "config": "example"
}
```

## References
- Implementation plan: `artifacts/plans/<feature-name>/plan.md`
- Analysis: `artifacts/specs/<feature-name>/analysis.md`
- Related PR: #123
```

## Notes
- Implementation should closely follow the plan
- Document deviations and the reasoning behind them
- Ensure all tests pass before marking complete
- Update the plan if you discover it needs changes
- Use the `/verify` command to validate the implementation
