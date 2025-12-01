# Claude Assistant Guidelines

## Sub-Agent Usage

You have access to specialized sub-agents that can help you complete tasks more effectively. **Use them proactively** when appropriate.

### Available Agents

**Engineering & Architecture:**
- **Archie (Architect)**: System design, technical vision, architectural patterns, long-term planning
- **Stella (Staff Engineer)**: Technical leadership, implementation excellence, code review, mentoring
- **Emma (Engineering Manager)**: Team coordination, delivery management, technical planning
- **Lee (Team Lead)**: Technical execution, team coordination, hands-on development
- **Taylor (Team Member)**: Individual contribution, feature implementation
- **Neil (Test Engineer)**: Testing strategy, QA, test automation, quality assurance

**Product & Strategy:**
- **Parker (Product Manager)**: Market strategy, customer feedback, business value, roadmap decisions
- **Olivia (Product Owner)**: Backlog management, user stories, sprint planning, stakeholder communication
- **Dan (Senior Director)**: Strategic direction, cross-team coordination, executive alignment
- **Diego (Program Manager)**: Multi-team coordination, dependency management, risk mitigation
- **Sam (Scrum Master)**: Agile process, team facilitation, impediment removal
- **Jack (Delivery Owner)**: Release planning, deployment coordination, delivery tracking

**UX & Design:**
- **Aria (UX Architect)**: UX strategy, journey mapping, design system architecture
- **Uma (UX Team Lead)**: UX team coordination, design quality, research oversight
- **Felix (UX Feature Lead)**: Feature-level UX design, interaction design
- **Steve (UX Designer)**: Visual design, prototyping, user interface design
- **Ryan (UX Researcher)**: User research, usability testing, data analysis
- **Phoenix (PxE Specialist)**: Product experience optimization, user journey refinement

**Content & Documentation:**
- **Terry (Technical Writer)**: Documentation, API docs, user guides
- **Tessa (Writing Manager)**: Content strategy, documentation planning, editorial oversight
- **Casey (Content Strategist)**: Content planning, messaging, information architecture

### When to Use Sub-Agents

- Complex technical decisions requiring specialized expertise
- Breaking down multi-faceted problems (product + engineering + UX)
- Getting domain-specific perspectives (architecture, testing, UX, etc.)
- Planning features that span multiple disciplines
- Code reviews and technical analysis requiring senior perspective
- Market analysis and competitive research
- User experience and journey mapping
- Documentation and content strategy

**Don't hesitate to delegate** - these agents bring specialized expertise and perspectives that will improve the quality of your work.

### Important Usage Notes

- **ALWAYS omit the `model` parameter** when calling tools and sub-agents. The system will automatically use the appropriate model.
- Invoke agents by their full name (e.g., "archie-architect", "parker-product_manager") using the Task tool.

