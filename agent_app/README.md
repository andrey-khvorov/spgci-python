# agent_app — Minimal ClaudeCode Emulator

This folder contains a tiny "agent runtime" you can run locally to validate the full flow:

1) Load skill docs from the repo (`skills/registry.json` → `*/skills.md`)
2) Follow the skill steps by calling the library executors (`spgci.market_commentary.*`)
3) Receive tabular output as a `pandas.DataFrame`

## Why this exists

`spgci` is a **library**, not an agent runtime. ClaudeCode (or any tool-calling LLM runtime) is the runtime.
This app simulates that runtime without requiring an LLM.

## Quick start (calling a real server)

From repo root:

```powershell
poetry install

# Use your local server
poetry run python agent_app/run_marketcommentary.py --base-url http://localhost:4000 --from-date 2026-01-01 --to-date 2026-03-07

# If your server requires auth, set a token (recommended over passing it on CLI)
$env:SPGCI_TOKEN = "<YOUR_TOKEN>"
poetry run python agent_app/run_marketcommentary.py --base-url http://localhost:4000 --from-date 2026-01-01 --to-date 2026-03-07
```

## Quick start (using the stub server)

If you don't have a working backend locally (or your auth setup is still in progress), run the stub server:

```powershell
poetry run python agent_app/stub_server.py --port 4010
$env:SPGCI_TOKEN = "dev-token"
poetry run python agent_app/run_marketcommentary.py --base-url http://localhost:4010 --from-date 2026-01-01 --to-date 2026-03-07
```

The stub implements:
- `POST /api/unstructured/marketcommentary`

## Files

- `agent_app/lib/skill_loader.py`: loads skill Markdown from the repo
- `agent_app/run_marketcommentary.py`: loads the skill doc + calls the executors
- `agent_app/stub_server.py`: tiny local stub to emulate the required endpoint
