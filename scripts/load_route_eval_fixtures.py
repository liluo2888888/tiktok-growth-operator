from __future__ import annotations

import json
from pathlib import Path

from text_normalization import read_json_file


def load_route_eval_fixtures(skill_root: Path) -> dict:
    fixture_path = skill_root / "references" / "route-eval-fixtures.json"
    payload = read_json_file(fixture_path)
    return payload if isinstance(payload, dict) else {}
