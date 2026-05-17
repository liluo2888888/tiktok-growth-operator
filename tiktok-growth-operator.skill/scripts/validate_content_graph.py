from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from content_graph import apply_graph_to_videos, build_content_graph, shortlist_provenance_cell
from text_normalization import read_json_file


def skill_root() -> Path:
    return Path(__file__).resolve().parents[1]


def run_import(scene: str, capture_root: Path, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / "content-graph-check.json"
    command = [
        sys.executable,
        str(skill_root() / "scripts" / "import_tiktok_capture_pack.py"),
        "--capture-root",
        str(capture_root),
        "--scene",
        scene,
        "--project",
        "Content Graph Validation",
        "--output",
        str(output),
    ]
    completed = subprocess.run(command, text=True, capture_output=True, encoding="utf-8", check=False)
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr or completed.stdout or "import failed")
    printed = normalize_output_path(completed.stdout)
    if printed.exists():
        return printed
    candidates = sorted(output_dir.glob(f"scene-{scene}-*.json"), key=lambda path: path.stat().st_mtime, reverse=True)
    if candidates:
        return candidates[0]
    raise RuntimeError(f"Could not locate imported scene {scene} report under {output_dir}")


def normalize_output_path(stdout: str) -> Path:
    for line in reversed(stdout.strip().splitlines()):
        text = line.strip()
        if text.endswith(".json"):
            return Path(text)
    return Path()


def assert_graph_file(capture_root: Path) -> dict:
    graph_path = capture_root / "content_graph.json"
    if not graph_path.exists():
        raise RuntimeError(f"Missing content graph artifact: {graph_path}")
    graph = read_json_file(graph_path)
    if not isinstance(graph, dict) or not graph.get("shortlist_provenance"):
        raise RuntimeError("content_graph.json must include shortlist_provenance map")
    return graph


def assert_report_graph(report_path: Path) -> None:
    report = read_json_file(report_path)
    if not isinstance(report, dict):
        raise RuntimeError(f"Invalid report JSON: {report_path}")
    if not isinstance(report.get("content_graph"), dict):
        raise RuntimeError(f"Report missing content_graph summary: {report_path}")
    sections = {section.get("heading"): section for section in report.get("sections", []) if isinstance(section, dict)}
    provenance_found = False
    for section in sections.values():
        headers = ((section or {}).get("table") or {}).get("headers") or []
        if "入选溯源" in headers:
            provenance_found = True
            break
    if not provenance_found:
        raise RuntimeError(f"Expected 入选溯源 column in a scene table: {report_path}")


def main() -> None:
    fixture_root = skill_root() / "testdata" / "validation"
    capture_roots = [
        fixture_root / "captures" / "scene01-strong-inputs-pass",
        fixture_root / "captures" / "tiktok-analysis-pack-smoke-20260423f" / "01-tiktok",
    ]
    results = []

    ranked_path = capture_roots[0] / "aggregate_ranked_videos.json"
    if not ranked_path.exists():
        ranked_path = capture_roots[0] / "ranked_videos.json"
    ranked_fixture = read_json_file(ranked_path)
    if not isinstance(ranked_fixture, list) or not ranked_fixture:
        raise RuntimeError("scene01 fixture ranked_videos.json is missing or empty")
    graph = build_content_graph(ranked_fixture)
    enriched = apply_graph_to_videos(ranked_fixture[:1], graph)
    if not shortlist_provenance_cell(enriched[0]):
        raise RuntimeError("shortlist_provenance_cell should not be empty for enriched videos")
    results.append({"check": "unit-graph-build", "status": "ok", "edge_count": graph.get("edge_count", 0)})

    for capture_root in capture_roots:
        if not capture_root.exists():
            continue
        report_path = run_import("01", capture_root, capture_root / "_content_graph_validation")
        graph = assert_graph_file(capture_root)
        assert_report_graph(report_path)
        results.append(
            {
                "check": "scene01-import",
                "capture_root": str(capture_root),
                "report": str(report_path),
                "cluster_summary": graph.get("cluster_summary", {}),
                "status": "ok",
            }
        )
        break

    print(json.dumps({"success": True, "results": results}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
