# Canvas Template Routing Rules

These rules decide WHICH canvas template to use.
They are system rules, not user preferences.

---

## Sequence Diagrams

If `diagram_type == "sequence"`:

- If the content intent is:
  - documentation
  - explanation
  - sharing
  - usage instructions
  - public-facing notes

  → use `templates/canvas.sequence.compact.md`

- Otherwise:
  → use `templates/canvas.sequence.detailed.md`

---

## Important
- This decision is made by note-creator.
- Do NOT ask the user.
- Do NOT let the model improvise.
- The selected template MUST be applied strictly.
