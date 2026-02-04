# My Claude Skills Repository

A personal collection of reusable Claude skills for extending AI capabilities.

## Structure

```
├── skills/           # Your custom skills
│   └── skill-name/
│       ├── SKILL.md  # Skill instructions (required)
│       └── ...       # Supporting files
├── _templates/       # Templates for creating new skills
└── README.md
```

## Quick Start

### Creating a New Skill

1. Copy the template:
   ```bash
   cp -r _templates/skill-template skills/your-skill-name
   ```

2. Edit `skills/your-skill-name/SKILL.md` with your skill's instructions

3. Commit your changes:
   ```bash
   git add skills/your-skill-name
   git commit -m "Add: your-skill-name skill"
   ```

### Using Skills in Claude

To use these skills in Cowork mode:
1. Select this folder as your workspace
2. Skills will be auto-discovered from the `skills/` directory
3. Invoke skills by name or let Claude detect when to use them

## Skill Guidelines

Each skill should have:
- **Clear trigger conditions** - when should Claude use this skill?
- **Step-by-step instructions** - what should Claude do?
- **Examples** (optional) - show expected behavior
- **Supporting files** (optional) - templates, scripts, etc.

## Version Control Tips

- Use meaningful commit messages: `Add: skill-name`, `Fix: skill-name`, `Update: skill-name`
- Tag stable versions: `git tag v1.0.0`
- Create branches for experimental skills

## Links

- [Claude Skills Documentation](https://docs.anthropic.com)
- [Skill Creator Guide](_templates/CREATING-SKILLS.md)
