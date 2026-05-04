from __future__ import annotations

import json
from pathlib import Path


def load_route_eval_fixtures(skill_root: Path) -> dict:
    fixture_path = skill_root / "references" / "route-eval-fixtures.json"
    return json.loads(fixture_path.read_text(encoding="utf-8"))
