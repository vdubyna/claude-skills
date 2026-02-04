# My Claude Skills Repository

A personal collection of reusable Claude skills for extending AI capabilities.

## Structure

```
├── skills/               # Your custom skills (source)
│   └── skill-name/
│       ├── SKILL.md      # Skill instructions (required)
│       └── ...           # Supporting files
├── dist/                 # Packaged skills (ZIP files)
├── _templates/           # Templates for creating new skills
├── .claude-plugin/       # Plugin marketplace config
└── build.sh              # Script to package skills
```

## Installation Methods

### Method 1: Claude Desktop / Claude.ai Web (ZIP)

1. Build the packaged skill:
   ```bash
   ./build.sh pm  # specific skill
   ./build.sh     # all skills
   ```

2. Upload `dist/pm.zip` via:
   - **Claude Desktop**: Settings → Capabilities → Skills → Upload
   - **Claude.ai Web**: Settings → Capabilities → Skills → Upload

### Method 2: Claude Code CLI (Marketplace)

Add this repository as a marketplace:
```bash
/plugin marketplace add https://github.com/vdubyna/claude-skills
/plugin install pm
```

### Method 3: Symlink (Development)

For local development with auto-updates:
```bash
ln -s /path/to/claude-skills/skills/* ~/.claude/skills/
```

## Creating a New Skill

1. Copy the template:
   ```bash
   cp -r _templates/skill-template skills/your-skill-name
   ```

2. Edit `skills/your-skill-name/SKILL.md`:
   - Update YAML frontmatter (`name`, `description`)
   - Add instructions and examples

3. Build and test:
   ```bash
   ./build.sh your-skill-name
   ```

4. Add to marketplace (`.claude-plugin/marketplace.json`)

5. Commit and push:
   ```bash
   git add skills/your-skill-name .claude-plugin/marketplace.json
   git commit -m "Add: your-skill-name skill"
   git push
   ```

## SKILL.md Format

Every skill must have YAML frontmatter:

```markdown
---
name: skill-name
description: Brief description of what this skill does and when to use it.
---

# Skill Title

Instructions here...
```

### Optional Frontmatter Fields

```yaml
---
name: skill-name
description: What it does
disable-model-invocation: false  # Only user can invoke
user-invocable: false            # Only Claude can invoke
allowed-tools: [Read, Grep]      # Restrict available tools
---
```

## Available Skills

| Skill | Description | Install |
|-------|-------------|---------|
| `pm` | Proofread messages for professional communication | `/plugin install pm` |

## Version Control Tips

- Use meaningful commit messages: `Add: skill-name`, `Fix: skill-name`, `Update: skill-name`
- Tag stable versions: `git tag v1.0.0`
- Create branches for experimental skills

## Links

- [Claude Skills Documentation](https://support.claude.com/en/articles/12512180-using-skills-in-claude)
- [Creating Custom Skills](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills)
- [Skill Creator Guide](_templates/CREATING-SKILLS.md)
