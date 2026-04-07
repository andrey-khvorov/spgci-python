# SPGCI Agent Skills

This repo hosts "Agent Skills" documentation as plain Markdown files so they can be published as public artifacts later.

## Where skills live

- Each skill lives in its own top-level folder (example: `market_commentary/skills.md`).
- The registry lives at `skills/registry.json` and is the source of truth for which skills exist.

## Add a new skill

1) Create a new folder at the repo root (example: `my_skill/`).
2) Add your Markdown doc at `my_skill/skills.md`.
3) Add an entry to `skills/registry.json` under `skills[]`:

Required fields:
- `name`: stable identifier (must be unique)
- `title`: human-friendly title
- `description`: short description
- `path`: repo-relative path to the `skills.md` file (use forward slashes)
- `version`: semver (string)

4) Run the validator:

```bash
python tools/validate_skills.py
```

## Raw GitHub URLs

GitHub can serve the raw Markdown file contents via `raw.githubusercontent.com`:

```
https://raw.githubusercontent.com/<OWNER>/<REPO>/<BRANCH>/<PATH>
```

Example (default branch):

```
https://raw.githubusercontent.com/<OWNER>/<REPO>/main/market_commentary/skills.md
```
