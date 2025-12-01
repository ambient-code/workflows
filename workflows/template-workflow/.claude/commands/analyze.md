# /analyze - Analyze Requirements and Context

## Purpose
Analyze the problem space, gather context from the codebase, and understand requirements. This command helps you investigate the current state and identify what needs to be done.

## Prerequisites
- Workspace initialized (run `/init` if not done)

## Arguments
- `description` (required): A description of what you want to analyze

## Process

1. **Parse the analysis request**
   - Understand what aspect needs to be analyzed (feature, bug, refactoring, etc.)
   - Identify the scope (specific files, modules, or entire codebase)

2. **Gather context**
   - Search relevant code files
   - Read related documentation
   - Identify dependencies and integrations
   - Review existing tests and specifications

3. **Perform analysis**
   - Identify current implementation (if any)
   - List gaps or issues
   - Note relevant patterns, conventions, and constraints
   - Consider edge cases and potential challenges

4. **Document findings**
   - Create a structured analysis document
   - Include code references with file:line notation
   - List questions that need clarification
   - Identify risks and dependencies

5. **Generate recommendations**
   - Suggest possible approaches
   - Highlight trade-offs
   - Recommend next steps

## Output
- Creates analysis document: `artifacts/specs/<feature-name>/analysis.md`
- Updates workflow state in `.workflow-config.json`

## Usage Examples

```
/analyze user authentication system
```

```
/analyze bug in payment processing module
```

```
/analyze database schema migration strategy
```

## Output Format

The analysis document includes:

```markdown
# Analysis: [Topic]

## Overview
Brief summary of the analysis

## Current State
- What exists today
- Current implementation details
- Relevant code references (file.ts:123)

## Findings
- Key observations
- Gaps or issues identified
- Relevant patterns and conventions

## Context
- Dependencies
- Integration points
- Related systems or modules

## Considerations
- Edge cases
- Performance implications
- Security considerations
- Scalability factors

## Questions
- Items needing clarification
- Decisions required

## Recommendations
- Suggested approaches
- Trade-offs to consider
- Recommended next steps

## References
- Links to relevant documentation
- Related tickets or issues
- Code references
```

## Notes
- This command is exploratory and does not modify code
- The analysis serves as input for the /plan command
- Multiple analyses can be performed for different aspects
- Analysis documents are versioned in the artifacts directory
