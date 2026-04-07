from __future__ import annotations

import json
import sys
from pathlib import Path


PLACEHOLDER = "PASTE CONTENT HERE"


def _fail(errors: list[str]) -> int:
    for err in errors:
        print(f"ERROR: {err}")
    return 1


def _load_registry(registry_path: Path) -> tuple[list[dict], list[str]]:
    errors: list[str] = []

    if not registry_path.exists():
        return [], [f"Missing registry file: {registry_path.as_posix()}"]

    try:
        raw = registry_path.read_text(encoding="utf-8")
    except OSError as exc:
        return [], [f"Failed to read registry file: {registry_path.as_posix()} ({exc})"]

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        return [], [
            "Invalid JSON in skills/registry.json: "
            f"{exc.msg} (line {exc.lineno}, col {exc.colno})"
        ]

    if isinstance(data, list):
        skills = data
    elif isinstance(data, dict) and isinstance(data.get("skills"), list):
        skills = data["skills"]
    else:
        return [], [
            "Registry JSON must be either a list of skills or an object with a 'skills' array."
        ]

    normalized: list[dict] = []
    for idx, entry in enumerate(skills):
        if not isinstance(entry, dict):
            errors.append(f"Registry entry #{idx} is not an object")
            continue
        normalized.append(entry)

    return normalized, errors


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    registry_path = repo_root / "skills" / "registry.json"

    skills, errors = _load_registry(registry_path)

    seen_names: set[str] = set()
    for idx, skill in enumerate(skills):
        name = skill.get("name")
        path_str = skill.get("path")

        if not isinstance(name, str) or not name.strip():
            errors.append(f"Registry entry #{idx} missing valid 'name'")
            continue
        if name in seen_names:
            errors.append(f"Duplicate skill name in registry: {name}")
        seen_names.add(name)

        if not isinstance(path_str, str) or not path_str.strip():
            errors.append(f"Skill '{name}' missing valid 'path'")
            continue

        if "\\" in path_str:
            errors.append(
                f"Skill '{name}' path must use forward slashes ('/'): {path_str}"
            )
            continue

        # Registry uses repo-relative paths; normalize '/' and avoid absolute paths.
        if Path(path_str).is_absolute() or path_str.startswith("\\") or path_str.startswith("/"):
            errors.append(
                f"Skill '{name}' has non-relative path (must be repo-relative): {path_str}"
            )
            continue

        skill_path = repo_root / Path(path_str)
        if not skill_path.exists():
            errors.append(
                f"Skill '{name}' path does not exist: {path_str}"
            )
            continue
        if not skill_path.is_file():
            errors.append(
                f"Skill '{name}' path is not a file: {path_str}"
            )
            continue

        try:
            content = skill_path.read_text(encoding="utf-8")
        except OSError as exc:
            errors.append(
                f"Failed to read skill doc for '{name}': {path_str} ({exc})"
            )
            continue

        if not content.strip():
            errors.append(f"Skill doc is empty for '{name}': {path_str}")
            continue

        if PLACEHOLDER in content:
            errors.append(
                f"Skill doc still contains placeholder text for '{name}': {path_str}"
            )

    if errors:
        return _fail(errors)

    print(f"OK: validated {len(skills)} skill(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
