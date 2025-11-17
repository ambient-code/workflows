# Template Workflow Feedback & Issues

This document captures issues, improvements, and learnings discovered while implementing the Bug Fix Workflow using the template workflow as a base.

**Created**: 2025-11-17
**Workflow**: Bug Fix Workflow
**Template Version**: Based on commit 7164ec1

---

## Summary

Overall, the template workflow is comprehensive and well-documented. However, several issues and improvement opportunities were identified during implementation that would benefit future workflow creators.

## Issues Identified

### 1. Missing `.mcp.json` Documentation

**Severity**: Medium
**Category**: Documentation Gap

**Issue**:
- Template README mentions `.mcp.json` for MCP server configurations
- No example `.mcp.json` file provided in the template
- No documentation on what should go in this file or when it's needed

**Impact**:
- Workflow creators unsure if they need MCP server configuration
- No guidance on how to structure `.mcp.json` if needed
- Inconsistent MCP integration across workflows

**Recommendation**:
- Add example `.mcp.json` to template with common MCP servers (GitHub, file system, etc.)
- Document when MCP servers are needed vs optional
- Provide configuration examples for different use cases

**Example needed**:
```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"]
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/workspace"]
    }
  }
}
```

---

### 2. Vague `results` Field Behavior

**Severity**: Medium
**Category**: Documentation Clarity

**Issue**:
- The `results` field in `ambient.json` uses glob patterns but documentation doesn't explain:
  - How results are displayed to users in the UI
  - Whether patterns are validated or just documentation
  - If the platform automatically detects these files
  - What happens if files don't match the patterns

**Impact**:
- Unclear if `results` field is prescriptive or descriptive
- Workflow creators don't know if they need to create exact paths
- No guidance on troubleshooting when results don't appear

**Recommendation**:
- Clarify whether `results` field is:
  - Auto-detection: Platform scans for matching files
  - Validation: Platform checks if files exist
  - Documentation only: Just for reference
- Document how results appear in the UI
- Provide examples of working vs non-working patterns

---

### 3. No Error Handling Guidance

**Severity**: High
**Category**: Missing Best Practices

**Issue**:
- Command templates show happy-path execution only
- No guidance on handling failures mid-workflow
- No pattern for resuming from failed steps
- No examples of error recovery

**Impact**:
- Workflows don't gracefully handle errors
- Users get stuck when commands fail
- No consistent error handling across workflows
- Difficult to resume interrupted workflows

**Recommendation**:
- Add "Error Handling" section to command template
- Show examples of:
  - Checking preconditions before executing
  - Handling partial failures
  - Providing clear error messages
  - Resuming from interruptions
- Document workflow state management patterns

**Example pattern needed**:
```markdown
## Error Handling

If this command fails:
- Check that [prerequisites] are met
- Verify [resources] exist
- Review error messages in [location]
- To resume: [steps to continue]

Common errors:
- "File not found": [solution]
- "Permission denied": [solution]
```

---

### 4. Agent Selection Clarity

**Severity**: Medium
**Category**: Documentation & Guidance

**Issue**:
- Template doesn't explain when Claude should invoke which agent
- No guidance on multi-agent collaboration patterns
- Agent descriptions in workflow don't match agent file capabilities
- Unclear how to recommend agents in command files

**Impact**:
- Inconsistent agent invocation
- Agents under-utilized or over-utilized
- Workflow creators unsure how to design agent collaboration
- User confusion about when to expect agent involvement

**Recommendation**:
- Add "Agent Collaboration" section to template README
- Show examples of:
  - When to invoke agents automatically vs on request
  - How to design multi-agent workflows
  - Patterns for agent handoffs
  - Documenting agent recommendations in commands
- Create decision tree for agent selection

**Example pattern needed**:
```markdown
## Agent Invocation Patterns

**Automatic Invocation**:
- When command complexity exceeds threshold
- For specialized tasks (testing, security)

**User-Requested Invocation**:
- "Invoke Stella for complex debugging"

**Agent Handoffs**:
- Architect → Engineer → Tester
```

---

### 5. Artifacts Directory Inconsistency

**Severity**: Low
**Category**: Convention Clarification

**Issue**:
- Some examples use `artifacts/`, others use workflow-specific paths like `artifacts/bugfix/`
- No clear guidance on when to use which pattern
- Risk of artifacts conflicting between workflows

**Impact**:
- Inconsistent artifact organization across workflows
- Potential file conflicts if multiple workflows active
- Unclear cleanup and artifact management

**Recommendation**:
- Standardize on `artifacts/{workflow-name}/` pattern
- Document this convention clearly in template
- Update all examples to follow convention
- Add artifact cleanup guidance

---

### 6. Template Variable Documentation

**Severity**: Medium
**Category**: Feature Clarity

**Issue**:
- Examples show variables like `{{REPO_NAME}}` and `{{BRANCH_NAME}}`
- Not documented whether these are actually supported
- No list of available template variables
- Unclear how variable substitution works

**Impact**:
- Workflow creators use unsupported variables
- Variables don't get substituted, confusing users
- Missed opportunities to use dynamic context

**Recommendation**:
- Document all supported template variables
- Show examples of variable substitution
- Explain when variables are evaluated (startup vs runtime)
- Provide fallback patterns for unsupported variables

**Example documentation needed**:
```markdown
## Template Variables

Supported in `systemPrompt` and `startupPrompt`:

- `{{REPO_NAME}}` - Repository name
- `{{BRANCH_NAME}}` - Current branch
- `{{WORKSPACE_PATH}}` - Workspace directory
- `{{USER_NAME}}` - User creating session

Note: Variables are evaluated at session creation time.
```

---

### 7. Missing Testing Workflow Example

**Severity**: Medium
**Category**: Missing Example

**Issue**:
- Template workflow has init/analyze/plan/execute/verify
- No specific testing command example
- Testing is crucial for many workflows but not demonstrated

**Impact**:
- Workflow creators don't see testing patterns
- Testing gets tacked on instead of integrated
- No best practices for test artifact generation

**Recommendation**:
- Add `/test` command to template as optional example
- Show how to integrate testing into workflows
- Demonstrate test result artifact patterns
- Include testing best practices

---

## Improvements Implemented in Bug Fix Workflow

These improvements were made in the bugfix workflow and could be adopted by the template:

### 1. Progressive Disclosure Pattern

- Workflow supports jumping to any phase based on user context
- Clear guidance on when to use each phase
- Example scenarios showing different entry points

**Template could adopt**: "Getting Started" section with multiple entry point examples

### 2. Agent Attribution Headers

- Added HTML comments noting agent source repository
- Clear attribution to platform repository
- Helps maintain agent version synchronization

**Template could adopt**: Standard attribution pattern for copied/referenced agents

### 3. Comprehensive Command Structure

- Purpose, Prerequisites, Process, Output, Usage Examples, Notes, Agent Recommendations
- Consistent structure across all commands
- Makes commands self-documenting

**Template could adopt**: Standardize command file structure with required sections

### 4. Project-Specific Guidance

- Commands include project-specific examples (Go, Python, JS)
- Shows how to customize for different stacks
- Reduces friction for workflow creators

**Template could adopt**: Include multi-language examples in commands

### 5. Troubleshooting Section

- Common issues and solutions
- Decision guidance for edge cases
- Helps users self-serve

**Template could adopt**: Required troubleshooting section in README

---

## Additional Enhancement Ideas

### 1. Workflow Chaining

**Current state**: Each workflow is isolated
**Enhancement**: Allow workflows to invoke other workflows

**Use case**: Bug fix workflow could invoke spec-kit workflow for complex fixes requiring design

**Implementation**: Add `workflows` field to ambient.json with dependencies

### 2. Workflow State Management

**Current state**: No persistent state between commands
**Enhancement**: Track workflow progress and allow resumption

**Use case**: Long-running workflows interrupted mid-execution

**Implementation**: Create `artifacts/{workflow}/.workflow-state.json` to track progress

### 3. Pre-flight Checks

**Current state**: Commands assume environment is ready
**Enhancement**: Add optional `check.md` or `validate.md` command

**Use case**: Verify tools, dependencies, permissions before starting

**Implementation**: Add standard check command to template

### 4. Lifecycle Hooks

**Current state**: Only manual command execution
**Enhancement**: Add hooks for automation (pre/post command)

**Use case**: Auto-run formatters after /fix, auto-commit after /document

**Implementation**: Use `hooks` field in ambient.json for command triggers

### 5. Workflow Metrics

**Current state**: No visibility into workflow usage
**Enhancement**: Track command execution time, success rate

**Use case**: Identify slow or problematic workflow phases

**Implementation**: Add optional telemetry to workflow execution

---

## Template Usage Experience

### What Worked Well

✅ **Comprehensive inline documentation** in ambient.json
✅ **Clear directory structure** easy to understand and replicate
✅ **Detailed command examples** showed the expected format
✅ **FIELD_REFERENCE.md** comprehensive field documentation
✅ **Agent persona examples** demonstrated different roles

### What Could Be Improved

❌ **Missing MCP server configuration** left questions unanswered
❌ **Unclear results field behavior** required experimentation
❌ **No error handling patterns** had to design from scratch
❌ **Agent collaboration not documented** required inference
❌ **Template variables unclear** avoided using them

---

## Recommendations for Template Maintainers

### High Priority

1. **Add .mcp.json example** with common MCP servers
2. **Document `results` field behavior** (validation vs documentation)
3. **Add error handling section** to command template
4. **Standardize artifacts directory convention** (`artifacts/{workflow}/`)

### Medium Priority

5. **Add agent collaboration guidance** with decision tree
6. **Document template variables** or remove examples
7. **Add testing command example** to template
8. **Create troubleshooting section template** for READMEs

### Low Priority

9. **Consider workflow chaining** for future versions
10. **Add workflow state management** patterns
11. **Provide pre-flight check examples**

---

## Feedback for Template Repository

This feedback should be shared with the `ootb-ambient-workflows` repository maintainers via:

- **Issues**: Create individual issues for each high-priority item
- **Discussion**: Start discussion on agent collaboration patterns
- **PR**: Submit PR with improvements once discussed

**Next steps**:
1. File GitHub issues for critical gaps (MCP, results, error handling)
2. Propose agent collaboration documentation enhancement
3. Share bugfix workflow as example of best practices

---

## Conclusion

The template workflow provides a solid foundation for creating new workflows. The issues identified are mostly documentation gaps rather than fundamental problems. With targeted improvements to documentation and a few additional examples, the template would be even more valuable for workflow creators.

**Overall assessment**: ⭐⭐⭐⭐☆ (4/5)
- Strong foundation and structure
- Excellent inline documentation
- Minor gaps in edge case handling and examples

The Bug Fix Workflow implementation was successful and can serve as a reference for future workflow creators.
