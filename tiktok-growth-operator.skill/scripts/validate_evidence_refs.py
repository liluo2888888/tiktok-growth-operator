from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from text_normalization import read_json_file


REQUIRED_SECTIONS = {
    "03": [
        "Executive Conclusion",
        "Structure Logic",
        "Core Mechanism",
        "Reusable Formula",
        "Risks And Adaptation Notes",
    ],
    "04": [
        "Executive Conclusion",
        "Structure Logic",
        "Core Mechanism",
        "可复用公式",
        "Risks And Adaptation Notes",
        "BGM And Sensory Layer",
        "Next Action",
    ],
    "05": [
        "Executive Conclusion",
        "Structure Logic",
        "Core Mechanism",
        "Reusable Formula",
        "Risks And Adaptation Notes",
        "Next Action",
    ],
    "08": [
        "Executive Conclusion",
        "High-Level Judgment",
        "Evidence Clusters",
        "Recommended Action",
    ],
    "17": [
        "Executive Conclusion",
        "Structure Logic",
        "Core Mechanism",
        "Reusable Formula",
        "Visual And Distribution Signature",
        "Next Action",
    ],
    "18": [
        "Executive Conclusion",
        "Objects To Track",
        "Why They Matter",
        "Next Action",
    ],
    "19": [
        "Executive Conclusion",
        "High-Level Judgment",
        "Evidence Clusters",
        "Recommended Action",
    ],
}

IMPORT_CASES = [
    ("03", "scene01-strong-inputs-pass"),
    ("04", "scene01-strong-inputs-pass"),
    ("05", "scene01-strong-inputs-pass"),
    ("08", "scene08-multi-product-home-goods-comments"),
    ("17", "scene01-strong-inputs-pass"),
    ("18", "scene18-19-multi-week-account"),
    ("19", "scene19-roi-multiwindow-account"),
]


def skill_root() -> Path:
    return Path(__file__).resolve().parents[1]


def fixture_capture_root(name: str) -> Path:
    return skill_root() / "testdata" / "validation" / "captures" / name


def run_import(scene: str, capture_root: Path, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / f"scene-{scene}-evidence-ref-check.json"
    command = [
        sys.executable,
        str(skill_root() / "scripts" / "import_tiktok_capture_pack.py"),
        "--capture-root",
        str(capture_root),
        "--scene",
        scene,
        "--project",
        "Evidence Ref Validation",
        "--output",
        str(output),
    ]
    completed = subprocess.run(command, text=True, capture_output=True, encoding="utf-8", check=False)
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr or completed.stdout or f"import failed for scene {scene}")
    for line in reversed((completed.stdout or "").strip().splitlines()):
        text = line.strip()
        if text.endswith(".json"):
            return Path(text)
    candidates = sorted(output_dir.glob(f"scene-{scene}-*.json"), key=lambda path: path.stat().st_mtime, reverse=True)
    if candidates:
        return candidates[0]
    if output.exists():
        return output
    raise RuntimeError(f"Could not locate imported report for scene {scene} under {output_dir}")


def assert_evidence_ref_shape(ref: dict, scene: str, heading: str, index: int) -> None:
    for key in ("source_type", "source_id", "source_url", "time_range", "excerpt", "supports"):
        if not str(ref.get(key, "")).strip():
            raise RuntimeError(
                f"Scene {scene} section '{heading}' evidence_refs[{index}] missing '{key}'"
            )


def assert_report_evidence_refs(scene: str, report_path: Path) -> dict:
    report = read_json_file(report_path)
    sections = {str(section.get("heading", "")).strip(): section for section in report.get("sections", [])}
    checked_sections = 0
    checked_refs = 0
    for heading in REQUIRED_SECTIONS[scene]:
        section = sections.get(heading)
        if not section:
            raise RuntimeError(f"Scene {scene} report missing section '{heading}' in {report_path}")
        refs = section.get("evidence_refs") or []
        if not refs:
            raise RuntimeError(f"Scene {scene} section '{heading}' must include evidence_refs")
        checked_sections += 1
        for index, ref in enumerate(refs, start=1):
            if not isinstance(ref, dict):
                raise RuntimeError(f"Scene {scene} section '{heading}' evidence_refs[{index}] must be an object")
            assert_evidence_ref_shape(ref, scene, heading, index)
            checked_refs += 1
    return {
        "scene": scene,
        "report": str(report_path),
        "sections_checked": checked_sections,
        "evidence_ref_count": checked_refs,
        "status": "ok",
    }


def render_smoke(scene: str, report_path: Path, output_dir: Path) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = report_path.stem
    command = [
        sys.executable,
        str(skill_root() / "scripts" / "render_scene_report.py"),
        "--input",
        str(report_path),
        "--formats",
        "md,docx,xlsx",
        "--output-dir",
        str(output_dir),
        "--base-name",
        stem,
    ]
    completed = subprocess.run(command, text=True, capture_output=True, encoding="utf-8", check=False)
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr or completed.stdout or f"render failed for scene {scene}")
    md_path = output_dir / f"{stem}.md"
    docx_path = output_dir / f"{stem}.docx"
    xlsx_path = output_dir / f"{stem}.xlsx"
    for path in (md_path, docx_path, xlsx_path):
        if not path.exists():
            raise RuntimeError(f"Expected export artifact missing: {path}")
    md_text = md_path.read_text(encoding="utf-8")
    if "Evidence References" not in md_text and "证据" not in md_text:
        raise RuntimeError(f"Rendered markdown missing evidence reference block: {md_path}")
    return {
        "scene": scene,
        "markdown": str(md_path),
        "docx": str(docx_path),
        "xlsx": str(xlsx_path),
        "status": "ok",
    }


def main() -> None:
    results: list[dict] = []
    runtime_root = skill_root() / "testdata" / "validation" / "reports" / "_evidence_ref_validation"
    for scene, fixture_name in IMPORT_CASES:
        capture_root = fixture_capture_root(fixture_name)
        if not capture_root.exists():
            raise RuntimeError(f"Missing capture fixture: {capture_root}")
        report_path = run_import(scene, capture_root, runtime_root / f"scene-{scene}")
        results.append(assert_report_evidence_refs(scene, report_path))
        if scene in {"04", "08", "18"}:
            results.append(render_smoke(scene, report_path, runtime_root / f"scene-{scene}" / "exports"))
    print(json.dumps({"success": True, "results": results}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(json.dumps({"success": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        raise SystemExit(1) from exc
