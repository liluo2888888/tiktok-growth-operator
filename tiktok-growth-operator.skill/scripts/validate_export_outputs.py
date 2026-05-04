from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from zipfile import ZipFile

from openpyxl import load_workbook


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render representative scene reports and validate DOCX/XLSX export structure."
    )
    parser.add_argument(
        "--output-root",
        default="",
        help="Optional explicit output root for generated validation artifacts.",
    )
    return parser.parse_args()


def skill_root() -> Path:
    return Path(__file__).resolve().parents[1]


def default_output_root() -> Path:
    return skill_root() / "tmp" / "20260504_export_validation_suite"


def run_render(input_json: Path, output_dir: Path) -> dict:
    command = [
        sys.executable,
        str(skill_root() / "scripts" / "render_scene_report.py"),
        "--input",
        str(input_json),
        "--output-dir",
        str(output_dir),
        "--formats",
        "md,docx,xlsx",
    ]
    completed = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", check=True)
    return json.loads(completed.stdout)


def validate_workbook(path: Path) -> dict:
    workbook = load_workbook(path)
    expected_sheets = {"Summary", "Section Overview", "Section Index"}
    missing = sorted(expected_sheets - set(workbook.sheetnames))
    if missing:
        raise AssertionError(f"Missing sheets in {path.name}: {', '.join(missing)}")

    overview = workbook["Section Overview"]
    section_index = workbook["Section Index"]
    if overview["A4"].hyperlink is None:
        raise AssertionError(f"Section Overview first section link missing in {path.name}")
    if section_index["B4"].hyperlink is None or section_index["C4"].hyperlink is None:
        raise AssertionError(f"Section Index navigation link missing in {path.name}")

    target_sheet = section_index["C4"].value
    if target_sheet not in workbook.sheetnames:
        raise AssertionError(f"Section Index target sheet missing in {path.name}: {target_sheet}")
    back_link = workbook[target_sheet]["A2"].hyperlink
    if back_link is None or back_link.target != "#'Section Index'!A1":
        raise AssertionError(f"Section sheet back-link invalid in {path.name}")

    if not workbook["Summary"].tables:
        raise AssertionError(f"Summary table missing in {path.name}")
    if not overview.tables:
        raise AssertionError(f"Section Overview table missing in {path.name}")
    if not section_index.tables:
        raise AssertionError(f"Section Index table missing in {path.name}")
    for cell in ["A3", "B3", "C3", "D3", "E3", "F3"]:
        if not workbook["Summary"][cell].value:
            raise AssertionError(f"Summary metric card missing at {cell} in {path.name}")
    for cell in ["A4", "B4", "C4", "D4", "E4", "F4"]:
        if not workbook["Summary"][cell].value:
            raise AssertionError(f"Summary quality card missing at {cell} in {path.name}")

    return {
        "sheets": workbook.sheetnames,
        "summary_tables": list(workbook["Summary"].tables.keys()),
        "overview_tables": list(overview.tables.keys()),
        "index_tables": list(section_index.tables.keys()),
        "first_section_sheet": target_sheet,
        "summary_quality_values": [workbook["Summary"][cell].value for cell in ["A4", "B4", "C4", "D4", "E4", "F4"]],
        "section_index_sheet_names": [
            section_index.cell(row=row, column=3).value
            for row in range(4, section_index.max_row + 1)
            if section_index.cell(row=row, column=3).value
        ],
    }


def validate_docx(path: Path) -> dict:
    with ZipFile(path) as archive:
        names = archive.namelist()
        document_xml = archive.read("word/document.xml").decode("utf-8")

    required_strings = [
        "Contents",
        "Section Overview",
        "Back to Contents",
        "Back to Section Overview",
    ]
    missing_strings = [value for value in required_strings if value not in document_xml]
    if missing_strings:
        raise AssertionError(f"DOCX missing expected navigation text in {path.name}: {', '.join(missing_strings)}")
    if "contents_anchor" not in document_xml or "section_overview" not in document_xml:
        raise AssertionError(f"DOCX missing expected bookmarks in {path.name}")
    has_embedded_media = any(name.startswith("word/media/") for name in names)
    if has_embedded_media and "Figure 1." not in document_xml:
        raise AssertionError(f"DOCX missing expected figure caption text in {path.name}")

    return {
        "has_contents": True,
        "has_section_overview": True,
        "has_back_links": True,
        "has_figure_caption": (not has_embedded_media) or ("Figure 1." in document_xml),
        "has_embedded_media": has_embedded_media,
        "has_bookmarks": True,
    }


def synthetic_duplicate_heading_report() -> dict:
    return {
        "metadata": {
            "scene": "17",
            "project": "Synthetic Duplicate Heading Check",
            "title": "Synthetic Duplicate Heading Check",
            "status": "draft",
            "generated_at": "2026-05-04",
            "scene_title": "Synthetic Regression",
            "deliverable_type": "validation",
            "scenario_file": "synthetic.json",
            "scene_slug": "synthetic-regression",
        },
        "working_context": {
            "summary": "Synthetic report for duplicate section heading validation.",
            "inputs": ["fixture-a"],
            "minimum_evidence": [],
            "ideal_evidence": [],
            "constraints": [],
            "requested_outputs": ["docx", "xlsx"],
            "ready_checklist": ["ok"],
        },
        "executive_summary": {
            "conclusion": "Synthetic regression passed.",
            "why_it_matters": "Stable sheet naming must survive duplicate headings.",
            "next_action": "Keep exporter deterministic.",
            "confidence": "high",
        },
        "operator_guide": {
            "operator_checklist": ["Render and inspect workbook links."],
            "common_failure_modes": ["Broken overview links when titles collide."],
        },
        "sections": [
            {
                "heading": "Repeated Section",
                "instruction": "First repeated heading.",
                "paragraphs": ["Alpha"],
                "bullets": [],
                "numbered": [],
                "table": {"title": "", "headers": [], "rows": []},
            },
            {
                "heading": "Repeated Section",
                "instruction": "Second repeated heading.",
                "paragraphs": ["Beta"],
                "bullets": [],
                "numbered": [],
                "table": {"title": "", "headers": [], "rows": []},
            },
        ],
        "evidence": [],
        "assets": [{"label": "Fixture Image", "path": "", "note": "Synthetic asset row for caption validation."}],
        "notes": [],
        "sources": [],
    }


def synthetic_sparse_report() -> dict:
    return {
        "metadata": {
            "scene": "15",
            "project": "Synthetic Sparse Section Check",
            "title": "Synthetic Sparse Section Check",
            "status": "draft",
            "generated_at": "2026-05-04",
            "scene_title": "Synthetic Regression",
            "deliverable_type": "validation",
            "scenario_file": "synthetic.json",
            "scene_slug": "synthetic-regression",
        },
        "working_context": {
            "summary": "Synthetic sparse report for empty-section validation.",
            "inputs": [],
            "minimum_evidence": [],
            "ideal_evidence": [],
            "constraints": [],
            "requested_outputs": [],
            "ready_checklist": [],
        },
        "executive_summary": {
            "conclusion": "Sparse render stays stable.",
            "why_it_matters": "Empty sections should not break tables or links.",
            "next_action": "Keep placeholder handling intact.",
            "confidence": "medium",
        },
        "operator_guide": {
            "operator_checklist": [],
            "common_failure_modes": [],
        },
        "sections": [
            {
                "heading": "Empty Section",
                "instruction": "",
                "paragraphs": [],
                "bullets": [],
                "numbered": [],
                "table": {"title": "", "headers": [], "rows": []},
            }
        ],
        "evidence": [],
        "assets": [{"label": "Sparse Fixture Image", "path": "", "note": "Synthetic asset row for caption validation."}],
        "notes": [],
        "sources": [],
    }


def run_synthetic_render(report: dict, output_dir: Path) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)
        temp_path = Path(handle.name)
    try:
        return run_render(temp_path, output_dir)
    finally:
        temp_path.unlink(missing_ok=True)


def main() -> None:
    args = parse_args()
    root = Path(args.output_root) if args.output_root else default_output_root()
    root.mkdir(parents=True, exist_ok=True)

    fixtures = [
        {
            "name": "scene15",
            "input": skill_root() / "tmp" / "20260504_capture_runner_scene15" / "scene-15" / "scene-15-scene15-capture-run.json",
        },
        {
            "name": "scene17",
            "input": skill_root() / "tmp" / "20260504_capture_runner_scene17" / "scene-17" / "scene-17-tiktok-official-capture-run.json",
        },
    ]
    synthetic_fixtures = [
        {"name": "synthetic_duplicate_heading", "report": synthetic_duplicate_heading_report()},
        {"name": "synthetic_sparse_section", "report": synthetic_sparse_report()},
    ]

    results = []
    for fixture in fixtures:
        output_dir = root / fixture["name"]
        rendered = run_render(fixture["input"], output_dir)
        workbook_check = validate_workbook(Path(rendered["xlsx"]))
        docx_check = validate_docx(Path(rendered["docx"]))
        results.append(
            {
                "name": fixture["name"],
                "input": str(fixture["input"]),
                "output_dir": str(output_dir),
                "rendered": rendered,
                "workbook_check": workbook_check,
                "docx_check": docx_check,
            }
        )

    for fixture in synthetic_fixtures:
        output_dir = root / fixture["name"]
        rendered = run_synthetic_render(fixture["report"], output_dir)
        workbook_check = validate_workbook(Path(rendered["xlsx"]))
        docx_check = validate_docx(Path(rendered["docx"]))
        if fixture["name"] == "synthetic_duplicate_heading":
            sheet_names = workbook_check["section_index_sheet_names"]
            if len(sheet_names) != len(set(sheet_names)):
                raise AssertionError("Duplicate-heading synthetic fixture produced non-unique section sheet names")
        if fixture["name"] == "synthetic_sparse_section":
            if not any(str(value).startswith("1\nEmpty Sections") for value in workbook_check["summary_quality_values"]):
                raise AssertionError("Sparse synthetic fixture did not flag empty sections in Summary quality cards")
        results.append(
            {
                "name": fixture["name"],
                "input": "synthetic",
                "output_dir": str(output_dir),
                "rendered": rendered,
                "workbook_check": workbook_check,
                "docx_check": docx_check,
            }
        )

    summary_path = root / "validation_summary.json"
    summary_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"status": "ok", "summary": str(summary_path), "runs": results}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
