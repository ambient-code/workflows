# Bug Fix Workflow for Ambient Code Platform

A systematic, comprehensive workflow for analyzing, fixing, and verifying software bugs with thorough documentation. Guides developers through the complete bug resolution lifecycle from reproduction to release.

## Overview

This workflow provides a structured approach to fixing software bugs:
- **Systematic Process**: Five-phase methodology from reproduction to documentation
- **Root Cause Focus**: Emphasizes understanding *why* bugs occur, not just *what* happens
- **Comprehensive Testing**: Ensures fixes work and prevents regression
- **Complete Documentation**: Creates all artifacts needed for release and future reference
- **Agent Collaboration**: Leverages specialized agents for complex scenarios

## What's Included

### Directory Structure

```
bugfix/
├── .ambient/
│   ├── ambient.json           # Workflow configuration
│   └── ambient.clean.json     # Clean version without comments
├── .claude/
│   ├── agents/                # Specialized agent personas
│   │   ├── stella-staff_engineer.md    # Complex debugging & root cause
│   │   ├── neil-test_engineer.md       # Testing strategy & verification
│   │   └── taylor-team_member.md       # Implementation support
│   └── commands/              # Workflow phase commands
│       ├── reproduce.md       # Phase 1: Bug reproduction
│       ├── diagnose.md        # Phase 2: Root cause analysis
│       ├── fix.md             # Phase 3: Implementation
│       ├── test.md            # Phase 4: Testing & verification
│       └── document.md        # Phase 5: Documentation
├── FIELD_REFERENCE.md         # Complete field documentation
└── README.md                  # This file
```

### Workflow Phases

The Bug Fix Workflow follows a systematic 5-phase approach:

#### Phase 1: Reproduce (`/reproduce`)
**Purpose**: Systematically reproduce the bug and document observable behavior

- Parse bug reports and extract key information
- Set up environment matching bug conditions
- Attempt reproduction with variations to understand boundaries
- Document minimal reproduction steps
- Create reproduction report with severity assessment

**Output**: `artifacts/bugfix/reports/reproduction.md`

**When to use**: Start here if you have a bug report, issue URL, or symptom description

#### Phase 2: Diagnose (`/diagnose`)
**Purpose**: Perform root cause analysis and assess impact

- Review reproduction report and understand failure conditions
- Analyze code paths and trace execution flow
- Examine git history and recent changes
- Form and test hypotheses about root cause
- Assess impact across the codebase
- Recommend fix approach

**Output**: `artifacts/bugfix/analysis/root-cause.md`

**When to use**: After successful reproduction, or skip here if you know the symptoms

**Agent Recommendation**: Invoke **Stella (Staff Engineer)** for complex architectural issues, race conditions, or system-level debugging

#### Phase 3: Fix (`/fix`)
**Purpose**: Implement the bug fix following best practices

- Review fix strategy from diagnosis phase
- Create feature branch (`bugfix/issue-{number}-{description}`)
- Implement minimal code changes to fix the bug
- Address similar patterns identified in analysis
- Run linters and formatters
- Document implementation choices

**Output**: Modified code files + `artifacts/bugfix/fixes/implementation-notes.md`

**When to use**: After diagnosis phase, or jump here if you already know the root cause

**Agent Recommendation**:
- **Taylor (Team Member)** for straightforward fixes
- **Stella (Staff Engineer)** for complex or architectural changes

#### Phase 4: Test (`/test`)
**Purpose**: Verify the fix and create regression tests

- Create regression test that fails without fix, passes with fix
- Write comprehensive unit tests for modified code
- Run integration tests in realistic scenarios
- Execute full test suite to catch side effects
- Perform manual verification of original reproduction steps
- Check for performance or security impacts

**Output**:
- New test files in repository
- `artifacts/bugfix/tests/verification.md`

**When to use**: After implementing the fix

**Agent Recommendation**: Invoke **Neil (Test Engineer)** for:
- Comprehensive test strategy design
- Complex integration test setup
- Performance testing guidance
- Security testing recommendations

#### Phase 5: Document (`/document`)
**Purpose**: Create complete documentation for the fix

- Update issue/ticket with root cause and fix summary
- Create release notes entry
- Write CHANGELOG addition
- Update code comments with issue references
- Draft team announcements
- Write PR description

**Output**: `artifacts/bugfix/docs/`:
- `issue-update.md` - Issue comment text
- `release-notes.md` - Release notes entry
- `changelog-entry.md` - CHANGELOG addition
- `team-announcement.md` - Internal communication
- `pr-description.md` - PR description (optional)
- `user-announcement.md` - Customer communication (optional)

**When to use**: After testing is complete

## Getting Started

### Quick Start

1. **Create an AgenticSession** in the Ambient Code Platform
2. **Select "Bug Fix Workflow"** from the workflows dropdown
3. **Provide context**: Bug report URL, issue number, or symptom description
4. **Start with `/reproduce`** to systematically document the bug
5. **Follow the phases** sequentially or jump to any phase based on your context

### Example Usage

**Scenario 1: You have a bug report**
```
User: "Fix bug https://github.com/org/repo/issues/425 - session status updates failing"

Workflow: Starts with /reproduce to confirm the bug
→ /diagnose to find root cause
→ /fix to implement solution
→ /test to verify fix
→ /document to create release notes
```

**Scenario 2: You know the symptoms**
```
User: "Sessions are failing to update status in the operator"

Workflow: Jumps to /diagnose for root cause analysis
→ /fix to implement
→ /test to verify
→ /document
```

**Scenario 3: You already know the fix**
```
User: "Missing retry logic in UpdateStatus call at operator/handlers/sessions.go:334"

Workflow: Jumps to /fix to implement
→ /test to verify
→ /document
```

### Prerequisites

- Access to the codebase where the bug exists
- Ability to run and test code locally or in appropriate environment
- Understanding of project coding standards and conventions
- Git access for creating branches and reviewing history

## Agent Orchestration

This workflow is orchestrated by **Amber**, the Ambient Code Platform's expert colleague and codebase intelligence agent.

### Amber - Workflow Orchestrator
**Codebase Illuminati, Pair Programmer, Proactive Maintenance**

Amber serves as your single point of contact throughout the bug fix workflow. Rather than manually selecting agents, Amber automatically coordinates the right specialists from the complete ACP agent ecosystem based on the complexity and nature of the task.

**Amber's Role:**
- **Intelligent Orchestration**: Automatically invokes appropriate specialists when needed
- **Proactive Engagement**: Brings in experts without requiring explicit requests
- **Adaptive Complexity Handling**: Scales from simple bugs to complex system-level issues
- **Complete Ecosystem Access**: Can engage any ACP platform agent as appropriate

**Specialists Amber May Engage:**

- **Stella (Staff Engineer)** - Complex debugging, root cause analysis, architectural issues, performance problems
- **Neil (Test Engineer)** - Comprehensive test strategies, integration testing, automation, security testing
- **Taylor (Team Member)** - Straightforward implementations, code quality, documentation
- **secure-software-braintrust** - Security vulnerability assessment and mitigation
- **sre-reliability-engineer** - Performance tuning, reliability issues, infrastructure debugging
- **frontend-performance-debugger** - Frontend-specific performance bugs
- **Terry (Technical Writer)** - Complex technical documentation, user-facing content
- **Tessa (Writing Manager)** - Documentation strategy, content coordination
- **And any other platform agents** as the situation warrants

**How It Works:**
You interact only with Amber. Amber assesses each phase of the workflow and automatically brings in the right expertise:
- Complex architectural bug? Amber engages Stella
- Need comprehensive testing? Amber consults Neil
- Security implications? Amber invokes the security braintrust
- Straightforward fix? Amber handles it directly or with Taylor

**Benefits:**
- **Simplified Workflow**: One interface (Amber) for all complexity levels
- **Expertise On-Demand**: Right specialist at the right time, automatically
- **No Agent Selection Burden**: Trust Amber to coordinate appropriately
- **Flexible and Adaptive**: Handles edge cases and unusual scenarios

## Artifacts Generated

All workflow artifacts are organized in the `artifacts/bugfix/` directory:

```
artifacts/bugfix/
├── reports/                  # Bug reproduction reports
│   └── reproduction.md
├── analysis/                 # Root cause analysis
│   └── root-cause.md
├── fixes/                    # Implementation notes
│   └── implementation-notes.md
├── tests/                    # Test results and verification
│   └── verification.md
├── docs/                     # Documentation and release notes
│   ├── issue-update.md
│   ├── release-notes.md
│   ├── changelog-entry.md
│   ├── team-announcement.md
│   └── pr-description.md
└── logs/                     # Execution logs
    └── *.log
```

## Best Practices

### Reproduction
- Take time to reproduce reliably - flaky reproduction leads to incomplete diagnosis
- Document even failed attempts - inability to reproduce is valuable information
- Create minimal reproduction steps that others can follow

### Diagnosis
- Understand the *why*, not just the *what*
- Document your reasoning process for future developers
- Use `file:line` notation when referencing code (e.g., `handlers.go:245`)
- Consider similar patterns elsewhere in the codebase

### Implementation
- Keep fixes minimal - only change what's necessary
- Don't combine refactoring with bug fixes
- Reference issue numbers in code comments
- Consider backward compatibility

### Testing
- Regression tests are mandatory - every fix must include a test
- Test the test - verify it fails without the fix
- Run the full test suite, not just new tests
- Manual verification matters

### Documentation
- Be clear and specific for future developers
- Link issues, PRs, and commits for easy navigation
- Consider your audience (technical vs. user-facing)
- Don't skip this step - documentation is as important as code

## Customization

### For Your Project

You can customize this workflow by:

1. **Adding project-specific linting commands** in `/fix` command
2. **Customizing test commands** in `/test` for your stack (Go, Python, JS, etc.)
3. **Adding custom agents** for domain-specific expertise
4. **Extending phases** with additional steps for your workflow
5. **Modifying artifact paths** to match your project structure

### Environment-Specific Adjustments

Adjust the workflow for different environments:

- **Microservices**: Add service dependency analysis to `/diagnose`
- **Frontend**: Include browser testing in `/test`
- **Backend**: Add database migration checks to `/fix`
- **Infrastructure**: Include deployment validation in `/test`

## Troubleshooting

### Common Issues

**"I can't reproduce the bug"**
- Document what you tried and what was different
- Check environment differences (versions, config, data)
- Ask the reporter for more details
- Consider it may be fixed or non-reproducible

**"Multiple potential root causes"**
- Document all hypotheses in `/diagnose`
- Test each systematically
- May need multiple fixes if multiple issues

**"Tests are failing after fix"**
- Check if tests were wrong or your fix broke something
- Review test assumptions
- Consider if behavior change was intentional

**"Fix is too complex"**
- Invoke Stella for complex scenarios
- Consider breaking into smaller fixes
- May indicate architectural issue

## Integration with ACP

This workflow integrates seamlessly with the Ambient Code Platform:

- **Workflow Selection**: Choose "Bug Fix Workflow" when creating AgenticSession
- **Multi-repo Support**: Works with single or multiple repositories
- **Artifact Management**: All outputs saved to `artifacts/bugfix/`
- **Agent Invocation**: Automatically suggests agents based on complexity
- **Progressive Disclosure**: Jump to any phase based on your context

## Contributing

Found issues with the workflow or have improvements?

- **Report issues**: [ootb-ambient-workflows issues](https://github.com/ambient-code/ootb-ambient-workflows/issues)
- **Suggest improvements**: Create a PR with your enhancements
- **Share learnings**: Document what worked well for your team

## License

This workflow is part of the Ambient Code Platform OOTB Workflows collection.

## Support

- **Documentation**: See [Ambient Code Platform docs](https://ambient-code.github.io/platform/)
- **Issues**: [File a bug](https://github.com/ambient-code/ootb-ambient-workflows/issues)
- **Questions**: Ask in the ACP community channels

---

**Happy Bug Fixing! 🐛→✅**
