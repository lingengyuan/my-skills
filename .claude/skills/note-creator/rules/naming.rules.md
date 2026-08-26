# Naming Rules

## Title Sanitization
- Remove illegal characters: / \ : * ? " < > |
- Trim whitespace
- Keep Chinese characters

## Output Paths
outputs/<folder>/<title>/

## Collision Policy
If the directory already exists:
- Inspect its existing artifacts first.
- Preserve existing files by default.
- Overwrite only files the user explicitly asks to replace.
- Use a new title or path when creating a separate note package.
