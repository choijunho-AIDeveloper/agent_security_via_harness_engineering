"""
Filesystem interface for harness package operations.

Handles reading the current project state, computing diffs against the template,
and applying file operations (guides + sensors) to the target directory.
"""

import os
import stat
import json
import shutil
from pathlib import Path
from typing import Any

from .template import GUIDE_FILE_DESCRIPTIONS, ALL_TEMPLATE_FILES

# Directories we read when scanning the existing harness
HARNESS_SCAN_DIRS = [".agent", "docs", ".claude"]
HARNESS_SCAN_FILES = ["CLAUDE.md"]

# Directories/files that are never touched (security)
BLOCKED_ABSOLUTE_PREFIXES = ["/etc", "/sys", "/proc", "/boot", "/usr/bin", "/usr/sbin", "/bin", "/sbin"]


# ---------------------------------------------------------------------------
# Path Safety
# ---------------------------------------------------------------------------

def resolve_root(raw_path: str) -> Path:
    """Expand ~ and resolve to absolute path."""
    return Path(raw_path).expanduser().resolve()


def validate_path(root_path: str, target_path: str) -> bool:
    """
    Ensure target_path resolves inside root_path.
    Returns True if safe, False if the path escapes the root.
    """
    root = resolve_root(root_path)
    target = (root / target_path).resolve()

    # Must be inside root
    try:
        target.relative_to(root)
    except ValueError:
        return False

    # Must not be a blocked system path
    target_str = str(target)
    for blocked in BLOCKED_ABSOLUTE_PREFIXES:
        if target_str.startswith(blocked):
            return False

    return True


# ---------------------------------------------------------------------------
# Scanning
# ---------------------------------------------------------------------------

def scan_existing_harness(root_path: str) -> dict[str, Any]:
    """
    Scan the current project for an existing harness.

    Returns:
        {
          "tree": str,                   # printable directory tree
          "guides": dict[str, str],      # relative_path -> file content
          "sensors": dict | None,        # parsed .claude/settings.json or None
          "claude_md": str | None,       # CLAUDE.md content or None
          "hook_scripts": dict[str, str] # relative_path -> script content
        }
    """
    root = resolve_root(root_path)
    guides: dict[str, str] = {}
    hook_scripts: dict[str, str] = {}
    sensors = None
    claude_md = None

    # Read CLAUDE.md
    claude_md_path = root / "CLAUDE.md"
    if claude_md_path.exists():
        claude_md = claude_md_path.read_text(encoding="utf-8")

    # Read .agent/ and docs/
    for scan_dir in [".agent", "docs"]:
        dir_path = root / scan_dir
        if dir_path.exists():
            for file_path in sorted(dir_path.rglob("*.md")):
                rel = str(file_path.relative_to(root))
                try:
                    guides[rel] = file_path.read_text(encoding="utf-8")
                except Exception:
                    guides[rel] = ""

    # Read .claude/settings.json
    settings_path = root / ".claude" / "settings.json"
    if settings_path.exists():
        try:
            sensors = json.loads(settings_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            sensors = None

    # Read .claude/hooks/ scripts
    hooks_dir = root / ".claude" / "hooks"
    if hooks_dir.exists():
        for script_path in sorted(hooks_dir.iterdir()):
            if script_path.is_file():
                rel = str(script_path.relative_to(root))
                try:
                    hook_scripts[rel] = script_path.read_text(encoding="utf-8")
                except Exception:
                    hook_scripts[rel] = ""

    return {
        "tree": _build_tree(root_path),
        "guides": guides,
        "sensors": sensors,
        "claude_md": claude_md,
        "hook_scripts": hook_scripts,
    }


def diff_against_template(current_guides: dict[str, str]) -> dict[str, list[str]]:
    """
    Compare existing guides against the template file list.

    Returns:
        {
          "missing":  list of template files not present,
          "existing": list of template files already present,
          "extra":    list of present files not in the template
        }
    """
    template_set = set(ALL_TEMPLATE_FILES)
    current_set = set(current_guides.keys())

    return {
        "missing": sorted(template_set - current_set),
        "existing": sorted(template_set & current_set),
        "extra": sorted(current_set - template_set),
    }


def _build_tree(root_path: str, max_depth: int = 4) -> str:
    """Build a compact text representation of the project directory tree."""
    root = resolve_root(root_path)
    lines = [str(root.name) + "/"]

    IGNORE = {
        ".git", "__pycache__", "node_modules", ".venv", "venv",
        ".mypy_cache", ".pytest_cache", "dist", "build", ".next",
        "coverage", ".DS_Store",
    }

    def _walk(path: Path, prefix: str, depth: int):
        if depth > max_depth:
            return
        try:
            entries = sorted(path.iterdir(), key=lambda e: (e.is_file(), e.name))
        except PermissionError:
            return
        entries = [e for e in entries if e.name not in IGNORE]
        for i, entry in enumerate(entries):
            connector = "└── " if i == len(entries) - 1 else "├── "
            lines.append(prefix + connector + entry.name + ("/" if entry.is_dir() else ""))
            if entry.is_dir():
                extension = "    " if i == len(entries) - 1 else "│   "
                _walk(entry, prefix + extension, depth + 1)

    _walk(root, "", 1)
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Dry Run
# ---------------------------------------------------------------------------

def compute_dry_run(root_path: str, operations: list[dict]) -> list[dict]:
    """
    For each file operation, compute what would change without touching the FS.

    Returns list of dicts:
        {
          "action": "create|modify|delete",
          "path": str,
          "exists_before": bool,
          "content_before": str | None,
          "content_after": str | None,  # None for delete
          "reason": str
        }
    """
    root = resolve_root(root_path)
    previews = []

    for op in operations:
        path = op.get("path", "")
        action = op.get("action", "")
        content = op.get("content", "")
        reason = op.get("reason", "")

        if not validate_path(root_path, path):
            previews.append({
                "action": action,
                "path": path,
                "error": "허용된 경로 밖이거나 시스템 경로입니다 — 건너뜀",
                "reason": reason,
            })
            continue

        abs_path = root / path
        exists = abs_path.exists()
        content_before = None
        if exists and abs_path.is_file():
            try:
                content_before = abs_path.read_text(encoding="utf-8")
            except Exception:
                content_before = "(읽기 실패)"

        previews.append({
            "action": action,
            "path": path,
            "exists_before": exists,
            "content_before": content_before,
            "content_after": content if action in ("create", "modify") else None,
            "reason": reason,
        })

    return previews


# ---------------------------------------------------------------------------
# Apply Operations
# ---------------------------------------------------------------------------

def apply_guides(root_path: str, operations: list[dict]) -> dict[str, list]:
    """
    Apply file create/modify/delete operations for guide documents.

    Returns:
        {"success": [path, ...], "failed": [(path, reason), ...]}
    """
    root = resolve_root(root_path)
    success = []
    failed = []

    for op in operations:
        path = op.get("path", "")
        action = op.get("action", "")
        content = op.get("content", "")

        if not validate_path(root_path, path):
            failed.append((path, "경로 검증 실패 — 허용된 범위를 벗어남"))
            continue

        abs_path = root / path

        try:
            if action in ("create", "modify"):
                abs_path.parent.mkdir(parents=True, exist_ok=True)
                abs_path.write_text(content, encoding="utf-8")
                success.append(path)

            elif action == "delete":
                if abs_path.exists():
                    abs_path.unlink()
                success.append(path)

            else:
                failed.append((path, f"알 수 없는 action: {action}"))

        except Exception as e:
            failed.append((path, str(e)))

    return {"success": success, "failed": failed}


def apply_sensors(root_path: str, sensors: dict) -> dict[str, list]:
    """
    Apply sensor configuration: write .claude/settings.json and hook scripts.

    sensors = {
        "settings_json": {...},
        "hook_scripts": [
            {"path": ".claude/hooks/foo.sh", "content": "...", "executable": true}
        ]
    }
    """
    root = resolve_root(root_path)
    success = []
    failed = []

    # Write settings.json
    settings_json = sensors.get("settings_json")
    if settings_json:
        settings_path = root / ".claude" / "settings.json"
        try:
            settings_path.parent.mkdir(parents=True, exist_ok=True)

            # Merge with existing settings if present
            existing = {}
            if settings_path.exists():
                try:
                    existing = json.loads(settings_path.read_text(encoding="utf-8"))
                except json.JSONDecodeError:
                    existing = {}

            merged = _merge_settings(existing, settings_json)
            settings_path.write_text(json.dumps(merged, indent=2, ensure_ascii=False), encoding="utf-8")
            success.append(".claude/settings.json")
        except Exception as e:
            failed.append((".claude/settings.json", str(e)))

    # Write hook scripts
    for script in sensors.get("hook_scripts", []):
        path = script.get("path", "")
        content = script.get("content", "")
        executable = script.get("executable", False)

        if not validate_path(root_path, path):
            failed.append((path, "경로 검증 실패"))
            continue

        abs_path = root / path
        try:
            abs_path.parent.mkdir(parents=True, exist_ok=True)
            abs_path.write_text(content, encoding="utf-8")
            if executable:
                current = abs_path.stat().st_mode
                abs_path.chmod(current | stat.S_IXUSR | stat.S_IXGRP)
            success.append(path)
        except Exception as e:
            failed.append((path, str(e)))

    return {"success": success, "failed": failed}


def apply_harness_package(
    root_path: str,
    guides: list[dict],
    sensors: dict,
    claude_md: str | None = None,
) -> dict[str, Any]:
    """
    Apply a complete harness package: guides + sensors + CLAUDE.md.

    Returns combined results from all sub-operations.
    """
    all_success = []
    all_failed = []

    # Apply guide documents
    guide_result = apply_guides(root_path, guides)
    all_success.extend(guide_result["success"])
    all_failed.extend(guide_result["failed"])

    # Apply CLAUDE.md if provided
    if claude_md is not None:
        root = resolve_root(root_path)
        try:
            (root / "CLAUDE.md").write_text(claude_md, encoding="utf-8")
            all_success.append("CLAUDE.md")
        except Exception as e:
            all_failed.append(("CLAUDE.md", str(e)))

    # Apply sensors
    if sensors:
        sensor_result = apply_sensors(root_path, sensors)
        all_success.extend(sensor_result["success"])
        all_failed.extend(sensor_result["failed"])

    return {"success": all_success, "failed": all_failed}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _merge_settings(existing: dict, new: dict) -> dict:
    """
    Deep-merge new settings into existing.
    For hooks lists, append new entries rather than overwriting.
    """
    result = dict(existing)

    for key, value in new.items():
        if key == "hooks" and isinstance(value, dict):
            existing_hooks = result.get("hooks", {})
            merged_hooks = dict(existing_hooks)
            for event, entries in value.items():
                if event in merged_hooks and isinstance(merged_hooks[event], list):
                    # Append without duplicating by command
                    existing_commands = {
                        h.get("hooks", [{}])[0].get("command", "")
                        for h in merged_hooks[event]
                        if h.get("hooks")
                    }
                    for entry in entries:
                        cmd = ""
                        if entry.get("hooks"):
                            cmd = entry["hooks"][0].get("command", "")
                        if cmd not in existing_commands:
                            merged_hooks[event].append(entry)
                else:
                    merged_hooks[event] = entries
            result["hooks"] = merged_hooks
        else:
            result[key] = value

    return result
