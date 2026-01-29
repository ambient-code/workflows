---
description: Conduct product discovery to understand the problem space and user needs.
displayName: prd.discover
icon: 🔍
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

The text the user typed after `/prd.discover` in the triggering message is the initial problem or product idea. Use this to guide the discovery process.

**IMPORTANT: Agent Collaboration**

You MUST proactively invoke the following collaborating agents to ensure comprehensive discovery:

1. **@parker-product_manager.md** - For market strategy, competitive analysis, and opportunity quantification
2. **@ryan-ux_researcher.md** - CRITICAL: For user insights from research studies. This agent MUST access the "All UXR Reports" folder via the Google Workspace MCP server to ground requirements in available research. Every requirement should be research-informed with citations.
3. **@aria-ux_architect.md** (from bullpen) - For user journey mapping and ecosystem-level UX strategy

Invoke these agents at the start of the discovery process to leverage their expertise. Work collaboratively with them throughout the discovery phase.

Given that initial input, do this:

1. **Create Discovery Document**: Generate `discovery.md` with the following structure:

   ```markdown
   # Product Discovery: [Product/Feature Name]

   **Date**: [Current Date]
   **Status**: In Progress

   ## Problem Statement

   [What problem are we trying to solve?]

   ## User Research

   ### Target Users
   - [User persona 1]
   - [User persona 2]

   ### User Pain Points
   - [Pain point 1]
   - [Pain point 2]

   ### User Goals
   - [Goal 1]
   - [Goal 2]

   ## Market Analysis

   ### Competitive Landscape
   - [Competitor 1]: [Their approach]
   - [Competitor 2]: [Their approach]

   ### Market Opportunity
   [Size and scope of opportunity]

   ## Proposed Solution (High-Level)

   [Initial solution concept]

   ## Success Metrics

   - [Metric 1]
   - [Metric 2]

   ## Open Questions

   - [Question 1]
   - [Question 2]

   ## Next Steps

   - [ ] Complete user research
   - [ ] Validate problem-solution fit
   - [ ] Move to requirements gathering
   ```

2. **Conduct Discovery Research**:
   - Analyze the problem space based on user input
   - Identify target users and their needs
   - Research market context and competition
   - Define high-level success metrics
   - Document open questions that need answers

3. **Ask Clarifying Questions**:
   - If critical information is missing, ask the user:
     - Who are the target users?
     - What problem does this solve for them?
     - What are the business goals?
     - Are there competing solutions?
   - Limit to 3-5 most critical questions

4. **Generate Discovery Insights**:
   - Summarize key findings
   - Identify risks and assumptions
   - Recommend whether to proceed to requirements phase

5. **Report Completion**:
   - Path to discovery document
   - Key insights summary
   - Recommendation on next steps (run `/prd.rfe` if ready)

## Guidelines

- Focus on understanding the problem before jumping to solutions
- Use data and research to support insights
- Document assumptions clearly
- Identify what you don't know
- Be honest about gaps in understanding
