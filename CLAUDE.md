# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Claude Skills repository for building, managing, and distributing reusable skills for Claude Desktop, Claude.ai Web, and Claude Code CLI. Skills are self-contained markdown-based instruction sets that extend Claude's capabilities.

## Build Commands

```bash
./build.sh              # Build all skills into ZIP files in dist/
./build.sh <skill-name> # Build a specific skill (e.g., ./build.sh pm)
```

The build script validates that each skill has a `SKILL.md` file with proper YAML frontmatter before packaging.

## Creating a New Skill

1. Create a directory under `skills/` with your skill name
2. Add a `SKILL.md` file with required YAML frontmatter:

```yaml
---
name: skill-name
description: Brief description of what this skill does and when to use it.
---
```

3. Write instructions in markdown below the frontmatter
4. Test with `./build.sh skill-name`

Reference `_templates/skill-template/SKILL.md` for the template structure and `_templates/CREATING-SKILLS.md` for best practices.

## SKILL.md Format

Required frontmatter fields: `name`, `description`

Optional frontmatter fields:
- `disable-model-invocation: true` - Only user can invoke (not Claude)
- `user-invocable: false` - Only Claude can invoke (not user)
- `allowed-tools: [Read, Grep]` - Restrict which tools are available

## Repository Structure

- `skills/` - Source directory for all skills (each skill in its own subdirectory)
- `_templates/` - Templates and guides for creating new skills
- `dist/` - Built ZIP packages (gitignored)
- `.claude-plugin/marketplace.json` - Plugin registry for marketplace distribution
- `.github/workflows/` - CI validation and release automation

## Validation

GitHub Actions automatically validate on push/PR to `skills/**`:
- SKILL.md must exist in each skill directory
- YAML frontmatter must be properly delimited with `---`
- `name` and `description` fields are required

## Commit Convention

Use format: `[Action]: skill-name`
- `Add: skill-name` - New skill
- `Fix: skill-name` - Bug fix
- `Update: skill-name` - Enhancement
