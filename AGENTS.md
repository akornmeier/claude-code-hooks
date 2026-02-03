# Claude Code Agents

This repository contains self-validating agents and orchestration patterns for Claude Code.

## Quick Links

- [Writing Agent Plans](docs/writing-agent-plans.md) - How to write effective orchestration plans
- [Hook Validators](#hook-validators) - Quality gate implementations
- [Shared Agents](#shared-agents) - User-level agents in `~/.claude/agents/`
- [Project Agents](#project-agents) - Project-specific agents

---

## Architecture

```
~/.claude/                     # User-level (shared across projects)
├── agents/                    # Agent definitions
│   ├── tdd-builder.md         # TDD-enforced builder with all gates
│   ├── ts-builder.md          # Standard builder with lint/type gates
│   ├── ts-validator.md        # Read-only verification agent
│   ├── turborepo-runner.md    # Monorepo orchestration
│   └── coverage-checker.md    # Coverage validation
├── hooks/
│   └── validators/
│       ├── tdd_enforcer.py        # PreToolUse: blocks impl without test
│       ├── session_start_tdd.py   # SessionStart: resets TDD state
│       ├── oxlint_validator.py    # PostToolUse: lint validation
│       ├── tsc_validator.py       # PostToolUse: type validation
│       └── coverage_validator.py  # Stop: coverage threshold gate
└── data/
    └── tdd_session_state.json     # TDD session tracking

~/code/stached/.claude/agents/     # Stached-specific
├── convex-builder.md              # Convex backend specialist
├── article-parser.md              # Content extraction
└── extension-builder.md           # WXT browser extension

~/code/oculis/.claude/agents/      # Oculis-specific
├── axe-specialist.md              # Accessibility testing
├── adapter-guide.md               # DI/Adapter patterns
└── tdd-builder.md                 # Oculis TDD builder
```

---

## Self-Validating Agent Pattern

The core innovation is **self-validating agents** - agents that cannot complete work without passing quality gates:

```
┌─────────────────────────────────────────────────────────────┐
│  SELF-VALIDATING AGENT                                       │
│                                                              │
│  Agent Definition (.md file)                                 │
│  ├── System Prompt: What the agent does                      │
│  ├── PreToolUse Hooks: Gates BEFORE action                   │
│  │   └── TDD enforcer: Can't write impl without test         │
│  ├── PostToolUse Hooks: Validates AFTER action               │
│  │   └── Lint/Type validators: Can't proceed with errors     │
│  └── Stop Hooks: Final gate BEFORE completion                │
│      └── Coverage validator: Can't stop without 80%          │
│                                                              │
│  Result: Agent keeps working until ALL gates pass            │
└─────────────────────────────────────────────────────────────┘
```

### Two Layers of Validation

| Layer | Purpose | Validators |
|-------|---------|------------|
| **Plan Validation** | Ensure plans have required structure | `validate_new_file.py`, `validate_file_contains.py` |
| **Code Quality** | Ensure code meets engineering standards | `tdd_enforcer.py`, `oxlint_validator.py`, `tsc_validator.py`, `coverage_validator.py` |

**Plan validators** ensure the orchestrating agent creates well-formed plans with required sections.
**Code quality validators** ensure builder agents produce production-ready code.

### Why This Matters

> "You want to be teaching your agents how to build like you would."

The difference between **agentic engineering** and **vibe coding** is knowing the outcome your agent will generate. Self-validating agents with templated plans create predictable, high-quality results.

---

## Hook Validators

### TDD Enforcer (`tdd_enforcer.py`)
**Event**: PreToolUse (Write|Edit|MultiEdit)

Blocks implementation file writes until corresponding test file has been modified in the session.

```python
# Patterns matched as test files:
src/foo.ts        → src/foo.test.ts, src/foo.spec.ts
src/bar/Baz.tsx   → src/bar/Baz.test.tsx, src/bar/__tests__/Baz.test.tsx
```

### Session Start TDD (`session_start_tdd.py`)
**Event**: SessionStart

Clears TDD session state, ensuring each session starts fresh.

### OXLint Validator (`oxlint_validator.py`)
**Event**: PostToolUse (Write|Edit)

Runs `pnpm exec oxlint` on TS/JS files. Blocks if lint errors found.

### TSC Validator (`tsc_validator.py`)
**Event**: PostToolUse (Write|Edit)

Runs `npx tsc --noEmit` on TypeScript files. Blocks if type errors found.

### Coverage Validator (`coverage_validator.py`)
**Event**: Stop

Runs `pnpm test:coverage` and blocks if coverage < 80%.

---

## Shared Agents

### `tdd-builder`
**Model**: opus | **Color**: cyan

The flagship self-validating agent with all gates:
- PreToolUse: TDD enforcement
- PostToolUse: Lint + Type validation
- Stop: Coverage threshold

Use for disciplined TDD workflow.

### `ts-builder`
**Model**: opus | **Color**: blue

Standard builder with quality validation:
- PostToolUse: Lint + Type validation

Use for general implementation without strict TDD.

### `ts-validator`
**Model**: sonnet | **Color**: yellow

Read-only verification agent:
- Disallowed: Write, Edit, MultiEdit, NotebookEdit

Use after builder to verify work meets standards.

### `turborepo-runner`
**Model**: sonnet | **Color**: green

Monorepo orchestration specialist:
- Tools: Bash, Read, Glob

Use for running commands across monorepo packages.

### `coverage-checker`
**Model**: haiku | **Color**: purple

Lightweight coverage validation:
- Disallowed: Write, Edit

Use to check coverage after tests pass.

---

## Project Agents

### Stached

| Agent | Purpose |
|-------|---------|
| `convex-builder` | Convex backend with type-check gate |
| `article-parser` | Mozilla Readability, HTML sanitization |
| `extension-builder` | WXT framework, Manifest V3 |

### Oculis

| Agent | Purpose |
|-------|---------|
| `axe-specialist` | WCAG compliance, axe-core |
| `adapter-guide` | DI/Adapter architecture (read-only) |
| `tdd-builder` | TDD with Turborepo validation |

---

## Usage

### Invoking Agents via Task Tool

```typescript
Task({
  description: "Implement feature with TDD",
  prompt: "Create user authentication with tests first",
  subagent_type: "tdd-builder",
  model: "opus"
})
```

### Orchestrating Multiple Agents

See [Writing Agent Plans](docs/writing-agent-plans.md) for the complete orchestration format.

```markdown
## Team Members

- Builder
  - Name: auth-builder
  - Role: Implement authentication
  - Agent Type: tdd-builder
  - Resume: true

- Validator
  - Name: auth-validator
  - Role: Verify auth implementation
  - Agent Type: ts-validator
  - Resume: true
```

---

## Creating New Agents

### Agent Definition Format

```yaml
---
name: my-agent
description: Action-oriented description for auto-delegation
model: opus | sonnet | haiku
color: red | blue | green | yellow | purple | orange | pink | cyan
tools: Tool1, Tool2        # Optional: restrict tools
disallowedTools: Write     # Optional: deny tools
hooks:
  PreToolUse:
    - matcher: "Write|Edit"
      hooks:
        - type: command
          command: uv run ~/.claude/hooks/validators/my_validator.py
  PostToolUse:
    - matcher: "Write"
      hooks:
        - type: command
          command: pnpm lint
  Stop:
    - hooks:
        - type: command
          command: pnpm test
---

# Agent Name

## Purpose
What this agent does and when to use it.

## Instructions
How the agent should operate.

## Report
Output format when task completes.
```

### Hook Output Format

Hooks must output JSON:

```json
// Allow the action
{"decision": "allow"}

// Block the action
{"decision": "block", "reason": "Explanation of why blocked"}
```

---

## Testing

### Verify TDD Enforcer

```bash
# Should block (no test exists)
echo '{"tool_input": {"file_path": "src/foo.ts"}}' | python3 ~/.claude/hooks/validators/tdd_enforcer.py

# Should allow (it's a test file)
echo '{"tool_input": {"file_path": "src/foo.test.ts"}}' | python3 ~/.claude/hooks/validators/tdd_enforcer.py

# Should allow (test was recorded)
echo '{"tool_input": {"file_path": "src/foo.ts"}}' | python3 ~/.claude/hooks/validators/tdd_enforcer.py
```

### Reset TDD State

```bash
python3 ~/.claude/hooks/validators/session_start_tdd.py
```

### Validate Python Syntax

```bash
python3 -m py_compile ~/.claude/hooks/validators/*.py
```
