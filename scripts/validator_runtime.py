from __future__ import annotations

import shutil
import tempfile
from datetime import datetime, timedelta
from pathlib import Path


VALIDATOR_RUNTIME_PREFIX = "tgo-validate-"


def validator_temp_parent(skill_root: Path) -> Path:
    parent = skill_root.parent / ".codex-tmp"
    parent.mkdir(parents=True, exist_ok=True)
    return parent


def cleanup_old_validator_roots(skill_root: Path, *, max_age_hours: int = 72) -> list[str]:
    temp_parent = validator_temp_parent(skill_root)
    cutoff = datetime.now() - timedelta(hours=max_age_hours)
    removed: list[str] = []
    for child in temp_parent.iterdir():
        if not child.is_dir() or not child.name.startswith(VALIDATOR_RUNTIME_PREFIX):
            continue
        try:
            modified_at = datetime.fromtimestamp(child.stat().st_mtime)
        except OSError:
            continue
        if modified_at > cutoff:
            continue
        try:
            shutil.rmtree(child)
            removed.append(str(child))
        except OSError:
            continue
    return removed


def create_validator_runtime(skill_root: Path, run_slug: str, explicit_root: str = "") -> Path:
    if explicit_root.strip():
        root = Path(explicit_root).expanduser().resolve()
        root.mkdir(parents=True, exist_ok=True)
        return root
    cleanup_old_validator_roots(skill_root)
    temp_parent = validator_temp_parent(skill_root)
    return Path(tempfile.mkdtemp(prefix=f"{VALIDATOR_RUNTIME_PREFIX}{run_slug}-", dir=str(temp_parent)))
