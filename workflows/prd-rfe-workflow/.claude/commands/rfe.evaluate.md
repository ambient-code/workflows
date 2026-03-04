---
description: Evaluate RFE artifacts against quality criteria and append scores.
displayName: rfe.evaluate
icon: 📊
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

This command evaluates RFE documents against 5 quality criteria. It can evaluate a single RFE (if specified in $ARGUMENTS) or all RFEs in the `rfe-tasks/` directory.

1. **Determine Scope**:
   - If $ARGUMENTS contains a specific RFE file path or ID, evaluate only that RFE
   - If $ARGUMENTS is empty, evaluate ALL RFEs in `rfe-tasks/` directory

2. **Load RFE(s)**:
   - Read the target RFE file(s) from `rfe-tasks/`

3. **Evaluate Each RFE Against 5 Criteria** (score 1-5 each):

   ### Clarity of Purpose and Stakeholder Alignment
   - **1**: Vague problem statement; unclear who the user/stakeholder is or what they are trying to achieve.
   - **5**: Clearly defines the specific user role, the current pain point, and the desired business outcome.

   ### Structural Completeness and Organization
   - **1**: Unformatted "wall of text" or a random list of notes with no clear sections or logical flow.
   - **5**: Perfectly structured with logical headings (e.g., Scope, Risks, Assumptions) and professional formatting.

   ### Actionability and Testability
   - **1**: Lacks any definable acceptance criteria or next steps; impossible for a developer to know when the task is "done."
   - **5**: Includes precise, testable requirements and acceptance criteria that guide validation.

   ### Language Quality and Communicative Tone
   - **1**: Ambiguous, overly verbose, or unprofessional language; uses inappropriate jargon or casual slang.
   - **5**: Concise, precise, and maintains a highly professional technical tone throughout.

   ### Role Consistency and Perspective
   - **1**: Shows no distinguishable difference from a default/generic RFE; fails to adopt the assigned persona's concerns.
   - **5**: Frames the entire request using the assigned role's unique priorities (e.g., a Security Lead focusing on vulnerability, or a PM focusing on ROI).

4. **Append Evaluation Footer to Each RFE**:

   ```markdown
   ---
   ## Evaluation
   **Score**: X/25 | Clarity: X | Structure: X | Actionability: X | Language: X | Role: X

   [One sentence explaining the key factors that influenced the scores.]
   ```

   If an Evaluation section already exists, replace it.

5. **Report Results**:
   - Display scores for each evaluated RFE
   - Highlight any RFEs scoring below 15

## Guidelines

- Be objective and consistent in scoring
- Use the full 1-5 range - don't cluster scores in the middle
- The one-sentence assessment should identify the PRIMARY factor(s) affecting the score
- If an RFE scores below 15, suggest specific improvements
