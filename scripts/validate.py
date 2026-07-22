#!/usr/bin/env python3
"""
Validate the domain-profile repository.

Two checks, no third-party dependencies (stdlib only, so CI needs no install):

1. Every ``<domain>/<version>.json`` conforms to the DomainProfile schema used by
   leqo-backend / leqo-evolution-engine (name, version, domainBlocks grouped by
   category; each block has a label and optional properties/constraints/ports).
2. ``index.json`` is consistent with the files on disk: every listed version
   exists, every profile file is listed, ``name``/``version`` inside each file
   match the manifest, and ``latest`` is the highest listed version.

Exit code 0 if everything is valid, 1 otherwise (with a report of every problem).

Usage:
    python scripts/validate.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

errors: list[str] = []


def err(message: str) -> None:
    errors.append(message)


def _is_str_list(value: object) -> bool:
    return isinstance(value, list) and all(isinstance(v, str) for v in value)


def validate_block(where: str, block: object) -> None:
    if not isinstance(block, dict):
        err(f"{where}: block is not an object")
        return
    if not isinstance(block.get("label"), str) or not block["label"]:
        err(f"{where}: block is missing a non-empty 'label'")

    for prop in block.get("properties", []) or []:
        if not isinstance(prop, dict) or not isinstance(prop.get("name"), str) or not isinstance(prop.get("type"), str):
            err(f"{where}: property must have string 'name' and 'type' ({prop!r})")

    for con in block.get("constraints", []) or []:
        if not isinstance(con, dict) or not isinstance(con.get("propertyName"), str) or not isinstance(con.get("constraint"), str):
            err(f"{where}: constraint must have string 'propertyName' and 'constraint' ({con!r})")

    if "ports" in block and not _is_str_list(block["ports"]):
        err(f"{where}: 'ports' must be a list of strings")


def validate_profile(path: Path) -> dict | None:
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        err(f"{path}: invalid JSON ({exc})")
        return None

    rel = path.relative_to(REPO_ROOT)
    if not isinstance(data, dict):
        err(f"{rel}: top-level value must be an object")
        return None
    if not isinstance(data.get("name"), str) or not data["name"]:
        err(f"{rel}: missing non-empty 'name'")
    if not isinstance(data.get("version"), str) or not data["version"]:
        err(f"{rel}: missing non-empty 'version'")

    blocks = data.get("domainBlocks")
    if not isinstance(blocks, dict):
        err(f"{rel}: 'domainBlocks' must be an object of category -> [block]")
    else:
        for category, block_list in blocks.items():
            if not isinstance(block_list, list):
                err(f"{rel}: category '{category}' must map to a list of blocks")
                continue
            for i, block in enumerate(block_list):
                validate_block(f"{rel} [{category}][{i}]", block)

    return data if isinstance(data, dict) else None


def version_key(v: str) -> tuple:
    return tuple(int(p) if p.isdigit() else p for p in v.split("."))


def validate_index() -> None:
    index_path = REPO_ROOT / "index.json"
    if not index_path.exists():
        err("index.json is missing")
        return
    try:
        index = json.loads(index_path.read_text())
    except json.JSONDecodeError as exc:
        err(f"index.json: invalid JSON ({exc})")
        return

    domains = index.get("domains")
    if not isinstance(domains, list):
        err("index.json: 'domains' must be a list")
        return

    listed_dirs = set()
    for entry in domains:
        name = entry.get("name")
        directory = entry.get("directory")
        versions = entry.get("versions")
        latest = entry.get("latest")

        if not isinstance(directory, str):
            err(f"index.json: domain entry missing string 'directory' ({entry!r})")
            continue
        listed_dirs.add(directory)
        dir_path = REPO_ROOT / directory
        if not dir_path.is_dir():
            err(f"index.json: directory '{directory}' does not exist")
            continue
        if not _is_str_list(versions) or not versions:
            err(f"index.json [{directory}]: 'versions' must be a non-empty list of strings")
            continue

        # Every listed version file exists and matches the manifest.
        for version in versions:
            vpath = dir_path / f"{version}.json"
            if not vpath.exists():
                err(f"index.json [{directory}]: listed version '{version}' has no file {version}.json")
                continue
            data = validate_profile(vpath)
            if data is None:
                continue
            if data.get("name") != name:
                err(f"{directory}/{version}.json: name '{data.get('name')}' != manifest name '{name}'")
            if data.get("version") != version:
                err(f"{directory}/{version}.json: version '{data.get('version')}' != filename version '{version}'")

        # Every profile file on disk is listed in the manifest.
        on_disk = sorted(p.stem for p in dir_path.glob("*.json"))
        missing = [v for v in on_disk if v not in versions]
        if missing:
            err(f"index.json [{directory}]: files not listed in manifest: {', '.join(missing)}")

        # latest is the highest listed version.
        if latest is not None:
            expected_latest = max(versions, key=version_key)
            if latest != expected_latest:
                err(f"index.json [{directory}]: 'latest' is '{latest}', expected '{expected_latest}'")

    # Every domain directory on disk is listed in the manifest.
    for child in REPO_ROOT.iterdir():
        if child.is_dir() and not child.name.startswith(".") and child.name != "scripts":
            if any(child.glob("*.json")) and child.name not in listed_dirs:
                err(f"index.json: directory '{child.name}' has profiles but is not in the manifest")


def main() -> int:
    validate_index()

    # Also validate any profile files not reachable via the index (defense in depth).
    for path in REPO_ROOT.glob("*/*.json"):
        if path.parent.name != "scripts":
            validate_profile(path)

    if errors:
        print(f"Validation FAILED with {len(errors)} problem(s):\n")
        for e in sorted(set(errors)):
            print(f"  - {e}")
        return 1

    print("Validation passed: all profiles and index.json are consistent.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
