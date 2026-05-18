from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from category_saturation import estimate_category_saturation
from text_normalization import read_json_file
from weekly_baseline import compute_weekly_baseline_delta, ensure_weekly_baseline_artifact


def skill_root() -> Path:
    return Path(__file__).resolve().parents[1]


def fixture_capture_root(name: str) -> Path:
    return skill_root() / "testdata" / "validation" / "captures" / name


def load_ranked_videos(capture_root: Path) -> list[dict]:
    for name in ("aggregate_ranked_videos.json", "ranked_videos.json"):
        path = capture_root / name
        if path.exists():
            payload = read_json_file(path)
            if isinstance(payload, list):
                return payload
    raise FileNotFoundError(f"no ranked video list under {capture_root}")


def validate_weekly_delta_fixture(name: str) -> dict:
    capture_root = fixture_capture_root(name)
    ranked = load_ranked_videos(capture_root)
    delta = ensure_weekly_baseline_artifact(capture_root, ranked)
    artifact_path = capture_root / "weekly_baseline_delta.json"
    if not artifact_path.exists():
        raise RuntimeError(f"missing weekly_baseline_delta.json for {name}")
    if not delta.get("anomalies"):
        raise RuntimeError(f"expected anomalies for {name}")
    if delta.get("mode") not in {"compare", "baseline"}:
        raise RuntimeError(f"unexpected weekly baseline mode for {name}: {delta.get('mode')}")
    return {"capture_root": str(capture_root), "mode": delta.get("mode"), "anomaly_count": len(delta.get("anomalies") or [])}


def validate_scene07_saturation() -> dict:
    capture_root = fixture_capture_root("scene01-strong-inputs-pass")
    ranked = load_ranked_videos(capture_root)
    assessment = estimate_category_saturation(ranked)
    if not assessment.get("verdict"):
        raise RuntimeError("scene07 saturation verdict missing")
    return {"verdict": assessment.get("verdict"), "demand_heat": assessment.get("demand_heat")}


def validate_scene18_import() -> dict:
    capture_root = fixture_capture_root("scene18-19-multi-week-account")
    output_dir = skill_root() / "testdata" / "validation" / "reports" / "_weekly_baseline_validation" / "scene-18"
    output_dir.mkdir(parents=True, exist_ok=True)
    command = [
        sys.executable,
        str(skill_root() / "scripts" / "import_tiktok_capture_pack.py"),
        "--capture-root",
        str(capture_root),
        "--scene",
        "18",
        "--project",
        "Weekly Baseline Validation",
        "--output",
        str(output_dir / "scene-18.json"),
    ]
    completed = subprocess.run(command, text=True, capture_output=True, encoding="utf-8", check=False)
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr or completed.stdout or "scene 18 import failed")
    report_path = output_dir / "scene-18.json"
    if not report_path.exists():
        candidates = sorted(output_dir.glob("scene-18-*.json"), key=lambda item: item.stat().st_mtime, reverse=True)
        if not candidates:
            raise RuntimeError("scene 18 report not found")
        report_path = candidates[0]
    report = read_json_file(report_path)
    why = next((section for section in report.get("sections", []) if section.get("heading") == "Why They Matter"), {})
    rows = (why.get("table") or {}).get("rows") or []
    if not rows:
        raise RuntimeError("scene 18 Why They Matter table is empty")
    text = json.dumps(why, ensure_ascii=False)
    if "Change-First" not in text and "周度基线" not in text:
        raise RuntimeError("scene 18 missing change-first weekly digest cues")
    return {"report": str(report_path), "why_row_count": len(rows)}


def main() -> None:
    results = {
        "scene18_fixture": validate_weekly_delta_fixture("scene18-19-multi-week-account"),
        "scene19_fixture": validate_weekly_delta_fixture("scene19-roi-multiwindow-account"),
        "scene07_saturation": validate_scene07_saturation(),
        "scene18_import": validate_scene18_import(),
        "smoke": {
            "empty": compute_weekly_baseline_delta([]).get("mode"),
        },
    }
    print(json.dumps({"ok": True, "results": results}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        raise SystemExit(1) from exc
