# OpenAI plugin submission

This directory contains the prepared materials for submitting Parallel as a
combined remote MCP and skills plugin through the OpenAI plugin submission
portal.

## Submission shape

- Submission type: **With MCP**
- MCP URL type: **Universal**
- Production MCP URL: `https://search.parallel.ai/mcp`
- Authentication: none for the initial anonymous, rate-limited service
- Uploaded skill package: `parallel/`
- Custom UI: none

The portal owns the MCP connection for a public submission. The uploaded
package therefore contains the OpenAI-facing skill and listing metadata but
does not include or depend on the Claude plugin's `.mcp.json`.

## Prepared materials

- `parallel/` — uploadable plugin and skill bundle
- `review/listing.md` — proposed listing copy and starter prompts
- `review/test-cases.md` — exactly five positive and three negative cases
- `review/tool-annotations.md` — required annotation values and justifications
- `review/demo-script.md` — a short recording plan covering the main workflows
- `review/release-notes.md` — initial release notes
- `review/data-practices.md` — draft disclosure for privacy review
- `review/input-checklist.md` — decisions and assets still needed from Parallel
- `scripts/build_submission.py` — deterministic ZIP builder
- `scripts/check_mcp.py` — live production MCP metadata check

## Portal flow

1. Confirm the owning OpenAI organization has Apps Management write access and
   completed identity verification.
2. Create a plugin at <https://platform.openai.com/plugins> and select
   **With MCP**.
3. Enter the production Universal MCP URL and complete domain verification.
4. Select **Scan Tools**, then confirm both tools and their annotations.
5. Upload the package created by `scripts/build_submission.py` in the Skills
   section.
6. Add the listing, starter prompts, release notes, and review test cases from
   `review/`.
7. Add the approved logo, support URL, demo-recording URL, country availability,
   and policy attestations.
8. Run every review test in a clean ChatGPT and Codex environment before
   submitting.

## Build and validate

From the repository root:

```bash
python3 submission/openai/scripts/build_submission.py --output /tmp/parallel-openai-plugin.zip
python3 submission/openai/scripts/check_mcp.py
python3 /path/to/plugin-creator/scripts/validate_plugin.py submission/openai/parallel
python3 /path/to/skill-creator/scripts/quick_validate.py submission/openai/parallel/skills/parallel-web-research
```

The generated ZIP contains one top-level `parallel/` directory so the package
can be inspected or extracted without mixing its contents into another folder.

## Official references

- <https://developers.openai.com/plugins/deploy/submission>
- <https://developers.openai.com/plugins/deploy/submission-errors>
- <https://developers.openai.com/plugins/build/skills>
- <https://developers.openai.com/plugins/guides/submit-claude-plugin>
