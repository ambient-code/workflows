# PRD & RFE Creation Workflow for Ambient Code Platform

A comprehensive workflow for creating Product Requirements Documents (PRDs) and systematically breaking them down into actionable Request for Enhancement (RFE) items. Guides product teams through the complete product definition lifecycle from discovery to implementation roadmap.

## Overview

This workflow provides a structured approach to product requirements and feature planning:
- **Discovery-Driven Process**: Six-phase methodology from discovery to prioritization
- **Requirements Excellence**: Emphasizes clear, testable, and measurable requirements
- **Structured Breakdown**: Systematic decomposition of PRDs into implementable RFEs
- **Prioritization Frameworks**: Multiple methods (MoSCoW, RICE, Value vs Effort)
- **Agent Collaboration**: Leverages specialized product and technical agents

## What's Included

### Directory Structure

```
prd-rfe-workflow/
├── .ambient/
│   └── ambient.json           # Workflow configuration
├── .claude/
│   ├── agents/                # Specialized agent personas
│   │   ├── quinn-product_strategist.md    # Product vision & strategy
│   │   ├── bailey-business_analyst.md     # Requirements analysis
│   │   ├── riley-product_owner.md         # RFE breakdown & prioritization
│   │   └── morgan-technical_writer.md     # Documentation quality
│   └── commands/              # Workflow phase commands
│       ├── prd.discover.md    # Phase 1: Product discovery
│       ├── prd.requirements.md # Phase 2: Requirements gathering
│       ├── prd.create.md      # Phase 3: PRD creation
│       ├── rfe.breakdown.md   # Phase 4: RFE decomposition
│       ├── rfe.prioritize.md  # Phase 5: Prioritization & roadmap
│       └── review.md          # Phase 6: Quality review
├── artifacts/                 # Generated artifacts (created during workflow)
└── README.md                  # This file
```

### Workflow Phases

The PRD-RFE Workflow follows a systematic 6-phase approach:

#### Phase 1: Discovery (`/prd.discover`)
**Purpose**: Conduct product discovery to understand the problem space and user needs

- Define the problem statement
- Research target users and their pain points
- Analyze competitive landscape and market opportunity
- Propose high-level solution concepts
- Define success metrics
- Document open questions and assumptions

**Output**: `artifacts/discovery.md`

**When to use**: Start here when exploring a new product idea or feature concept

**Agent Recommendation**: Invoke **Quinn (Product Strategist)** for strategic product discovery, market analysis, and vision development

#### Phase 2: Requirements (`/prd.requirements`)
**Purpose**: Gather and document detailed product requirements

- Transform user needs into specific requirements
- Write user stories with acceptance criteria
- Define functional and non-functional requirements
- Document constraints and dependencies
- Prioritize requirements (MoSCoW)
- Identify what's in scope and out of scope

**Output**: `artifacts/requirements.md`

**When to use**: After discovery phase, or jump here if you have a well-defined problem

**Agent Recommendation**: Invoke **Bailey (Business Analyst)** for requirements elicitation, acceptance criteria definition, and stakeholder alignment

#### Phase 3: Create PRD (`/prd.create`)
**Purpose**: Create a comprehensive Product Requirements Document

- Generate complete PRD from discovery and requirements
- Write executive summary and product vision
- Document goals, success metrics, and KPIs
- Define target users and personas
- Create detailed user stories and use cases
- Specify functional and non-functional requirements
- Define scope, assumptions, dependencies, and risks
- Validate PRD quality and completeness

**Output**:
- `artifacts/prd.md`
- `artifacts/prd-checklist.md`

**When to use**: After requirements gathering phase

**Agent Recommendations**:
- **Quinn (Product Strategist)** for strategic sections (vision, market positioning)
- **Bailey (Business Analyst)** for requirements sections
- **Morgan (Technical Writer)** for documentation quality review

#### Phase 4: RFE Breakdown (`/rfe.breakdown`)
**Purpose**: Break down the PRD into actionable Request for Enhancement items

- Analyze PRD for discrete, implementable units of work
- Create RFE master list with overview and summary
- Generate individual RFE documents with detailed specifications
- Define acceptance criteria for each RFE
- Identify dependencies between RFEs
- Size RFEs (Small/Medium/Large/XLarge)
- Create dependency graph and sequencing plan
- Validate completeness and traceability

**Output**:
- `artifacts/rfes.md` (Master RFE list)
- `artifacts/rfe-tasks/RFE-XXX-*.md` (Individual RFE documents)

**When to use**: After PRD creation and approval

**Agent Recommendation**: Invoke **Riley (Product Owner)** for breaking PRDs into RFEs, defining acceptance criteria, and managing dependencies

#### Phase 5: Prioritization (`/rfe.prioritize`)
**Purpose**: Prioritize RFEs and create implementation roadmap

- Apply prioritization framework (MoSCoW, RICE, Value vs Effort)
- Score and rank RFEs based on business value
- Create implementation roadmap with phases/releases
- Define dependency-driven sequence
- Perform risk-adjusted prioritization
- Map RFEs to business goals and user needs
- Generate recommendations for implementation order

**Output**:
- `artifacts/prioritization.md`
- `artifacts/roadmap-visual.md` (optional)

**When to use**: After RFE breakdown is complete

**Agent Recommendation**: Invoke **Riley (Product Owner)** for prioritization strategy and roadmap planning

#### Phase 6: Review (`/review`)
**Purpose**: Review all artifacts and validate completeness and quality

- Scan all generated artifacts for completeness
- Perform quality assessment (PRD, RFEs, prioritization)
- Create traceability matrix (PRD requirements → RFEs)
- Calculate quality scores and metrics
- Identify issues, gaps, and recommendations
- Assess readiness for stakeholder review and implementation
- Generate comprehensive review report

**Output**: `artifacts/review-report.md`

**When to use**: After all phases are complete, before stakeholder review

**Agent Recommendation**: Invoke **Morgan (Technical Writer)** for documentation quality review and clarity improvements

## Getting Started

### Quick Start

1. **Create an AgenticSession** in the Ambient Code Platform
2. **Select "PRD & RFE Creation"** from the workflows dropdown
3. **Start with `/prd.discover`** to begin product discovery
4. **Follow the phases** sequentially or jump to any phase based on your context

### Example Usage

**Scenario 1: New product idea**
```
User: "We want to add a user analytics dashboard to help users track their usage patterns"

Workflow: /prd.discover to understand the problem and opportunity
→ /prd.requirements to gather detailed requirements
→ /prd.create to generate comprehensive PRD
→ /rfe.breakdown to create implementable RFEs
→ /rfe.prioritize to plan implementation roadmap
→ /review to validate quality
```

**Scenario 2: You already have requirements**
```
User: "I have detailed requirements for a new reporting feature"

Workflow: Jump to /prd.create to generate PRD
→ /rfe.breakdown to create RFEs
→ /rfe.prioritize to plan roadmap
→ /review to validate
```

**Scenario 3: You have a PRD and need RFEs**
```
User: "I have a complete PRD for our mobile app redesign and need to break it into RFEs"

Workflow: Jump to /rfe.breakdown to decompose into RFEs
→ /rfe.prioritize to plan implementation
→ /review to validate coverage
```

### Prerequisites

- Clear understanding of the problem or product opportunity
- Access to user research, market data, or competitive analysis (helpful but not required)
- Stakeholder alignment on business goals and success metrics
- Understanding of technical constraints and dependencies (for RFE breakdown)

## Agent Orchestration

This workflow leverages specialized agents to ensure high-quality product documentation:

### Quinn - Product Strategist
**Product Vision, Strategy, and Discovery**

Quinn brings strategic product thinking and market expertise to the workflow.

**Quinn's Role:**
- Product discovery and problem validation
- Competitive analysis and market research
- Strategic PRD sections (vision, goals, positioning)
- Business outcome definition
- Value proposition development

**When to Engage:**
- Product discovery phase
- Strategic PRD sections
- Market opportunity analysis
- Product vision and goals definition

### Bailey - Business Analyst
**Requirements Elicitation and Documentation**

Bailey specializes in gathering, analyzing, and documenting detailed requirements.

**Bailey's Role:**
- Requirements gathering and analysis
- User story writing with acceptance criteria
- Process and workflow analysis
- Requirements traceability
- Gap and consistency analysis

**When to Engage:**
- Requirements gathering phase
- Detailed PRD requirements sections
- Acceptance criteria definition
- Requirements validation
- Traceability analysis

### Riley - Product Owner
**Backlog Management and Prioritization**

Riley excels at breaking down work and prioritizing for maximum value delivery.

**Riley's Role:**
- Breaking PRDs into implementable RFEs
- Defining RFE acceptance criteria
- Dependency identification and management
- Prioritization (MoSCoW, RICE, Value vs Effort)
- Roadmap and release planning

**When to Engage:**
- RFE breakdown phase
- Prioritization and roadmap planning
- Dependency analysis
- Scope negotiation
- MVP definition

### Morgan - Technical Writer
**Documentation Quality and Clarity**

Morgan ensures all documentation is clear, consistent, and professional.

**Morgan's Role:**
- PRD quality review and editing
- Documentation structure and flow
- Clarity and consistency improvements
- Terminology management
- Readability optimization

**When to Engage:**
- PRD review and editing
- Documentation quality checks
- Improving clarity and structure
- Final review phase

## Artifacts Generated

All workflow artifacts are organized in the `artifacts/` directory:

```
artifacts/
├── discovery.md                  # Product discovery document
├── requirements.md               # Detailed requirements
├── prd.md                        # Product Requirements Document
├── prd-checklist.md              # PRD quality checklist
├── rfes.md                       # RFE master list
├── rfe-tasks/                    # Individual RFE documents
│   ├── RFE-001-feature-name.md
│   ├── RFE-002-feature-name.md
│   └── ...
├── prioritization.md             # Prioritization and roadmap
├── roadmap-visual.md             # Visual roadmap (optional)
└── review-report.md              # Quality review report
```

## Best Practices

### Discovery
- Focus on understanding the problem before jumping to solutions
- Validate assumptions with user research and data
- Document what you don't know
- Identify risks and constraints early

### Requirements
- Make every requirement testable and measurable
- Use clear, unambiguous language
- Define acceptance criteria upfront
- Document assumptions and dependencies
- Clearly define what's in scope and out of scope

### PRD Creation
- Write for your audience (executives, stakeholders, technical teams)
- Focus on WHAT and WHY, not HOW
- Use measurable success metrics
- Include visual aids (tables, diagrams) where helpful
- Keep technical implementation details out of the PRD

### RFE Breakdown
- Each RFE should be independently valuable and deliverable
- Size RFEs appropriately (not too large, not too small)
- Define clear acceptance criteria for every RFE
- Ensure traceability back to PRD requirements
- Identify and document dependencies clearly

### Prioritization
- Prioritize based on business value and user impact
- Consider dependencies and risks
- Each roadmap phase should deliver cohesive value
- Be transparent about trade-offs and what's deferred
- Align priorities with business goals

### Review
- Check traceability from PRD to RFEs
- Validate completeness and quality
- Look for gaps, contradictions, and ambiguities
- Ensure documentation is stakeholder-ready
- Address critical issues before implementation

## Customization

### For Your Organization

You can customize this workflow by:

1. **Customizing PRD template** in `/prd.create` to match your org's format
2. **Adding custom prioritization methods** in `/rfe.prioritize`
3. **Modifying RFE sizing criteria** to match your team's velocity
4. **Adding company-specific agents** for domain expertise
5. **Extending phases** with additional validation steps
6. **Customizing artifact paths** to match your document management system

### Industry-Specific Adjustments

Adjust the workflow for different industries:

- **SaaS**: Add subscription metrics and user onboarding considerations
- **Enterprise**: Include compliance, security, and governance requirements
- **Mobile Apps**: Add app store requirements and device compatibility
- **Healthcare**: Include HIPAA and regulatory compliance
- **Financial Services**: Add security, audit, and compliance sections

## Troubleshooting

### Common Issues

**"The PRD is too vague or high-level"**
- Run `/prd.requirements` again to gather more detailed requirements
- Engage Bailey (Business Analyst) for requirements elicitation
- Ask clarifying questions to stakeholders
- Document assumptions and validate with users

**"RFEs are too large or too small"**
- Review RFE breakdown principles in `/rfe.breakdown`
- Engage Riley (Product Owner) for proper decomposition
- Consider dependencies and team capacity
- Aim for RFEs in the 2-10 day range

**"Priorities are unclear or conflicting"**
- Revisit business goals and success metrics in PRD
- Use multiple prioritization frameworks to triangulate
- Engage stakeholders to resolve conflicts
- Document trade-offs and rationale

**"Requirements aren't traceable to RFEs"**
- Run `/review` to generate traceability matrix
- Fill gaps by creating missing RFEs
- Consolidate or split RFEs as needed
- Update PRD if requirements changed

## Integration with ACP

This workflow integrates seamlessly with the Ambient Code Platform:

- **Workflow Selection**: Choose "PRD & RFE Creation" when creating AgenticSession
- **Artifact Management**: All outputs saved to `artifacts/` directory
- **Agent Invocation**: Automatically suggests agents based on phase and complexity
- **Progressive Disclosure**: Jump to any phase based on your context
- **Version Control**: All artifacts are plain markdown for easy versioning

## Contributing

Found issues with the workflow or have improvements?

- **Report issues**: [ambient-workflows issues](https://github.com/ambient-code/ambient-workflows/issues)
- **Suggest improvements**: Create a PR with your enhancements
- **Share learnings**: Document what worked well for your team

## License

This workflow is part of the Ambient Code Platform Workflows collection.

## Support

- **Documentation**: See [Ambient Code Platform docs](https://ambient-code.github.io/platform/)
- **Issues**: [File a bug](https://github.com/ambient-code/ambient-workflows/issues)
- **Questions**: Ask in the ACP community channels

---

**Happy Product Planning! 📋→🚀**
