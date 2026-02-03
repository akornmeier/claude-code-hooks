# Claude Code Hooks

Project-specific instructions for Claude Code.

## Overview

This repository demonstrates Claude Code hooks and self-validating agents. See [AGENTS.md](AGENTS.md) for agent documentation.

## Development

### Linting

```bash
# Python linting with Ruff
uv run ruff check .

# Python type checking with ty
uv run ty check
```

### Testing Hooks

```bash
# Validate Python syntax
python3 -m py_compile ~/.claude/hooks/validators/*.py

# Test TDD enforcer
echo '{"tool_input": {"file_path": "src/foo.ts"}}' | python3 ~/.claude/hooks/validators/tdd_enforcer.py
```

## Key Files

- `AGENTS.md` - Agent documentation and architecture
- `docs/writing-agent-plans.md` - Guide to writing orchestration plans
- `~/.claude/hooks/validators/` - Hook validator scripts
- `~/.claude/agents/` - Shared agent definitions
