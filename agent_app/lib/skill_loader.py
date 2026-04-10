from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class SkillEntry:
    name: str
    title: str
    description: str
    path: str
    version: str


def repo_root() -> Path:
    # agent_app/lib/skill_loader.py -> agent_app/lib -> agent_app -> repo root
    return Path(__file__).resolve().parents[2]


def load_registry() -> list[SkillEntry]:
    root = repo_root()
    registry_path = root / "skills" / "registry.json"
    data = json.loads(registry_path.read_text(encoding="utf-8"))

    skills_raw: Any
    if isinstance(data, dict) and isinstance(data.get("skills"), list):
        skills_raw = data["skills"]
    elif isinstance(data, list):
        skills_raw = data
    else:
        raise ValueError("Invalid registry schema; expected list or {'skills': [...]} ")

    entries: list[SkillEntry] = []
    for entry in skills_raw:
        entries.append(
            SkillEntry(
                name=str(entry["name"]),
                title=str(entry.get("title", "")),
                description=str(entry.get("description", "")),
                path=str(entry["path"]),
                version=str(entry.get("version", "")),
            )
        )
    return entries


def load_skill_markdown(name: str) -> str:
    name = name.strip()
    if not name:
        raise ValueError("skill name is required")

    entries = load_registry()
    match = next((e for e in entries if e.name == name), None)
    if match is None:
        known = ", ".join(sorted(e.name for e in entries))
        raise KeyError(f"Unknown skill: {name}. Known: {known}")

    root = repo_root()
    skill_path = root / Path(match.path)
    return skill_path.read_text(encoding="utf-8")
