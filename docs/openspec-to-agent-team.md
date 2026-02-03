# OpenSpec to Agent Team Orchestration

This guide shows how to take an existing OpenSpec requirement document and execute it using the agent team orchestration approach.

## The Workflow

```
┌─────────────────────────────────────────────────────────────┐
│  1. OPENSPEC DOCUMENT (Your requirement)                     │
│     └── docs/plans/2026-01-29-tag-filter-button-design.md   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  2. /plan (plan_w_team command)                              │
│     └── Transforms spec into executable team plan           │
│     └── Output: specs/<name>-team-plan.md                   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  3. /build (execute the plan)                                │
│     └── Orchestrator creates TaskList                       │
│     └── Deploys Builder agents for each task                │
│     └── Deploys Validator agents to verify                  │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  4. COMPLETED FEATURE                                        │
│     └── All tasks completed                                 │
│     └── All validations passed                              │
│     └── Code quality gates satisfied                        │
└─────────────────────────────────────────────────────────────┘
```

---

## Step 1: Start with Your OpenSpec Document

Example: `docs/plans/2026-01-29-tag-filter-button-design.md`

```markdown
# Tag Filter Button Design

## Summary
- Location: After status tabs in toolbar
- Interaction: Button morphs into expanded dialog
- State indicator: Badge count on collapsed button

## Components
### TagFilterButton (molecules/tags/)
...

## Files
| File                                  | Action |
|---------------------------------------|--------|
| molecules/tags/TagFilterButton.tsx    | Create |
| molecules/tags/TagFilterButton.test.tsx | Create |
| convex/articles.ts                    | Modify |

## Testing
- Badge shows correct count
- onSelectionChange called with correct IDs
```

---

## Step 2: Run `/plan` with Team Orchestration

In Claude Code, run:

```
/plan docs/plans/2026-01-29-tag-filter-button-design.md
```

Or with explicit orchestration guidance:

```
/plan docs/plans/2026-01-29-tag-filter-button-design.md "Use TDD builders for components, convex-builder for backend. Parallel where possible."
```

### What the `/plan` Command Does

1. **Reads your OpenSpec** - Understands the requirements, components, files
2. **Designs team composition** - Assigns specialized builders for each domain
3. **Creates task dependencies** - Orders work correctly (backend before frontend integration)
4. **Generates executable plan** - Saves to `specs/<name>-team-plan.md`

### Example Generated Plan

```markdown
# Plan: Tag Filter Button Implementation

## Task Description
Implement the tag filter button feature as specified in the design doc...

## Objective
Users can filter articles by tag via a morphing button/dialog...

## Team Orchestration

### Team Members

- Builder (Backend)
  - Name: convex-builder
  - Role: Implement tagIds filter in articles.list query
  - Agent Type: convex-builder
  - Resume: true

- Builder (Component)
  - Name: component-builder
  - Role: Create TagFilterButton with Motion animations
  - Agent Type: tdd-builder
  - Resume: true

- Builder (Integration)
  - Name: integration-builder
  - Role: Wire up URL params and page integration
  - Agent Type: ts-builder
  - Resume: true

- Validator
  - Name: feature-validator
  - Role: Verify all acceptance criteria met
  - Agent Type: ts-validator
  - Resume: true

## Step by Step Tasks

### 1. Implement Backend Filter
- **Task ID**: backend-filter
- **Depends On**: none
- **Assigned To**: convex-builder
- **Agent Type**: convex-builder
- **Parallel**: true
- Add `tagIds?: Id<"tags">[]` param to `api.articles.list`
- Use `by_user_and_tag` index for filtering
- Write backend tests

### 2. Create TagFilterButton Component
- **Task ID**: create-component
- **Depends On**: none
- **Assigned To**: component-builder
- **Agent Type**: tdd-builder
- **Parallel**: true
- Write tests first (TagFilterButton.test.tsx)
- Implement component with Motion layoutId
- Add Storybook stories

### 3. Create TagPicker Stories
- **Task ID**: tagpicker-stories
- **Depends On**: none
- **Assigned To**: component-builder
- **Agent Type**: tdd-builder
- **Parallel**: true
- Create TagPicker.stories.tsx
- Cover all interaction states

### 4. Integrate with Articles Page
- **Task ID**: page-integration
- **Depends On**: backend-filter, create-component
- **Assigned To**: integration-builder
- **Agent Type**: ts-builder
- **Parallel**: false
- Add URL param parsing for `?tags=id1,id2`
- Pass tagIds to articlesQuery
- Wire up TagFilterButton

### 5. Final Validation
- **Task ID**: validate-all
- **Depends On**: page-integration, tagpicker-stories
- **Assigned To**: feature-validator
- **Agent Type**: ts-validator
- **Parallel**: false
- Run all tests
- Verify Storybook stories render
- Check type errors
- Verify URL param persistence works

## Acceptance Criteria

1. [ ] Badge shows correct selected tag count
2. [ ] Button morphs smoothly to dialog
3. [ ] Tag selection persists in URL
4. [ ] Articles filter correctly by selected tags
5. [ ] All tests pass
6. [ ] No TypeScript errors
```

---

## Step 3: Execute with `/build`

```
/build specs/tag-filter-button-team-plan.md
```

### What Happens During Execution

1. **Orchestrator reads the plan** and creates TaskList
2. **Parallel tasks start simultaneously**:
   - `convex-builder` works on backend filter
   - `tdd-builder` writes tests then implements TagFilterButton
3. **Each builder reports completion** via TaskUpdate
4. **Dependent tasks unblock** when dependencies complete
5. **Validators verify** each completed task
6. **Self-validation hooks enforce quality**:
   - TDD enforcer ensures tests written first
   - OXLint validates no lint errors
   - TSC validates no type errors

### Monitoring Progress

The orchestrator shows real-time updates:

```
✓ Task 1: backend-filter (convex-builder) - Completed
✓ Task 2: create-component (component-builder) - Completed
✓ Task 3: tagpicker-stories (component-builder) - Completed
⏳ Task 4: page-integration (integration-builder) - In Progress
⏸ Task 5: validate-all - Blocked by: page-integration
```

---

## Step 4: Stached-Specific Agent Selection

For Stached, use these specialized agents:

| Domain | Agent | Why |
|--------|-------|-----|
| Convex backend | `convex-builder` | Knows Convex patterns, validates types |
| React components | `tdd-builder` | Enforces tests first, lint/type gates |
| Content parsing | `article-parser` | Readability, sanitization expertise |
| Browser extension | `extension-builder` | WXT, Manifest V3 knowledge |
| Integration work | `ts-builder` | Standard quality gates without TDD |
| Verification | `ts-validator` | Read-only validation |

---

## Example: Full Workflow

### 1. You have an OpenSpec doc

```bash
cat docs/plans/2026-01-29-tag-filter-button-design.md
```

### 2. Create the team plan

```bash
# In Claude Code
/plan docs/plans/2026-01-29-tag-filter-button-design.md "Use convex-builder for backend, tdd-builder for components"
```

### 3. Review the generated plan

```bash
cat specs/tag-filter-button-team-plan.md
```

### 4. Execute the plan

```bash
# In Claude Code
/build specs/tag-filter-button-team-plan.md
```

### 5. Watch agents work

```
[convex-builder] Implementing tagIds filter...
[tdd-builder] Writing TagFilterButton.test.tsx...
[tdd-builder] Tests written, now implementing component...
[ts-builder] Wiring up URL params...
[ts-validator] Running final validation...

✅ All tasks completed. All validations passed.
```

---

## Tips for Effective Team Plans

### 1. Identify Natural Parallelism

Tasks that don't depend on each other can run simultaneously:
- Backend and frontend component work
- Different independent components
- Tests and stories for the same component

### 2. Choose the Right Builder

| Task Type | Builder | Reason |
|-----------|---------|--------|
| New feature with tests | `tdd-builder` | Enforces test-first |
| Backend changes | `convex-builder` | Domain expertise |
| Quick fixes | `ts-builder` | Lighter weight |
| Extension work | `extension-builder` | WXT knowledge |
| UI components (Stached) | `shadcn-builder` | ShadCN + Motion |
| UI components (Oculis) | `nuxt-ui-builder` | NuxtUI + Motion-vue |
| UI verification | `ui-validator` | Design compliance |

### 3. Include UI Specs in Task Prompts

For UI tasks, include design requirements in the task description:

```markdown
### 2. Create TagFilterButton Component
- **Task ID**: create-component
- **Assigned To**: shadcn-builder
- **Agent Type**: shadcn-builder

**Design Requirements**:
- Use `motion.div` with `layoutId` for morph animation
- Collapsed: Icon button with badge showing selected count
- Expanded: Dialog with TagPicker inside
- Animation: ~200-300ms duration, material easing
- Focus: `focus-visible:ring-2 focus-visible:ring-ring`

**Accessibility**:
- `aria-expanded` on trigger button
- `aria-label="Filter by tag"` when collapsed
- Focus trap when expanded

**Files to create**:
- TagFilterButton.tsx (component)
- TagFilterButton.stories.tsx (all variants)
- TagFilterButton.test.tsx (behavior tests)
```

### 4. Add UI Validation Task

Always include a UI validation step for frontend work:

```markdown
### N-1. Validate UI Implementation
- **Task ID**: validate-ui
- **Depends On**: create-component
- **Assigned To**: ui-validator
- **Agent Type**: ui-validator
- **Parallel**: false
- Verify component matches design spec
- Check accessibility (WCAG AA)
- Confirm Storybook stories cover all variants
- Flag any issues for builder to fix

### N. Final Validation
- **Depends On**: validate-ui
- Run full test suite
- Verify no lint/type errors
```

### 3. Always End with Validation

```markdown
### N. Final Validation
- **Task ID**: validate-all
- **Depends On**: [all other task IDs]
- **Assigned To**: feature-validator
- **Agent Type**: ts-validator
```

### 4. Reference the Original Spec

In your task descriptions, reference the original OpenSpec:

```markdown
### 2. Create TagFilterButton
- Implement as specified in `docs/plans/2026-01-29-tag-filter-button-design.md#components`
- Follow the animation approach: layoutId on container, AnimatePresence for content
```

---

## Integrating with Existing OpenSpec Workflow

The agent team approach complements your existing OpenSpec commands:

| OpenSpec Command | When to Use | Agent Alternative |
|------------------|-------------|-------------------|
| `/openspec proposal` | Initial requirement gathering | Keep using this |
| `/openspec apply` | Simple, sequential implementation | Use for small changes |
| `/plan` + `/build` | Complex, parallelizable work | Use for multi-component features |

### Hybrid Workflow

1. **Create proposal** with `/openspec proposal`
2. **Refine design** in `changes/<id>/design.md`
3. **Generate team plan** with `/plan changes/<id>/design.md`
4. **Execute with agents** using `/build`
5. **Archive** with `/openspec archive` when done
