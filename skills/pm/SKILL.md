# PM - Proofread Message

Quick polish for professional messages. Fix grammar, spelling, and improve clarity.

## Usage

User invokes: `/pm <text>`

## Process

1. Fix spelling and grammar errors
2. Improve clarity and conciseness
3. Keep technical terms intact
4. Maintain professional tone appropriate for tech lead / senior developer context
5. Preserve the original intent and meaning

## Output Format

Return ONLY the corrected text in a code block:

```
[corrected text here]
```

No explanations. No "here's your corrected text". Just the clean result ready to copy-paste.

## Style Guidelines

- Short and direct (remove filler words)
- Professional but not overly formal
- Technical terms unchanged
- Active voice preferred
- One idea per sentence when possible

## Examples

Input: `/pm i think we need discus about the api endpoint becuase its not working proper on production`

Output:
```
We need to discuss the API endpoint - it's not working properly in production.
```

Input: `/pm can you please review my PR when you have time, i added new feature for cart calculation and also fix some bugs`

Output:
```
Please review my PR when you have time. I added a cart calculation feature and fixed some bugs.
```

Input: `/pm the deploy was success but we have issue with database connection on staging enviroment`

Output:
```
The deploy succeeded, but we have a database connection issue in staging.
```
