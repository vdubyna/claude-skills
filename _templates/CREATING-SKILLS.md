# Creating Effective Skills

A guide to writing skills that Claude can use effectively.

## Skill Structure

Every skill needs at minimum a `SKILL.md` file in its folder:

```
skills/
└── my-skill/
    ├── SKILL.md        # Required: Main instructions
    ├── templates/      # Optional: File templates
    ├── examples/       # Optional: Example files
    └── scripts/        # Optional: Helper scripts
```

## Writing Good Instructions

### 1. Be Specific About Triggers

Bad:
> "Use this skill for documents"

Good:
> "Use this skill when the user wants to create meeting notes, specifically when they mention 'meeting', 'notes', 'minutes', or 'agenda'"

### 2. Provide Step-by-Step Workflows

Structure your instructions as numbered steps:

```markdown
## Instructions

1. **Gather Information**
   - Ask the user for X if not provided
   - Check for Y in the workspace

2. **Process**
   - Do A
   - Then do B

3. **Output**
   - Save to workspace as filename.ext
   - Provide summary to user
```

### 3. Include Examples

Show Claude what success looks like:

```markdown
## Examples

### Creating a Bug Report

**Input:** "Create a bug report for the login issue"

**Output:** Creates `bug-report-login-YYYYMMDD.md` with:
- Title
- Steps to reproduce
- Expected vs actual behavior
- Environment details
```

### 4. Handle Edge Cases

Document what to do when things go wrong:

```markdown
## Notes

- If no date is provided, use today's date
- If file already exists, append a number (e.g., report-2.md)
- If required field is missing, ask user before proceeding
```

## Testing Your Skill

1. Start a new Cowork session
2. Select the folder containing your skill
3. Try various prompts that should trigger the skill
4. Verify the output matches expectations
5. Test edge cases

## Tips for Better Skills

- **Keep it focused**: One skill = one capability
- **Use clear language**: Avoid ambiguity
- **Provide defaults**: Don't require user input for everything
- **Think about files**: Specify exact filenames and paths
- **Consider iterations**: User might want to refine the output

## Debugging

If your skill isn't working:

1. Check `SKILL.md` exists in the skill folder
2. Verify the folder is in the workspace selected by Cowork
3. Review trigger conditions - are they specific enough?
4. Test with explicit invocation: "Use the X skill to..."
