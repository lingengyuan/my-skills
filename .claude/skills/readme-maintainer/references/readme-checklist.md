# README Checklist

Use for full rewrites; select content by reader need rather than treating this as a required section list.

## Content

- A short project definition and purpose.
- Runtime prerequisites and the primary installation path.
- A runnable usage example with the configuration it requires.
- Common operations and constraints that affect correct use, data, or recovery.
- Development commands and license where relevant.
- Verified links for detailed configuration, command reference, and architecture; destinations cover the topics delegated to them.

## Evidence

- Commands and options match current source or maintained scripts.
- Paths and links resolve; versions and tool names match authoritative files.
- Source-verified commands are not presented as successfully executed.
- Compatibility, metrics, and deployment claims have evidence.

## Publication quality

- The README stands alone without conversation, review, or editing history.
- Each paragraph adds useful information; repeated facts and empty sections are removed.
- Responsibilities and rules are stated directly; real constraints retain their meaning.
- Details are linked rather than duplicated, while the quick start remains usable.
- Brevity preserves prerequisites, contracts, safety conditions, and recovery limits.

## Language

- Preserve the existing language unless the user requests a change.
- For existing or requested bilingual content, keep both versions aligned in meaning and scope, then run `scripts/check_bilingual_readme.sh README.md`.
