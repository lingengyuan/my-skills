---
name: insight-collector
description: >
  Analyze any input material (URLs, code snippets, images, text, documents, screenshots)
  and extract technical insights, reusable code, and project ideas into the CodeSnippets
  knowledge base at /root/projects/CodeSnippets. Use this skill when the user drops a link,
  pastes code, shares a screenshot, sends a document, or provides raw text and wants it
  analyzed and archived as inspiration. Triggers: "收录", "分析这个", "记录一下",
  "add this to snippets", "collect", "/insight", or when user provides material
  (link/code/image/doc) with intent to archive into the project.
---

# Insight Collector

Analyze input material and extract technical insights into the CodeSnippets project.

## Workflow

1. **Identify input type** and acquire content:

   | Input | Action |
   |-------|--------|
   | URL | Fetch with WebFetch, extract full technical content |
   | Code snippet (pasted) | Analyze directly |
   | Image / screenshot | Read the image file, extract visible code or concepts |
   | Document (.pdf, .md, .txt) | Read the file |
   | Raw text | Analyze directly |

2. **Analyze** — extract these from the material:

   - **Reusable code snippets**: working code worth saving (identify language)
   - **Technical patterns**: architectural ideas, API usage, design patterns
   - **Tools & libraries**: notable dependencies worth knowing about
   - **Ideas & directions**: what could be built with this, non-obvious use cases

3. **Classify and write** — route each extracted item to the right location. Read `references/project-conventions.md` for directory map, header templates, and naming conventions. Write outputs:

   - Code snippets → `{language}/` directory with standard header comment
   - Ideas and inspiration → `ideas/{topic}.md` using idea template
   - Cross-cutting analysis → `analysis/{topic}.md`
   - Combined HTML tools → `html-tools/`

   File naming: lowercase, hyphens, descriptive. E.g. `zvec-inprocess-vector.py`, `agentic-hoarding-patterns.md`.

4. **Update README.md** — add new entries to both English and Chinese catalog tables. Update the project structure tree only if a new directory was created.

5. **Report** — summarize to the user:
   - What files were created
   - Key insights extracted
   - Suggested next steps or related existing snippets in the project

## Guidelines

- Prefer Chinese for idea docs and comments (matching project convention), English for code
- One insight source may produce multiple output files (e.g. a blog post yields 2 code snippets + 1 idea doc)
- Always include `来源` (source URL) in headers when input was a URL
- Do NOT fabricate code that wasn't in the source — only extract what's actually there
- For large sources, focus on the most novel and reusable parts
- Cross-reference existing files in the project when relevant (e.g. "relates to python/tape_context.py")
- When the input is an image/screenshot, describe what you see and extract any visible code or architecture diagrams
