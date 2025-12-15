---
description: Prioritize RFEs using various prioritization frameworks and create an implementation roadmap.
displayName: Prioritize RFEs
icon: 🎯
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

This command helps prioritize RFEs and creates an implementation roadmap. It should be run after `/rfe.breakdown`.

1. **Load Context**:
   - Read `artifacts/rfes.md`
   - Read `artifacts/prd.md` for business goals and success metrics
   - Consider user input from $ARGUMENTS for prioritization criteria

2. **Gather Prioritization Input**:
   - Ask user about prioritization approach (if not specified in $ARGUMENTS):
     - **MoSCoW**: Must have, Should have, Could have, Won't have
     - **RICE**: Reach, Impact, Confidence, Effort
     - **Value vs. Effort**: 2x2 matrix
     - **Kano Model**: Basic, Performance, Excitement features
   - Ask about any constraints (deadlines, resource limits, dependencies)

3. **Apply Prioritization Framework**:

   ### MoSCoW Method
   Categorize each RFE:
   - **Must Have**: Critical for launch, non-negotiable
   - **Should Have**: Important but not critical
   - **Could Have**: Nice to have if time permits
   - **Won't Have**: Out of scope for this release

   ### RICE Scoring (if selected)
   For each RFE, score:
   - **Reach**: How many users affected? (per time period)
   - **Impact**: How much does it impact each user? (0.25=minimal, 0.5=low, 1=medium, 2=high, 3=massive)
   - **Confidence**: How confident are we? (percentage: 100%, 80%, 50%)
   - **Effort**: How much work? (person-months)
   - **RICE Score** = (Reach × Impact × Confidence) / Effort

   ### Value vs. Effort Matrix (if selected)
   Plot each RFE on 2x2 grid:
   - **Quick Wins**: High value, low effort (do first)
   - **Big Bets**: High value, high effort (plan carefully)
   - **Fill-ins**: Low value, low effort (do if time permits)
   - **Money Pit**: Low value, high effort (avoid/defer)

4. **Create Prioritization Document**: Generate `artifacts/prioritization.md`:

   ```markdown
   # RFE Prioritization & Roadmap

   **Source**: [Link to rfes.md]
   **Date**: [Current Date]
   **Prioritization Method**: [MoSCoW/RICE/Value-Effort/Custom]

   ## Prioritization Summary

   | Priority | Count | RFE IDs |
   |----------|-------|---------|
   | Must Have / High | X | RFE-001, RFE-003, RFE-005 |
   | Should Have / Medium | X | RFE-002, RFE-004 |
   | Could Have / Low | X | RFE-006, RFE-007 |

   ## Prioritization Details

   ### Must Have / High Priority

   #### RFE-001: [Title]
   - **Priority Rationale**: [Why this is must-have]
   - **Business Value**: [What business value it delivers]
   - **User Impact**: [How it affects users]
   - **Dependencies**: [What depends on this]
   - **Estimated Effort**: [Size]
   - **Target Release**: [Release/Phase]

   [Repeat for each high-priority RFE]

   ### Should Have / Medium Priority

   [Similar structure]

   ### Could Have / Low Priority

   [Similar structure]

   ## RICE Scoring (if applicable)

   | RFE ID | Title | Reach | Impact | Confidence | Effort | RICE Score | Priority |
   |--------|-------|-------|--------|------------|--------|------------|----------|
   | RFE-001 | [Title] | 1000 | 2 | 80% | 2 | 800 | High |
   | RFE-002 | [Title] | 500 | 1 | 100% | 1 | 500 | Medium |

   ## Value vs. Effort Matrix (if applicable)

   ```
   High Value
   │
   │  Big Bets        Quick Wins
   │  [RFE-004]       [RFE-001, RFE-003]
   │
   │
   │  Money Pit       Fill-ins
   │  [RFE-007]       [RFE-006]
   │
   └────────────────────────────── High Effort
   Low Effort
   ```

   ## Implementation Roadmap

   ### Phase 1: MVP / Foundation (Release 1.0)
   **Goal**: [What this phase achieves]
   **Duration**: [Estimated timeline]

   #### Included RFEs
   - RFE-001: [Title] - [Estimated effort]
   - RFE-002: [Title] - [Estimated effort]

   **Phase Total**: [Total effort]
   **Key Deliverables**: [What users get]
   **Success Metrics**: [How we measure success]

   ### Phase 2: Core Features (Release 1.1)
   [Similar structure]

   ### Phase 3: Enhancements (Release 1.2)
   [Similar structure]

   ### Future Considerations (Backlog)
   - RFE-XXX: [Title] - [Why deferred]

   ## Dependency-Driven Sequence

   **Critical Path**:
   1. RFE-001 (Foundation) →
   2. RFE-003 (Depends on 001) →
   3. RFE-005 (Depends on 003)

   **Parallel Work Streams**:
   - **Stream A**: RFE-001 → RFE-003 → RFE-005
   - **Stream B**: RFE-002 → RFE-004 (can run in parallel)

   ## Risk-Adjusted Priority

   | RFE ID | Base Priority | Risk Level | Adjusted Priority | Rationale |
   |--------|---------------|------------|-------------------|-----------|
   | RFE-001 | High | Low | High | Safe to proceed |
   | RFE-004 | High | High | Medium | De-risk before committing |

   ## Trade-off Analysis

   ### If Timeline is Constrained
   **Recommended**: RFE-001, RFE-003 (Quick Wins)
   **Defer**: RFE-004, RFE-007 (Big Bets, Money Pit)

   ### If Resources are Constrained
   **Recommended**: Focus on Must-Have items only
   **Defer**: All Should-Have and Could-Have to Phase 2

   ## Stakeholder Alignment

   ### Business Goals Mapping
   - **Goal 1: [Business Goal]**
     - Supported by: RFE-001, RFE-003
   - **Goal 2: [Business Goal]**
     - Supported by: RFE-002, RFE-004

   ### User Needs Mapping
   - **User Need 1: [Need]**
     - Addressed by: RFE-001, RFE-005
   - **User Need 2: [Need]**
     - Addressed by: RFE-002

   ## Recommendations

   1. **Start with Phase 1 RFEs**: [List and rationale]
   2. **Parallel work**: [Which RFEs can be done in parallel]
   3. **Key dependencies**: [Critical path items]
   4. **Risk mitigation**: [High-risk items to address early]

   ## Next Steps

   - [ ] Review prioritization with stakeholders
   - [ ] Confirm roadmap phases
   - [ ] Begin implementation planning for Phase 1
   - [ ] Create detailed task breakdown for high-priority RFEs
   ```

5. **Validate Prioritization**:
   - Priorities align with business goals from PRD
   - Dependencies are respected in roadmap
   - Each phase delivers cohesive value
   - Effort estimates are realistic
   - Risks are identified and addressed

6. **Create Visual Roadmap** (optional): Generate `artifacts/roadmap-visual.md`:

   ```markdown
   # Visual Roadmap

   ## Timeline View

   ```
   Q1 2024          Q2 2024          Q3 2024
   ───────────────────────────────────────────
   Phase 1 MVP      Phase 2 Core     Phase 3
   │                │                │
   ├─ RFE-001 ─────┤                │
   ├─ RFE-002 ──────────────────────┤
   │  RFE-003 ──────┤                │
   │                └─ RFE-004 ──────┤
   │                   RFE-005 ──────┤
   ```

   ## Cumulative Value Delivery

   ```
   Value
   │        ╱─────
   │      ╱
   │    ╱
   │  ╱
   │╱
   └──────────────── Time
    P1   P2   P3
   ```
   ```

7. **Report Completion**:
   - Path to prioritization document
   - Summary of prioritization approach
   - Recommended implementation sequence
   - Total effort by phase
   - Next steps for implementation

## Guidelines

- Prioritization should be driven by business value and user impact
- Consider both dependencies and risks
- Create realistic roadmap phases
- Each phase should deliver cohesive value
- Document trade-offs and rationale for decisions
- Align priorities with PRD goals and success metrics
- Be transparent about what's being deferred and why
