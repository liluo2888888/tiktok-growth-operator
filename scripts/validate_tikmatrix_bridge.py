from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from validator_runtime import create_validator_runtime


DEFAULT_PROFILE_POSTS = Path(
    r"E:\tiktok\TikMatrix\tmp\live-profile-posts-browser-batch\mrorangecat555\profile_posts.json"
)
DEFAULT_COMMENTS = Path(
    r"E:\tiktok\TikMatrix\tmp\comments-live-mrorangecat-paged\7624057229930450192\comments.json"
)
DEFAULT_DOWNLOADS = Path(
    r"E:\tiktok\TikMatrix\tmp\skill-batch-download\downloads.json"
)


def resolve_fixture_path(*candidates: Path) -> Path:
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise SystemExit(f"Missing required validation fixture. Checked: {[str(candidate) for candidate in candidates]}")


def require_path(path: Path, label: str) -> None:
    if not path.exists():
        raise SystemExit(f"Missing required {label}: {path}")


def run_bridge(skill_root: Path, profile_posts: Path, comments: Path, downloads: Path) -> dict:
    scripts_root = skill_root / "scripts"
    output_root = create_validator_runtime(skill_root, "tikmatrix-bridge")
    command = [
        sys.executable,
        str(scripts_root / "run_tikmatrix_capture_bridge.py"),
        "--profile-posts-json",
        str(profile_posts),
        "--comments-json",
        str(comments),
        "--downloads-json",
        str(downloads),
        "--scene",
        "08",
        "--name",
        "validate-tikmatrix-bridge-scene08",
        "--project",
        "Validate TikMatrix Bridge Scene 08",
        "--market",
        "US",
        "--formats",
        "md",
        "--output-root",
        str(output_root),
    ]
    completed = subprocess.run(command, text=True, capture_output=True)
    payload = {
        "command": command,
        "returncode": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }
    if completed.returncode != 0:
        return payload

    data = json.loads(completed.stdout)
    bridge = data.get("bridge", {})
    operator_run = data.get("operator_run", {})
    bridge_root = Path(str(bridge.get("bridge_root", "")))
    run_root = Path(str(operator_run.get("run_root", "")))
    report_json = Path(str(operator_run.get("report_json", "")))

    expected_paths = [
        bridge_root / "summary.json",
        bridge_root / "profile_summary.json",
        bridge_root / "aggregate_ranked_videos.json",
        bridge_root / "aggregate_qualified_videos.json",
        bridge_root / "comments_sampled.json",
        bridge_root / "comments_flat.csv",
        bridge_root / "source_manifest.json",
        run_root / "run_manifest.json",
        report_json,
    ]
    missing = [str(path) for path in expected_paths if not path.exists()]
    if missing:
        payload["returncode"] = 1
        payload["stderr"] = "TikMatrix bridge validation missing expected outputs: " + "; ".join(missing)
        return payload

    operator_packs = operator_run.get("operator_packs", [])
    if not operator_packs:
        payload["returncode"] = 1
        payload["stderr"] = "TikMatrix bridge validation expected at least one derived operator pack"
        return payload

    ranked_rows = json.loads((bridge_root / "aggregate_ranked_videos.json").read_text(encoding="utf-8"))
    qualified_rows = json.loads((bridge_root / "aggregate_qualified_videos.json").read_text(encoding="utf-8"))
    if not isinstance(ranked_rows, list) or not ranked_rows:
        payload["returncode"] = 1
        payload["stderr"] = "TikMatrix bridge validation expected ranked rows in aggregate_ranked_videos.json"
        return payload
    if not isinstance(qualified_rows, list) or not qualified_rows:
        payload["returncode"] = 1
        payload["stderr"] = "TikMatrix bridge validation expected qualified rows in aggregate_qualified_videos.json"
        return payload

    top_ranked = ranked_rows[0]
    top_qualified = qualified_rows[0]
    required_ranked_fields = [
        "reuse_value_score",
        "popularity_score",
        "score_breakdown",
        "why_selected",
        "reuse_value_label",
        "reuse_purpose",
        "shopping_intent",
        "tkshop_signal",
        "commerce_confidence",
    ]
    missing_ranked_fields = [field for field in required_ranked_fields if field not in top_ranked or top_ranked.get(field) in ("", None, {})]
    if missing_ranked_fields:
        payload["returncode"] = 1
        payload["stderr"] = "TikMatrix bridge validation missing ranked quality fields: " + ", ".join(missing_ranked_fields)
        return payload

    breakdown = top_ranked.get("score_breakdown")
    if not isinstance(breakdown, dict):
        payload["returncode"] = 1
        payload["stderr"] = "TikMatrix bridge validation expected score_breakdown to be a JSON object"
        return payload
    expected_breakdown_keys = {
        "caption_completeness",
        "enrichment",
        "comment_density",
        "authority_signal",
        "proof_strength",
        "series_potential",
        "portability",
        "topic_spread",
        "commerce_signal",
        "popularity",
    }
    missing_breakdown_keys = sorted(expected_breakdown_keys.difference(breakdown.keys()))
    if missing_breakdown_keys:
        payload["returncode"] = 1
        payload["stderr"] = "TikMatrix bridge validation missing score_breakdown keys: " + ", ".join(missing_breakdown_keys)
        return payload

    required_qualified_fields = [
        "shortlist_priority",
        "shortlist_bucket",
        "shortlist_decision",
        "scene03_reason",
    ]
    missing_qualified_fields = [field for field in required_qualified_fields if field not in top_qualified or top_qualified.get(field) in ("", None)]
    if missing_qualified_fields:
        payload["returncode"] = 1
        payload["stderr"] = "TikMatrix bridge validation missing qualified shortlist fields: " + ", ".join(missing_qualified_fields)
        return payload

    payload["parsed"] = data
    payload["validated_output_root"] = str(output_root)
    return payload


def main() -> int:
    skill_root = Path(__file__).resolve().parents[1]
    fixture_root = skill_root / "testdata" / "validation" / "tikmatrix"
    profile_posts = resolve_fixture_path(
        fixture_root / "live-profile-posts-browser-batch" / "mrorangecat555" / "profile_posts.json",
        DEFAULT_PROFILE_POSTS,
    )
    comments = resolve_fixture_path(
        fixture_root / "comments-live-mrorangecat-paged" / "7624057229930450192" / "comments.json",
        DEFAULT_COMMENTS,
    )
    downloads = resolve_fixture_path(
        fixture_root / "skill-batch-download" / "downloads.json",
        DEFAULT_DOWNLOADS,
    )
    require_path(profile_posts, "profile_posts.json")
    require_path(comments, "comments.json")
    require_path(downloads, "downloads.json")
    result = run_bridge(skill_root, profile_posts, comments, downloads)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result["returncode"] != 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
