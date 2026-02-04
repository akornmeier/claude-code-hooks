---
description: Full design process - PRD → Clarification → UX Spec → Build Prompts
argument-hint: <feature idea or description>
model: opus
---

# Design Command

Transform a rough feature idea into comprehensive, build-ready specifications through a 4-stage design process.

## Variables

FEATURE_IDEA: $ARGUMENTS
OUTPUT_DIR: `specs/`

## Process Overview

```
Stage 1: PRD-Lite        → specs/<name>-prd.md
Stage 2: PRD-Clarifier   → specs/<name>-clarification.md
Stage 3: PRD-to-UX       → specs/<name>-ux-spec.md
Stage 4: UX-to-Prompts   → specs/<name>-build-prompts.md
```

## Instructions

- If no `FEATURE_IDEA` is provided, use AskUserQuestion to gather it
- Execute all 4 stages IN ORDER - do not skip stages
- Write outputs to files in `OUTPUT_DIR` - do not output long content to conversation
- Generate a kebab-case name from the feature idea for file naming
- After completion, provide instructions for `/plan_w_team` or `/build`

---

# Stage 1: MVP to Demo PRD Generator

## Role

You are a senior product thinker helping a builder turn a rough MVP idea into a clear, demo-grade Product Requirements Document (PRD).

Your goal is decision clarity, not enterprise ceremony.

## Input Analysis

The user has provided: `FEATURE_IDEA`

You must infer missing details, but:
- Clearly label assumptions
- Avoid overengineering
- Optimize for a believable demo, not production scale

## PRD Output Structure (Write to `specs/<name>-prd.md`)

### 1. One-Sentence Problem

Write a sharp problem statement in this format:

> [User] struggles to [do X] because [reason], resulting in [impact].

If multiple problems exist, pick the single most demo-worthy one.

### 2. Demo Goal (What Success Looks Like)

Describe:
- What must work for this demo to be considered successful
- What outcome the demo should clearly communicate

Optionally include:
- Non-Goals (what is intentionally out of scope)

### 3. Target User (Role-Based)

Define one primary user role.

Include:
- Role / context
- Skill level
- Key constraint (time, knowledge, access, etc.)

Avoid personas or demographics.

### 4. Core Use Case (Happy Path)

Describe the single most important end-to-end flow.

Include:
- Start condition
- Step-by-step flow (numbered)
- End condition

If this flow works, the demo works.

### 5. Functional Decisions (What It Must Do)

List only required functional capabilities.

Use this table:

| ID | Function | Notes |
|----|----------|-------|

Rules:
- Phrase as capabilities, not implementation
- No "nice-to-haves"
- Keep the list tight

### 6. UX Decisions (What the Experience Is Like)

Explicitly define UX assumptions so nothing is left implicit.

#### 6.1 Entry Point
- How the user starts
- What they see first

#### 6.2 Inputs
What the user provides (if anything).

#### 6.3 Outputs
What the user receives and in what form.

#### 6.4 Feedback & States
How the system communicates:
- Loading
- Success
- Failure
- Partial results

#### 6.5 Errors (Minimum Viable Handling)
What happens when:
- Input is invalid
- The system fails
- The user does nothing

### 7. Data & Logic (At a Glance)

#### 7.1 Inputs
Where data comes from: User, API, Static/mocked, Generated

#### 7.2 Processing
High-level logic only (no architecture diagrams).
Example: Input → transform → output

#### 7.3 Outputs
Where results go: UI only, Temporarily stored, Logged

### 8. Brand & Design Context

**IMPORTANT**: Before finalizing the PRD, search the codebase for:
- Existing design tokens, themes, or style guides
- Brand assets (logos, colors, typography)
- Component libraries or UI patterns in use
- Related features that should inform consistency

Document findings:
- Design system location (if any)
- Key brand colors/fonts
- Existing component patterns to reuse
- Consistency requirements with other features

---

# Stage 2: PRD Clarification

After writing the PRD, systematically clarify ambiguities through structured questioning.

## Create Tracking Document

Write to `specs/<name>-clarification.md`:

```markdown
# PRD Clarification Session

**Source PRD**: <name>-prd.md
**Session Started**: [date/time]
**Depth Selected**: [pending]
**Progress**: 0/[total]

---

## Session Log
```

## Ask Depth Preference

Use AskUserQuestion:

```json
{
  "questions": [{
    "question": "What depth of PRD analysis would you like?",
    "header": "Depth",
    "multiSelect": false,
    "options": [
      {"label": "Quick (5 questions)", "description": "Rapid surface-level review of critical ambiguities only"},
      {"label": "Medium (10 questions)", "description": "Balanced analysis covering key requirement areas"},
      {"label": "Long (20 questions)", "description": "Comprehensive review with detailed exploration"},
      {"label": "Ultralong (35 questions)", "description": "Exhaustive deep-dive leaving no stone unturned"}
    ]
  }]
}
```

## Questioning Strategy

Prioritize questions by impact:
1. **Critical Path Items**: Requirements blocking other features
2. **High-Ambiguity Areas**: Vague language, missing acceptance criteria
3. **Integration Points**: Interfaces with external systems
4. **Edge Cases**: Error handling, boundary conditions
5. **Non-Functional Requirements**: Performance, accessibility gaps
6. **User Journey Gaps**: Missing steps, undefined user states

## Question Quality Standards

Each question MUST be:
- **Specific**: Reference exact sections from the PRD
- **Actionable**: Answer directly informs a requirement update
- **Non-leading**: Avoid suggesting the "right" answer
- **Singular**: One clear question per turn

Use AskUserQuestion with 2-4 options for EVERY question.

Update the tracking document after EACH answer.

---

# Stage 3: PRD to UX Specification

Transform the clarified PRD into UX foundations through **6 forced designer mindset passes**.

**Core principle:** UX foundations come BEFORE visual specifications. Mental models, information architecture, and cognitive load analysis prevent "pretty but unusable" designs.

## The Iron Law

```
NO VISUAL SPECS UNTIL ALL 6 PASSES COMPLETE
```

- Don't mention colors, typography, or spacing until Pass 6 is done
- Don't describe screen layouts until information architecture is explicit
- Don't design components until affordances are mapped

## Write to `specs/<name>-ux-spec.md`

### Pass 1: User Intent & Mental Model Alignment

**Designer mindset:** "What does the user think is happening?"

**Force these questions:**
- What does the user believe this system does?
- What are they trying to accomplish in one sentence?
- What wrong mental models are likely?

**Output:**
```markdown
## Pass 1: Mental Model

**Primary user intent:** [One sentence]

**Likely misconceptions:**
- [Misconception 1]
- [Misconception 2]

**UX principle to reinforce/correct:** [Specific principle]
```

### Pass 2: Information Architecture

**Designer mindset:** "What exists, and how is it organized?"

**Actions:**
1. Enumerate ALL concepts the user will encounter
2. Group into logical buckets
3. Classify each as: Primary / Secondary / Hidden (progressive)

**Output:**
```markdown
## Pass 2: Information Architecture

**All user-visible concepts:**
- [Concept 1]
- [Concept 2]

**Grouped structure:**

### [Group Name]
- [Concept]: [Primary/Secondary/Hidden]
- Rationale: [One sentence]
```

### Pass 3: Affordances & Action Clarity

**Designer mindset:** "What actions are obvious without explanation?"

**Force explicit decisions:**
- What is clickable?
- What looks editable?
- What looks like output (read-only)?

**Output:**
```markdown
## Pass 3: Affordances

| Action | Visual/Interaction Signal |
|--------|--------------------------|
| [Action] | [What makes it obvious] |

**Affordance rules:**
- If user sees X, they should assume Y
```

### Pass 4: Cognitive Load & Decision Minimization

**Designer mindset:** "Where will the user hesitate?"

**Identify:**
- Moments of choice (decisions required)
- Moments of uncertainty (unclear what to do)
- Moments of waiting (system processing)

**Apply:**
- Collapse decisions (fewer choices)
- Delay complexity (progressive disclosure)
- Introduce defaults (reduce decision burden)

**Output:**
```markdown
## Pass 4: Cognitive Load

**Friction points:**
| Moment | Type | Simplification |
|--------|------|----------------|
| [Where] | Choice/Uncertainty/Waiting | [How to reduce] |

**Defaults introduced:**
- [Default 1]: [Rationale]
```

### Pass 5: State Design & Feedback

**Designer mindset:** "How does the system talk back?"

**For EACH major element, enumerate states:**
- Empty
- Loading
- Success
- Partial (incomplete data)
- Error

**Output:**
```markdown
## Pass 5: State Design

### [Element/Screen]
| State | User Sees | User Understands | User Can Do |
|-------|-----------|------------------|-------------|
| Empty | | | |
| Loading | | | |
| Success | | | |
| Partial | | | |
| Error | | | |
```

### Pass 6: Flow Integrity Check

**Designer mindset:** "Does this feel inevitable?"

**Sanity check:**
- Where could users get lost?
- Where would a first-time user fail?
- What must be visible vs can be implied?

**Output:**
```markdown
## Pass 6: Flow Integrity

**Flow risks:**
| Risk | Where | Mitigation |
|------|-------|------------|
| [Risk] | [Location] | [Guardrail/Nudge] |

**Visibility decisions:**
- Must be visible: [List]
- Can be implied: [List]

**UX constraints:** [Hard rules for visual phase]
```

---

# Stage 4: UX Spec to Build-Order Prompts

Transform the UX spec into sequential, self-contained prompts for implementation.

## Write to `specs/<name>-build-prompts.md`

## Build Order Strategy

Generate prompts in this order:

| Phase | What to Include | Why First |
|-------|-----------------|-----------|
| **1. Foundation** | Design tokens, shared types, base styles | Everything depends on these |
| **2. Layout Shell** | Page structure, navigation, panels | Container for all features |
| **3. Core Components** | Primary UI elements | Building blocks |
| **4. Interactions** | Drag-drop, connections, pickers | Depend on components |
| **5. States & Feedback** | Empty, loading, error, success | Refinement layer |
| **6. Polish** | Animations, responsive, edge cases | Final layer |

## Prompt Structure Template

Each prompt follows this structure:

```markdown
## [Feature Name]

### Context
[What this feature is and where it fits]

### Requirements
- [Specific behavior/appearance requirement]
- [Include specs: dimensions, colors, states]

### States
- Default: [description]
- [Other states]

### Interactions
- [How user interacts]
- [Keyboard support if applicable]

### Constraints
- [Technical or design constraints]
- [What NOT to include]
```

## Self-Containment Rules

Each prompt MUST:
- Include enough context to understand in isolation
- Include all visual specs relevant to that feature
- Include all states that feature can be in
- Include all interactions for that feature

Each prompt MUST NOT:
- Reference "see previous prompt"
- Assume knowledge from other prompts
- Leave specs vague ("appropriate styling")

## Output Format

```markdown
# Build-Order Prompts: [Project Name]

## Overview
[1-2 sentence summary]

## Build Sequence
1. [Prompt name] - [brief description]
2. [Prompt name] - [brief description]
...

---

## Prompt 1: [Feature Name]
[Full self-contained prompt]

---

## Prompt 2: [Feature Name]
[Full self-contained prompt]
```

---

# Completion

After all 4 stages, report:

```
✅ Design Process Complete

Files created:
- specs/<name>-prd.md
- specs/<name>-clarification.md
- specs/<name>-ux-spec.md
- specs/<name>-build-prompts.md

Next steps:
1. Review the build prompts in specs/<name>-build-prompts.md
2. Run: /plan_w_team specs/<name>-build-prompts.md
   OR
3. Run: /build specs/<name>-build-prompts.md
```
