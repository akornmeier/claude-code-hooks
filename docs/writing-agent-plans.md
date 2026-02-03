# Writing Effective Agent Orchestration Plans

This guide documents the plan format used by orchestrating agents to provide clear direction to builder and validator sub-agents.

## Self-Validating Agent Architecture

The power of this system comes from **self-validating agents** - agents that cannot complete without passing quality gates. There are two layers of validation:

### Plan Validation (Structure)
Ensures plans contain required sections before the planner can finish:
```yaml
hooks:
  Stop:
    - hooks:
        - type: command
          command: validate_new_file.py --directory specs --extension .md
        - type: command
          command: validate_file_contains.py --contains '## Task Description' --contains '## Team Orchestration'
```

### Code Quality Validation (Implementation)
Ensures code meets standards before builders can proceed:
```yaml
hooks:
  PreToolUse:
    - matcher: "Write|Edit"
      hooks:
        - type: command
          command: tdd_enforcer.py  # Must write test first
  PostToolUse:
    - matcher: "Write|Edit"
      hooks:
        - type: command
          command: oxlint_validator.py  # Lint must pass
        - type: command
          command: tsc_validator.py     # Types must check
  Stop:
    - hooks:
        - type: command
          command: coverage_validator.py  # Coverage must meet threshold
```

---

## Core Principle: Plans Are Executable Specifications

A plan is not just documentation—it's an **executable specification** that an orchestrating agent uses to:
1. Create tasks in a shared task list
2. Deploy specialized agents to execute those tasks
3. Track dependencies and progress
4. Validate completion against acceptance criteria

### Why This Matters

> "You want to be teaching your agents how to build like you would."

The difference between **agentic engineering** and **vibe coding** is knowing the outcome your agent will generate. Template meta-prompts create plans in a highly vetted, consistent format - ensuring predictable, high-quality results.

### Communication Through Task List

The task list is the **communication backbone** for agent teams:
- Agents don't run ad-hoc without a common mission
- Task dependencies ensure proper ordering
- Each agent knows when work is/isn't done
- Primary agent orchestrates, never codes directly

```
┌─────────────────────────────────────────────────────────────┐
│  ORCHESTRATION FLOW                                          │
│                                                              │
│  Plan Document (.md)                                         │
│      ↓                                                       │
│  Orchestrating Agent reads plan                              │
│      ↓                                                       │
│  TaskCreate for each step → Shared Task List                 │
│      ↓                                                       │
│  Task tool deploys Builder/Validator agents                  │
│      ↓                                                       │
│  Agents execute, update tasks, report completion             │
│      ↓                                                       │
│  Orchestrator validates against Acceptance Criteria          │
└─────────────────────────────────────────────────────────────┘
```

## Required Plan Sections

Every plan MUST contain these sections (enforced by validation hooks):

| Section | Purpose |
|---------|---------|
| `## Task Description` | What needs to be done |
| `## Objective` | What success looks like |
| `## Relevant Files` | Files to read, modify, or create |
| `## Team Orchestration` | Team composition |
| `### Team Members` | Named agents with roles |
| `## Step by Step Tasks` | Numbered, sequenced tasks |
| `## Acceptance Criteria` | Measurable completion criteria |

### Optional Sections (for complex tasks)

| Section | When to Include |
|---------|-----------------|
| `## Problem Statement` | Feature development, complex tasks |
| `## Solution Approach` | Architectural decisions needed |
| `## Implementation Phases` | Multi-phase projects |
| `## Validation Commands` | Specific commands to verify completion |
| `## Notes` | Dependencies, edge cases, context |

---

## Plan Format Template

```markdown
# Plan: <descriptive-name>

## Task Description
<Describe the task in detail. What problem are we solving? What's the context?>

## Objective
<Clear statement of what will be accomplished when complete>

## Problem Statement
<For features/complex tasks: Define the specific problem or opportunity>

## Solution Approach
<For features/complex tasks: How will we solve it?>

## Relevant Files

### Existing Files (to modify)
- `path/to/file.ts` - Why this file is relevant
- `path/to/another.ts` - What will change here

### New Files (to create)
- `path/to/new-file.ts` - Purpose of this new file

## Implementation Phases

### Phase 1: Foundation
<Setup, scaffolding, dependencies>

### Phase 2: Core Implementation
<Main feature work>

### Phase 3: Integration & Polish
<Testing, documentation, cleanup>

## Team Orchestration

- You operate as the team lead and orchestrate the team to execute the plan.
- IMPORTANT: You NEVER operate directly on the codebase. You use Task tools to deploy team members.
- Take note of the session ID of each team member for resumption.

### Team Members

- Builder
  - Name: <unique-name>
  - Role: <specific focus area>
  - Agent Type: builder
  - Resume: true

- Validator
  - Name: <unique-name>
  - Role: <what they validate>
  - Agent Type: validator
  - Resume: true

## Step by Step Tasks

### 1. <Task Name>
- **Task ID**: <kebab-case-id>
- **Depends On**: none
- **Assigned To**: <team member name>
- **Agent Type**: builder
- **Parallel**: true
- <Specific action item>
- <Specific action item>

### 2. <Task Name>
- **Task ID**: <kebab-case-id>
- **Depends On**: <previous-task-id>
- **Assigned To**: <team member name>
- **Agent Type**: validator
- **Parallel**: false
- <Validation action>

### N. Final Validation
- **Task ID**: validate-all
- **Depends On**: <all previous task IDs>
- **Assigned To**: <validator name>
- **Agent Type**: validator
- **Parallel**: false
- Run all validation commands
- Verify acceptance criteria met

## Acceptance Criteria

1. [ ] <Specific, measurable criterion>
2. [ ] <Another specific criterion>
3. [ ] <Verification that can be checked>

## Validation Commands

- `command here` - What it validates
- `another command` - What it checks

## Notes

- <Dependencies or prerequisites>
- <Edge cases to consider>
- <Important context>
```

---

## Task Specification Format

Each task in the plan follows this structure:

```markdown
### N. <Task Name>
- **Task ID**: <unique-kebab-case-id>
- **Depends On**: <task-ids-or-none>
- **Assigned To**: <team-member-name>
- **Agent Type**: <builder|validator|general-purpose>
- **Parallel**: <true|false>
- <Action item 1>
- <Action item 2>
```

### Field Definitions

| Field | Description | Example |
|-------|-------------|---------|
| **Task ID** | Unique kebab-case identifier | `build-auth-service` |
| **Depends On** | Task IDs that must complete first, or `none` | `setup-database, create-schema` |
| **Assigned To** | Team member name from Team Members section | `auth-builder` |
| **Agent Type** | The subagent type to use | `builder`, `validator`, `tdd-builder` |
| **Parallel** | Can run alongside other tasks? | `true` or `false` |
| **Action items** | Specific, actionable steps | `Create user model with email and password fields` |

### Dependency Patterns

```
Sequential (most common):
Task 1 (none) → Task 2 (depends: 1) → Task 3 (depends: 2)

Parallel then Merge:
Task 1 (none) ──┬─→ Task 3 (depends: 1, 2)
Task 2 (none) ──┘

Fan-out:
Task 1 (none) → Task 2 (depends: 1)
             → Task 3 (depends: 1)
             → Task 4 (depends: 1)

Diamond:
Task 1 (none) → Task 2 (depends: 1) ──┬─→ Task 4 (depends: 2, 3)
             → Task 3 (depends: 1) ──┘
```

---

## Team Member Definitions

### Structure

```markdown
- Builder
  - Name: <unique-identifier>
  - Role: <specific responsibility>
  - Agent Type: <subagent-type>
  - Resume: <true|false>
```

### Best Practices

1. **Unique Names**: Each team member needs a unique name for reference
   - Good: `api-builder`, `auth-validator`, `docs-builder`
   - Bad: `builder`, `validator` (not unique if multiple)

2. **Specific Roles**: Define exactly what each member is responsible for
   - Good: `Implement JWT authentication with refresh token support`
   - Bad: `Handle authentication stuff`

3. **Resume Strategy**:
   - `true`: Agent continues with same context (related follow-up work)
   - `false`: Fresh start (unrelated task, clean slate preferred)

### Common Team Compositions

**Simple Task (1 builder, 1 validator)**
```markdown
### Team Members

- Builder
  - Name: feature-builder
  - Role: Implement the feature according to spec
  - Agent Type: builder
  - Resume: true

- Validator
  - Name: feature-validator
  - Role: Verify implementation meets acceptance criteria
  - Agent Type: validator
  - Resume: true
```

**Complex Task (multiple specialized builders)**
```markdown
### Team Members

- Builder (API)
  - Name: api-builder
  - Role: Implement backend API endpoints
  - Agent Type: builder
  - Resume: true

- Builder (Frontend)
  - Name: ui-builder
  - Role: Implement React components
  - Agent Type: builder
  - Resume: true

- Builder (Tests)
  - Name: test-builder
  - Role: Write integration and unit tests
  - Agent Type: tdd-builder
  - Resume: true

- Validator
  - Name: integration-validator
  - Role: Validate full stack integration
  - Agent Type: validator
  - Resume: true
```

---

## Writing Effective Action Items

### Good Action Items (Specific, Actionable)

```markdown
### 3. Implement User Authentication
- Create `src/services/auth.ts` with login/logout functions
- Add JWT token generation using `jsonwebtoken` library
- Implement token refresh with 7-day expiry
- Add password hashing using bcrypt with 10 rounds
- Create middleware `src/middleware/auth.ts` for route protection
```

### Bad Action Items (Vague, Unclear)

```markdown
### 3. Implement User Authentication
- Handle authentication
- Make it secure
- Add tokens
- Do the middleware stuff
```

### Action Item Checklist

- [ ] Is it specific enough that someone unfamiliar could execute it?
- [ ] Does it mention specific files to create/modify?
- [ ] Are libraries/tools named explicitly?
- [ ] Are configuration values specified (e.g., "10 rounds", "7-day expiry")?
- [ ] Is success measurable?

---

## Acceptance Criteria Best Practices

### Characteristics of Good Criteria

1. **Specific**: Exact conditions, not vague descriptions
2. **Measurable**: Can be verified with a command or check
3. **Atomic**: Each criterion tests one thing
4. **Ordered**: From most fundamental to most integrated

### Examples

**Good Criteria**
```markdown
## Acceptance Criteria

1. [ ] `src/services/auth.ts` exports `login`, `logout`, `refreshToken` functions
2. [ ] JWT tokens expire after 15 minutes (access) and 7 days (refresh)
3. [ ] `pnpm test` passes with 100% of auth tests passing
4. [ ] `pnpm type-check` shows no TypeScript errors
5. [ ] Login with invalid credentials returns 401 status code
6. [ ] Protected routes return 403 without valid token
```

**Bad Criteria**
```markdown
## Acceptance Criteria

1. [ ] Authentication works
2. [ ] Tests pass
3. [ ] No errors
4. [ ] Secure
```

---

## Validation Commands Section

Link acceptance criteria to specific verification commands:

```markdown
## Validation Commands

- `pnpm test --filter=auth` - Run authentication tests
- `pnpm type-check` - Verify no TypeScript errors
- `curl -X POST localhost:3000/auth/login -d '{}' -w '%{http_code}'` - Verify 401 on empty credentials
- `grep -r "bcrypt" src/` - Confirm bcrypt is used for password hashing
- `cat src/services/auth.ts | grep "expiresIn"` - Verify token expiry is configured
```

---

## Common Anti-Patterns

### 1. Overly Large Tasks
**Problem**: Single task tries to do too much
```markdown
### 1. Build Entire Authentication System
- Create users table, API, frontend, tests, docs
```

**Solution**: Break into smaller, focused tasks
```markdown
### 1. Create Users Database Schema
### 2. Implement Auth API Endpoints
### 3. Build Login UI Component
### 4. Write Auth Integration Tests
### 5. Add Auth Documentation
```

### 2. Missing Dependencies
**Problem**: Tasks that should be sequential are marked parallel
```markdown
### 2. Write Tests
- **Depends On**: none  # WRONG - needs implementation first
```

**Solution**: Explicit dependency chain
```markdown
### 2. Write Tests
- **Depends On**: implement-feature
```

### 3. Vague Team Roles
**Problem**: Multiple builders with overlapping responsibilities
```markdown
- Builder
  - Name: builder-1
  - Role: Build stuff
```

**Solution**: Specific, non-overlapping responsibilities
```markdown
- Builder
  - Name: api-builder
  - Role: Implement REST API endpoints in /api directory
```

### 4. No Final Validation
**Problem**: Plan ends with build tasks, no verification
```markdown
### 5. Implement Final Feature
- Build the last thing
```

**Solution**: Always end with validation
```markdown
### 6. Final Validation
- **Assigned To**: validator
- Run all acceptance criteria checks
- Verify integration between components
```

---

## Example: Complete Plan

```markdown
# Plan: Add User Preferences API

## Task Description
Add a user preferences API that allows users to store and retrieve their application settings. Preferences should be stored per-user and support arbitrary JSON values.

## Objective
Users can save, retrieve, and update their preferences through a REST API with proper validation and persistence.

## Relevant Files

### Existing Files
- `src/database/schema.ts` - Add preferences table
- `src/routes/index.ts` - Register new routes

### New Files
- `src/routes/preferences.ts` - Preferences API endpoints
- `src/services/preferences.ts` - Preferences business logic
- `src/tests/preferences.test.ts` - API tests

## Team Orchestration

- You operate as the team lead and orchestrate the team to execute the plan.
- IMPORTANT: You NEVER operate directly on the codebase.

### Team Members

- Builder (Backend)
  - Name: preferences-builder
  - Role: Implement preferences API and database schema
  - Agent Type: builder
  - Resume: true

- Validator
  - Name: preferences-validator
  - Role: Verify API works correctly with all edge cases
  - Agent Type: validator
  - Resume: true

## Step by Step Tasks

### 1. Add Preferences Database Schema
- **Task ID**: add-schema
- **Depends On**: none
- **Assigned To**: preferences-builder
- **Agent Type**: builder
- **Parallel**: false
- Add `preferences` table to `src/database/schema.ts`
- Columns: `id`, `userId`, `key`, `value` (JSON), `createdAt`, `updatedAt`
- Add unique constraint on (userId, key)
- Run migration

### 2. Implement Preferences Service
- **Task ID**: implement-service
- **Depends On**: add-schema
- **Assigned To**: preferences-builder
- **Agent Type**: builder
- **Parallel**: false
- Create `src/services/preferences.ts`
- Implement `get(userId, key)`, `set(userId, key, value)`, `delete(userId, key)`, `list(userId)`
- Add input validation for key names (alphanumeric, max 100 chars)
- Handle JSON serialization/deserialization

### 3. Implement Preferences API Routes
- **Task ID**: implement-routes
- **Depends On**: implement-service
- **Assigned To**: preferences-builder
- **Agent Type**: builder
- **Parallel**: false
- Create `src/routes/preferences.ts`
- `GET /preferences` - List all preferences for authenticated user
- `GET /preferences/:key` - Get single preference
- `PUT /preferences/:key` - Set preference value
- `DELETE /preferences/:key` - Delete preference
- Register routes in `src/routes/index.ts`

### 4. Validate Implementation
- **Task ID**: validate-implementation
- **Depends On**: implement-routes
- **Assigned To**: preferences-validator
- **Agent Type**: validator
- **Parallel**: false
- Verify all files exist and compile
- Run `pnpm type-check`
- Test API endpoints manually with curl

### 5. Write Integration Tests
- **Task ID**: write-tests
- **Depends On**: validate-implementation
- **Assigned To**: preferences-builder
- **Agent Type**: builder
- **Parallel**: false
- Create `src/tests/preferences.test.ts`
- Test CRUD operations
- Test validation errors (invalid key, missing auth)
- Test concurrent updates

### 6. Final Validation
- **Task ID**: validate-all
- **Depends On**: write-tests
- **Assigned To**: preferences-validator
- **Agent Type**: validator
- **Parallel**: false
- Run `pnpm test`
- Verify all acceptance criteria
- Check for TypeScript errors

## Acceptance Criteria

1. [ ] `preferences` table exists with correct schema
2. [ ] All CRUD endpoints return correct HTTP status codes
3. [ ] Invalid key names return 400 Bad Request
4. [ ] Unauthenticated requests return 401
5. [ ] `pnpm test` passes with all preferences tests green
6. [ ] `pnpm type-check` shows no errors

## Validation Commands

- `pnpm type-check` - Verify TypeScript compilation
- `pnpm test --filter=preferences` - Run preferences tests
- `curl -X GET localhost:3000/preferences` - Should return 401 without auth
- `grep "preferences" src/database/schema.ts` - Verify schema added

## Notes

- Use existing auth middleware from `src/middleware/auth.ts`
- Preference values are stored as JSON, max 10KB per value
- Consider adding rate limiting in future iteration
```

---

## Summary

Effective agent orchestration plans:

1. **Are executable** - Contain enough detail for agents to work autonomously
2. **Have clear structure** - Follow the required sections format
3. **Define specific tasks** - Each task is atomic, actionable, measurable
4. **Manage dependencies** - Explicit task ordering prevents race conditions
5. **Assign accountability** - Named team members own specific work
6. **Validate completion** - End with verification against acceptance criteria
