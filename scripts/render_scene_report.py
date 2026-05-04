from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.oxml.shared import qn as qn_shared
from docx.shared import Inches, Pt
from openpyxl import Workbook
from openpyxl.formatting.rule import ColorScaleRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.utils import get_column_letter

from generate_scene_report import build_report_payload, load_catalog, render_markdown_from_payload, resolve_scene


TITLE_FILL = PatternFill(fill_type="solid", fgColor="1F4E78")
HEADER_FILL = PatternFill(fill_type="solid", fgColor="D9EAF7")
LABEL_FILL = PatternFill(fill_type="solid", fgColor="EEF4FB")
SUCCESS_FILL = PatternFill(fill_type="solid", fgColor="2F7D32")
WARNING_FILL = PatternFill(fill_type="solid", fgColor="D9A404")
DANGER_FILL = PatternFill(fill_type="solid", fgColor="B42318")
WRAP = Alignment(wrap_text=True, vertical="top")
THIN_SIDE = Side(style="thin", color="B8CBE0")
THIN_BORDER = Border(left=THIN_SIDE, right=THIN_SIDE, top=THIN_SIDE, bottom=THIN_SIDE)
HYPERLINK_FONT = Font(color="0563C1", underline="single")
RESERVED_SHEET_TITLES = {
    "Summary",
    "Section Overview",
    "Section Index",
    "Context Lists",
    "Evidence",
    "Assets",
    "Notes",
    "Sources",
    "Operator Guide",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render a structured TikTok Growth Operator scene report JSON into Markdown, DOCX, and XLSX outputs."
    )
    parser.add_argument("--input", help="Structured report JSON path.")
    parser.add_argument("--scene", help="Scene id or slug for scaffold generation.")
    parser.add_argument("--project", help="Project name for scaffold generation.")
    parser.add_argument("--context-file", help="Optional UTF-8 context file for scaffold generation.")
    parser.add_argument("--output-dir", required=True, help="Directory for rendered outputs.")
    parser.add_argument(
        "--formats",
        default="md,docx,xlsx",
        help="Comma-separated output formats: md, docx, xlsx.",
    )
    parser.add_argument(
        "--base-name",
        default="",
        help="Optional explicit output base filename without extension.",
    )
    return parser.parse_args()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def slugify(text: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9_-]+", "-", text.strip().lower())
    return normalized.strip("-") or "report"


def normalize_string_list(values: list | None) -> list[str]:
    return [str(item).strip() for item in values or [] if str(item).strip()]


def normalize_table(table: dict | None) -> dict:
    payload = table or {}
    headers = normalize_string_list(payload.get("headers"))
    rows = []
    for row in payload.get("rows", []) or []:
        rows.append([str(cell).strip() for cell in row])
    return {
        "title": str(payload.get("title", "")).strip(),
        "headers": headers,
        "rows": rows,
    }


def resolve_payload(args: argparse.Namespace) -> dict:
    if args.input:
        payload = load_json(Path(args.input))
    else:
        if not args.scene or not args.project:
            raise SystemExit("Provide --input, or provide both --scene and --project.")
        skill_root = Path(__file__).resolve().parents[1]
        catalog = load_catalog(skill_root)
        scene = resolve_scene(catalog, args.scene)
        context = Path(args.context_file).read_text(encoding="utf-8") if args.context_file else ""
        payload = build_report_payload(scene, args.project, context)

    metadata = payload.setdefault("metadata", {})
    scene_id = str(metadata.get("scene", "")).strip()
    skill_root = Path(__file__).resolve().parents[1]
    catalog = load_catalog(skill_root)
    if scene_id:
        scene = resolve_scene(catalog, scene_id)
        metadata.setdefault("scene_slug", scene["slug"])
        metadata.setdefault("scene_title", scene["title"])
        metadata.setdefault("deliverable_type", scene["deliverable_type"])
        metadata.setdefault("scenario_file", scene["scenario_file"])
    metadata.setdefault("project", "untitled-project")
    metadata.setdefault("title", f"Scene {metadata.get('scene', 'XX')} Report - {metadata['project']}")
    metadata.setdefault("status", "draft")
    metadata.setdefault("generated_at", "")

    working_context = payload.setdefault("working_context", {})
    working_context.setdefault("summary", "")
    working_context.setdefault("inputs", [])
    working_context.setdefault("minimum_evidence", [])
    working_context.setdefault("ideal_evidence", [])
    working_context.setdefault("constraints", [])
    working_context.setdefault("requested_outputs", [])
    working_context.setdefault("ready_checklist", [])

    executive = payload.setdefault("executive_summary", {})
    executive.setdefault("conclusion", "")
    executive.setdefault("why_it_matters", "")
    executive.setdefault("next_action", "")
    executive.setdefault("confidence", "")

    operator_guide = payload.setdefault("operator_guide", {})
    operator_guide.setdefault("operator_checklist", [])
    operator_guide.setdefault("common_failure_modes", [])

    normalized_sections = []
    for section in payload.get("sections", []) or []:
        normalized_sections.append(
            {
                "heading": str(section.get("heading", "")).strip() or "Untitled Section",
                "instruction": str(section.get("instruction", "")).strip(),
                "paragraphs": normalize_string_list(section.get("paragraphs")),
                "bullets": normalize_string_list(section.get("bullets")),
                "numbered": normalize_string_list(section.get("numbered")),
                "table": normalize_table(section.get("table")),
            }
        )
    payload["sections"] = normalized_sections

    normalized_evidence = []
    for item in payload.get("evidence", []) or []:
        normalized_evidence.append(
            {
                "label": str(item.get("label", "")).strip(),
                "detail": str(item.get("detail", "")).strip(),
                "source": str(item.get("source", "")).strip(),
            }
        )
    payload["evidence"] = normalized_evidence

    normalized_assets = []
    for item in payload.get("assets", []) or []:
        normalized_assets.append(
            {
                "label": str(item.get("label", "")).strip(),
                "path": str(item.get("path", "")).strip(),
                "note": str(item.get("note", "")).strip(),
            }
        )
    payload["assets"] = normalized_assets
    payload["notes"] = normalize_string_list(payload.get("notes"))
    payload["sources"] = normalize_string_list(payload.get("sources"))
    return payload


def infer_base_name(report: dict, explicit_base_name: str) -> str:
    if explicit_base_name.strip():
        return explicit_base_name.strip()
    metadata = report["metadata"]
    return f"scene-{metadata.get('scene', 'xx')}-{slugify(metadata.get('project', '') or metadata.get('title', 'report'))}"


def set_doc_font(document: Document) -> None:
    normal = document.styles["Normal"]
    normal.font.name = "Microsoft YaHei"
    normal.font.size = Pt(10.5)
    normal.element.rPr.rFonts.set(qn("w:eastAsia"), "Microsoft YaHei")
    for style_name in ["Title", "Heading 1", "Heading 2", "Heading 3"]:
        style = document.styles[style_name]
        style.font.name = "Microsoft YaHei"
        style.element.rPr.rFonts.set(qn("w:eastAsia"), "Microsoft YaHei")


def shade_doc_cell(cell, fill_hex: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn_shared("w:fill"), fill_hex)
    tc_pr.append(shd)


def set_cell_text(cell, text: str) -> None:
    cell.text = text
    for paragraph in cell.paragraphs:
        paragraph.paragraph_format.space_after = Pt(0)


def style_doc_table(table, header_row: bool = True, label_col: int | None = None) -> None:
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for row_index, row in enumerate(table.rows):
        for col_index, cell in enumerate(row.cells):
            for paragraph in cell.paragraphs:
                paragraph.paragraph_format.space_after = Pt(0)
            if row_index == 0 and header_row:
                shade_doc_cell(cell, "D9EAF7")
                for run in cell.paragraphs[0].runs:
                    run.bold = True
            elif label_col is not None and col_index == label_col:
                shade_doc_cell(cell, "EEF4FB")
                for run in cell.paragraphs[0].runs:
                    run.bold = True


def repeat_doc_header_row(table) -> None:
    header = table.rows[0]._tr
    tr_pr = header.get_or_add_trPr()
    tbl_header = OxmlElement("w:tblHeader")
    tbl_header.set(qn_shared("w:val"), "true")
    tr_pr.append(tbl_header)


def default_doc_table_widths(column_count: int) -> list[float]:
    width_map = {
        2: [1.6, 5.2],
        3: [1.4, 3.4, 2.0],
        4: [1.3, 2.4, 1.55, 1.55],
        5: [2.45, 0.8, 0.8, 0.8, 1.95],
        6: [1.75, 2.3, 0.6, 0.6, 0.6, 1.55],
    }
    if column_count in width_map:
        return width_map[column_count]
    usable_width = 6.8
    width = round(usable_width / max(column_count, 1), 2)
    return [width] * column_count


def set_doc_table_widths(table, column_widths: list[float] | None = None) -> None:
    widths = column_widths or default_doc_table_widths(len(table.columns))
    table.autofit = False
    for column_index, width in enumerate(widths[: len(table.columns)]):
        for cell in table.columns[column_index].cells:
            cell.width = Inches(width)


def add_doc_list(document: Document, title: str, values: list[str], style: str = "List Bullet") -> None:
    if not values:
        return
    document.add_heading(title, level=2)
    for item in values:
        document.add_paragraph(item, style=style)


def add_doc_field(paragraph, instruction: str) -> None:
    run = paragraph.add_run()
    fld_char_begin = OxmlElement("w:fldChar")
    fld_char_begin.set(qn_shared("w:fldCharType"), "begin")
    run._r.append(fld_char_begin)

    instr_text = OxmlElement("w:instrText")
    instr_text.set(qn_shared("xml:space"), "preserve")
    instr_text.text = instruction
    run._r.append(instr_text)

    fld_char_separate = OxmlElement("w:fldChar")
    fld_char_separate.set(qn_shared("w:fldCharType"), "separate")
    run._r.append(fld_char_separate)

    placeholder = paragraph.add_run(" ")
    fld_char_end = OxmlElement("w:fldChar")
    fld_char_end.set(qn_shared("w:fldCharType"), "end")
    placeholder._r.append(fld_char_end)


def bookmark_name(text: str, index: int) -> str:
    normalized = re.sub(r"[^A-Za-z0-9_]+", "_", text).strip("_") or f"section_{index}"
    return f"sec_{index}_{normalized[:28]}"


def add_doc_bookmark(paragraph, name: str, bookmark_id: int) -> None:
    start = OxmlElement("w:bookmarkStart")
    start.set(qn_shared("w:id"), str(bookmark_id))
    start.set(qn_shared("w:name"), name)
    end = OxmlElement("w:bookmarkEnd")
    end.set(qn_shared("w:id"), str(bookmark_id))
    paragraph._p.insert(0, start)
    paragraph._p.append(end)


def add_doc_internal_link(paragraph, text: str, anchor: str) -> None:
    hyperlink = OxmlElement("w:hyperlink")
    hyperlink.set(qn_shared("w:anchor"), anchor)
    run = OxmlElement("w:r")
    run_pr = OxmlElement("w:rPr")
    color = OxmlElement("w:color")
    color.set(qn_shared("w:val"), "0563C1")
    underline = OxmlElement("w:u")
    underline.set(qn_shared("w:val"), "single")
    run_pr.append(color)
    run_pr.append(underline)
    text_node = OxmlElement("w:t")
    text_node.text = text
    run.append(run_pr)
    run.append(text_node)
    hyperlink.append(run)
    paragraph._p.append(hyperlink)


def add_doc_toc(document: Document) -> None:
    heading = document.add_heading("Contents", level=1)
    add_doc_bookmark(heading, "contents_anchor", 899)
    paragraph = document.add_paragraph()
    add_doc_field(paragraph, 'TOC \\o "1-2" \\h \\z \\u')
    note = document.add_paragraph()
    note_run = note.add_run("If the table of contents looks empty, update fields once in Word.")
    note_run.italic = True


def add_doc_navigation_links(document: Document, links: list[tuple[str, str]]) -> None:
    paragraph = document.add_paragraph()
    paragraph.paragraph_format.space_after = Pt(8)
    for index, (label, anchor) in enumerate(links):
        add_doc_internal_link(paragraph, label, anchor)
        if index < len(links) - 1:
            paragraph.add_run(" | ")


def add_doc_header_footer(document: Document, report: dict) -> None:
    section = document.sections[0]
    header = section.header.paragraphs[0]
    header.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    header.text = f"{report['metadata'].get('scene', '')} | {report['metadata'].get('project', '')}"

    footer = section.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    footer.add_run(report["metadata"].get("generated_at", "") or "Generated")
    footer.add_run(" | Page ")
    add_doc_field(footer, "PAGE")


def add_doc_cover_page(document: Document, report: dict) -> None:
    metadata = report["metadata"]
    executive = report["executive_summary"]
    working_context = report["working_context"]

    banner = document.add_paragraph()
    banner.alignment = WD_ALIGN_PARAGRAPH.CENTER
    banner.paragraph_format.space_after = Pt(10)
    banner_run = banner.add_run((metadata.get("deliverable_type", "Scene Report") or "Scene Report").upper())
    banner_run.bold = True
    banner_run.font.size = Pt(10)

    title = document.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.paragraph_format.space_after = Pt(12)
    title_run = title.add_run(metadata["title"])
    title_run.bold = True
    title_run.font.size = Pt(22)

    subtitle = document.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    subtitle.paragraph_format.space_after = Pt(6)
    subtitle.add_run(
        f"Scene {metadata.get('scene', '')} | {metadata.get('scene_title', '') or metadata.get('deliverable_type', '')}".strip(" |")
    ).italic = True

    detail = document.add_paragraph()
    detail.alignment = WD_ALIGN_PARAGRAPH.CENTER
    detail.paragraph_format.space_after = Pt(18)
    detail.add_run(
        f"{metadata.get('project', '')} | {metadata.get('status', '') or 'draft'} | {metadata.get('generated_at', '') or 'Generated'}".strip(
            " |"
        )
    )

    cover_table = document.add_table(rows=4, cols=2)
    cover_rows = [
        ("Scene", f"{metadata.get('scene', '')} - {metadata.get('scene_title', '')}".strip(" -")),
        ("Deliverable", metadata.get("deliverable_type", "")),
        ("Scenario File", metadata.get("scenario_file", "")),
        ("Scene Slug", metadata.get("scene_slug", "")),
    ]
    for index, (label, value) in enumerate(cover_rows):
        set_cell_text(cover_table.cell(index, 0), label)
        set_cell_text(cover_table.cell(index, 1), value)
    style_doc_table(cover_table, header_row=False, label_col=0)
    set_doc_table_widths(cover_table, [1.6, 5.2])

    context_heading = document.add_paragraph()
    context_heading.paragraph_format.space_after = Pt(4)
    context_heading.add_run("Working Context").bold = True
    context_body = document.add_paragraph(working_context.get("summary", "") or "No working context provided.")
    context_body.paragraph_format.space_after = Pt(12)

    summary_heading = document.add_paragraph()
    summary_heading.paragraph_format.space_after = Pt(4)
    summary_heading.add_run("Executive Snapshot").bold = True
    summary_bits = [
        executive.get("conclusion", "").strip(),
        executive.get("why_it_matters", "").strip(),
        executive.get("next_action", "").strip(),
    ]
    for item in [value for value in summary_bits if value]:
        document.add_paragraph(item, style="List Bullet")

    document.add_page_break()


def add_label_value(document: Document, label: str, value: str) -> None:
    paragraph = document.add_paragraph()
    run = paragraph.add_run(label)
    run.bold = True
    paragraph.add_run(value or "N/A")


def render_table_docx(
    document: Document,
    headers: list[str],
    rows: list[list[str]],
    column_widths: list[float] | None = None,
) -> None:
    if not headers:
        return
    table = document.add_table(rows=1, cols=len(headers))
    for column, header in enumerate(headers):
        set_cell_text(table.cell(0, column), header)
    for row in rows:
        cells = table.add_row().cells
        padded = row + [""] * max(0, len(headers) - len(row))
        for column, value in enumerate(padded[: len(headers)]):
            set_cell_text(cells[column], value)
    style_doc_table(table)
    repeat_doc_header_row(table)
    set_doc_table_widths(table, column_widths)


def add_doc_image_caption(document: Document, caption: str) -> None:
    paragraph = document.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.paragraph_format.space_after = Pt(8)
    run = paragraph.add_run(caption)
    run.italic = True


def add_doc_section_overview(document: Document, report: dict, section_bookmarks: list[str]) -> None:
    heading = document.add_heading("Section Overview", level=1)
    add_doc_bookmark(heading, "section_overview", 900)
    table = document.add_table(rows=1, cols=5)
    headers = ["Section", "Paragraphs", "Bullets", "Steps", "Table"]
    for column, header in enumerate(headers):
        set_cell_text(table.cell(0, column), header)
    for index, section in enumerate(report["sections"]):
        row = table.add_row().cells
        table_summary = section["table"]["title"] or ("Yes" if section["table"]["headers"] else "No")
        values = [
            section["heading"],
            str(len(section["paragraphs"])),
            str(len(section["bullets"])),
            str(len(section["numbered"])),
            table_summary,
        ]
        for column, value in enumerate(values):
            set_cell_text(row[column], value)
        paragraph = row[0].paragraphs[0]
        paragraph.clear()
        add_doc_internal_link(paragraph, section["heading"], section_bookmarks[index])
    style_doc_table(table)
    set_doc_table_widths(table, [2.45, 0.8, 0.8, 0.8, 1.95])


def add_excel_table(ws, start_row: int, end_row: int, end_col: int, name: str) -> None:
    if end_row <= start_row or end_col < 1:
        return
    ref = f"A{start_row}:{get_column_letter(end_col)}{end_row}"
    table = Table(displayName=name, ref=ref)
    table.tableStyleInfo = TableStyleInfo(
        name="TableStyleMedium2",
        showFirstColumn=False,
        showLastColumn=False,
        showRowStripes=True,
        showColumnStripes=False,
    )
    ws.add_table(table)


def style_metric_card(cell, label: str, value: int) -> None:
    cell.value = f"{value}\n{label}"
    cell.font = Font(bold=True, color="FFFFFF", size=11)
    cell.fill = TITLE_FILL
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    cell.border = THIN_BORDER


def style_status_metric_card(cell, label: str, value: int) -> None:
    if value <= 0:
        fill = SUCCESS_FILL
        font_color = "FFFFFF"
    elif value == 1:
        fill = WARNING_FILL
        font_color = "111111"
    else:
        fill = DANGER_FILL
        font_color = "FFFFFF"
    cell.value = f"{value}\n{label}"
    cell.font = Font(bold=True, color=font_color, size=11)
    cell.fill = fill
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    cell.border = THIN_BORDER


def write_docx(report: dict, output: Path) -> None:
    metadata = report["metadata"]
    working_context = report["working_context"]
    executive = report["executive_summary"]
    section_bookmarks = [bookmark_name(section["heading"], index) for index, section in enumerate(report["sections"], start=1)]

    document = Document()
    set_doc_font(document)
    section = document.sections[0]
    section.top_margin = Inches(0.7)
    section.bottom_margin = Inches(0.7)
    section.left_margin = Inches(0.75)
    section.right_margin = Inches(0.75)
    add_doc_header_footer(document, report)
    add_doc_cover_page(document, report)
    title_heading = document.add_heading(metadata["title"], level=0)
    title_heading.alignment = WD_ALIGN_PARAGRAPH.CENTER

    meta_table = document.add_table(rows=7, cols=2)
    meta_rows = [
        ("Scene", f"{metadata.get('scene', '')} - {metadata.get('scene_title', '')}".strip(" -")),
        ("Project", metadata.get("project", "")),
        ("Deliverable Type", metadata.get("deliverable_type", "")),
        ("Generated", metadata.get("generated_at", "")),
        ("Status", metadata.get("status", "")),
        ("Scenario File", metadata.get("scenario_file", "")),
        ("Scene Slug", metadata.get("scene_slug", "")),
    ]
    for index, (label, value) in enumerate(meta_rows):
        set_cell_text(meta_table.cell(index, 0), label)
        set_cell_text(meta_table.cell(index, 1), value)
    style_doc_table(meta_table, header_row=False, label_col=0)
    set_doc_table_widths(meta_table, [1.6, 5.2])

    working_heading = document.add_heading("Working Context", level=1)
    working_heading.paragraph_format.keep_with_next = True
    document.add_paragraph(working_context.get("summary", "") or "No working context provided.")
    for label, key in [
        ("Inputs", "inputs"),
        ("Minimum Evidence", "minimum_evidence"),
        ("Ideal Evidence", "ideal_evidence"),
        ("Constraints", "constraints"),
        ("Requested Outputs", "requested_outputs"),
        ("Ready Checklist", "ready_checklist"),
    ]:
        add_doc_list(document, label, normalize_string_list(working_context.get(key)))

    executive_heading = document.add_heading("Executive Summary", level=1)
    executive_heading.paragraph_format.keep_with_next = True
    add_label_value(document, "Conclusion: ", executive.get("conclusion", ""))
    add_label_value(document, "Why It Matters: ", executive.get("why_it_matters", ""))
    add_label_value(document, "Next Action: ", executive.get("next_action", ""))
    add_label_value(document, "Confidence: ", executive.get("confidence", ""))

    add_doc_toc(document)
    add_doc_section_overview(document, report, section_bookmarks)
    add_doc_navigation_links(
        document,
        [("Back to Contents", "contents_anchor"), ("Jump to First Section", section_bookmarks[0])]
        if section_bookmarks
        else [("Back to Contents", "contents_anchor")],
    )

    for label, key in [
        ("Operator Checklist", "operator_checklist"),
        ("Common Failure Modes", "common_failure_modes"),
    ]:
        add_doc_list(document, label, normalize_string_list(report["operator_guide"].get(key)))

    if report["evidence"]:
        evidence_heading = document.add_heading("Evidence", level=1)
        evidence_heading.paragraph_format.keep_with_next = True
        render_table_docx(
            document,
            ["Label", "Detail", "Source"],
            [[item["label"], item["detail"], item["source"]] for item in report["evidence"]],
            [1.5, 3.8, 1.5],
        )

    if report["sections"]:
        document.add_page_break()

    for index, section in enumerate(report["sections"], start=1):
        heading = document.add_heading(section["heading"], level=1)
        heading.paragraph_format.keep_with_next = True
        add_doc_bookmark(heading, section_bookmarks[index - 1], 1000 + index)
        add_doc_navigation_links(document, [("Back to Contents", "contents_anchor"), ("Back to Section Overview", "section_overview")])
        if section["instruction"]:
            paragraph = document.add_paragraph()
            run = paragraph.add_run(section["instruction"])
            run.italic = True
        for paragraph_text in section["paragraphs"]:
            document.add_paragraph(paragraph_text)
        for item in section["bullets"]:
            document.add_paragraph(item, style="List Bullet")
        for item in section["numbered"]:
            document.add_paragraph(item, style="List Number")
        table = section["table"]
        if table["title"]:
            table_heading = document.add_heading(table["title"], level=2)
            table_heading.paragraph_format.keep_with_next = True
        render_table_docx(document, table["headers"], table["rows"])
        if not any([section["paragraphs"], section["bullets"], section["numbered"], table["headers"]]):
            document.add_paragraph("Fill this section.")

    if report["assets"]:
        assets_heading = document.add_heading("Assets", level=1)
        assets_heading.paragraph_format.keep_with_next = True
        render_table_docx(
            document,
            ["Label", "Path", "Note"],
            [[asset["label"], asset["path"], asset["note"]] for asset in report["assets"]],
            [1.5, 3.8, 1.5],
        )
        image_index = 1
        for asset in report["assets"]:
            path = Path(asset["path"]) if asset["path"] else None
            if path and path.exists() and path.suffix.lower() in {".png", ".jpg", ".jpeg", ".bmp", ".gif"}:
                document.add_picture(str(path), width=Inches(5.6))
                add_doc_image_caption(document, f"Figure {image_index}. {asset['label'] or path.name}")
                image_index += 1

    if report["notes"]:
        notes_heading = document.add_heading("Notes", level=1)
        notes_heading.paragraph_format.keep_with_next = True
        for item in report["notes"]:
            document.add_paragraph(item, style="List Bullet")

    if report["sources"]:
        sources_heading = document.add_heading("Sources", level=1)
        sources_heading.paragraph_format.keep_with_next = True
        for item in report["sources"]:
            document.add_paragraph(item, style="List Bullet")

    output.parent.mkdir(parents=True, exist_ok=True)
    document.save(output)


def style_title_row(ws, row: int, start_col: int, end_col: int, text: str) -> None:
    ws.merge_cells(start_row=row, start_column=start_col, end_row=row, end_column=end_col)
    cell = ws.cell(row=row, column=start_col)
    cell.value = text
    cell.font = Font(bold=True, color="FFFFFF", size=12)
    cell.fill = TITLE_FILL
    cell.alignment = Alignment(horizontal="center", vertical="center")
    cell.border = THIN_BORDER


def style_header_row(ws, row: int, headers: list[str]) -> None:
    for column, header in enumerate(headers, start=1):
        cell = ws.cell(row=row, column=column)
        cell.value = header
        cell.font = Font(bold=True)
        cell.fill = HEADER_FILL
        cell.alignment = WRAP
        cell.border = THIN_BORDER


def style_label_cell(cell) -> None:
    cell.font = Font(bold=True)
    cell.fill = LABEL_FILL
    cell.alignment = WRAP
    cell.border = THIN_BORDER


def style_value_cell(cell) -> None:
    cell.alignment = WRAP
    cell.border = THIN_BORDER


def apply_hyperlink(cell, target: str) -> None:
    if not target.strip():
        return
    cell.hyperlink = target
    cell.font = HYPERLINK_FONT


def add_sheet_back_link(ws, label: str = "Back to Section Overview", target: str = "#'Section Overview'!A1") -> None:
    cell = ws.cell(row=2, column=1)
    cell.value = label
    cell.hyperlink = target
    cell.font = HYPERLINK_FONT


def finalize_sheet(ws, freeze_cell: str = "A4", filter_row: int | None = None) -> None:
    ws.freeze_panes = freeze_cell
    if filter_row is not None and ws.max_row >= filter_row and ws.max_column >= 1:
        ws.auto_filter.ref = f"A{filter_row}:{get_column_letter(ws.max_column)}{ws.max_row}"
    ws.sheet_view.zoomScale = 90


def safe_sheet_title(index: int, heading: str, used: set[str]) -> str:
    base = re.sub(r"[:\\/*?\[\]]+", "-", heading).strip() or f"Section {index}"
    prefix = f"{index:02d}-"
    budget = 31 - len(prefix)
    candidate = prefix + base[:budget]
    counter = 2
    while candidate in used:
        suffix = f"-{counter}"
        candidate = prefix + base[: max(1, budget - len(suffix))] + suffix
        counter += 1
    used.add(candidate)
    return candidate


def build_section_sheet_map(report: dict) -> list[str]:
    used_titles = set(RESERVED_SHEET_TITLES)
    return [
        safe_sheet_title(index, section["heading"], used_titles)
        for index, section in enumerate(report["sections"], start=1)
    ]


def write_summary_sheet(workbook: Workbook, report: dict) -> None:
    ws = workbook.active
    ws.title = "Summary"
    style_title_row(ws, 1, 1, 6, report["metadata"]["title"])
    metrics = [
        ("Sections", len(report["sections"])),
        ("Evidence", len(report["evidence"])),
        ("Assets", len(report["assets"])),
        ("Notes", len(report["notes"])),
        ("Sources", len(report["sources"])),
        ("Ready Items", len(normalize_string_list(report["working_context"].get("ready_checklist")))),
    ]
    for column, (label, value) in enumerate(metrics, start=1):
        style_metric_card(ws.cell(row=3, column=column), label, value)
    ws.row_dimensions[3].height = 34
    quality_metrics = [
        ("Empty Sections", sum(1 for section in report["sections"] if not any([section["paragraphs"], section["bullets"], section["numbered"], section["table"]["headers"]]))),
        ("Missing Evidence", 1 if not report["evidence"] else 0),
        ("Missing Assets", 1 if not report["assets"] else 0),
        ("Broken Asset Paths", sum(1 for asset in report["assets"] if asset["path"] and not Path(asset["path"]).exists())),
        ("No Notes", 1 if not report["notes"] else 0),
        ("No Sources", 1 if not report["sources"] else 0),
    ]
    for column, (label, value) in enumerate(quality_metrics, start=1):
        style_status_metric_card(ws.cell(row=4, column=column), label, value)
    ws.row_dimensions[4].height = 34
    style_header_row(ws, 6, ["Field", "Value"])
    rows = [
        ("Scene", f"{report['metadata'].get('scene', '')} - {report['metadata'].get('scene_title', '')}".strip(" -")),
        ("Project", report["metadata"].get("project", "")),
        ("Deliverable Type", report["metadata"].get("deliverable_type", "")),
        ("Generated", report["metadata"].get("generated_at", "")),
        ("Status", report["metadata"].get("status", "")),
        ("Scenario File", report["metadata"].get("scenario_file", "")),
        ("Working Context", report["working_context"].get("summary", "")),
        ("Conclusion", report["executive_summary"].get("conclusion", "")),
        ("Why It Matters", report["executive_summary"].get("why_it_matters", "")),
        ("Next Action", report["executive_summary"].get("next_action", "")),
        ("Confidence", report["executive_summary"].get("confidence", "")),
    ]
    row = 7
    for label, value in rows:
        ws.cell(row=row, column=1).value = label
        ws.cell(row=row, column=2).value = value
        style_label_cell(ws.cell(row=row, column=1))
        style_value_cell(ws.cell(row=row, column=2))
        row += 1
    ws.cell(row=row, column=1).value = "Section Overview"
    ws.cell(row=row, column=2).value = "Open the section navigation sheet"
    style_label_cell(ws.cell(row=row, column=1))
    style_value_cell(ws.cell(row=row, column=2))
    apply_hyperlink(ws.cell(row=row, column=2), "#'Section Overview'!A1")
    row += 1
    ws.cell(row=row, column=1).value = "Section Index"
    ws.cell(row=row, column=2).value = "Open the section-to-sheet index"
    style_label_cell(ws.cell(row=row, column=1))
    style_value_cell(ws.cell(row=row, column=2))
    apply_hyperlink(ws.cell(row=row, column=2), "#'Section Index'!A1")
    ws.column_dimensions["A"].width = 22
    ws.column_dimensions["B"].width = 110
    for column in range(3, 7):
        ws.column_dimensions[get_column_letter(column)].width = 15
    add_excel_table(ws, 6, row, 2, "SummaryTable")
    finalize_sheet(ws, freeze_cell="A7", filter_row=6)


def write_section_overview_sheet(workbook: Workbook, report: dict, section_sheet_map: list[str]) -> None:
    ws = workbook.create_sheet("Section Overview")
    style_title_row(ws, 1, 1, 6, "Section Overview")
    add_sheet_back_link(ws, label="Back to Summary", target="#'Summary'!A1")
    headers = ["Section", "Instruction", "Paragraphs", "Bullets", "Steps", "Table Title"]
    style_header_row(ws, 3, headers)
    row = 4
    for index, section in enumerate(report["sections"], start=1):
        values = [
            section["heading"],
            section["instruction"],
            len(section["paragraphs"]),
            len(section["bullets"]),
            len(section["numbered"]),
            section["table"]["title"] or ("Yes" if section["table"]["headers"] else "No"),
        ]
        for column, value in enumerate(values, start=1):
            ws.cell(row=row, column=column).value = value
            style_value_cell(ws.cell(row=row, column=column))
        apply_hyperlink(ws.cell(row=row, column=1), f"#'{section_sheet_map[index - 1]}'!A1")
        row += 1
    widths = [28, 44, 12, 12, 12, 26]
    for index, width in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(index)].width = width
    if row > 4:
        for column in ["C", "D", "E"]:
            ws.conditional_formatting.add(
                f"{column}4:{column}{row - 1}",
                ColorScaleRule(
                    start_type="min",
                    start_color="F2F7FC",
                    mid_type="percentile",
                    mid_value=50,
                    mid_color="9CC2E5",
                    end_type="max",
                    end_color="1F4E78",
                ),
            )
        add_excel_table(ws, 3, row - 1, 6, "SectionOverviewTable")
    finalize_sheet(ws, freeze_cell="A4", filter_row=3)


def write_section_index_sheet(workbook: Workbook, report: dict, section_sheet_map: list[str]) -> None:
    ws = workbook.create_sheet("Section Index")
    style_title_row(ws, 1, 1, 7, "Section Index")
    add_sheet_back_link(ws, label="Back to Summary", target="#'Summary'!A1")
    headers = ["#", "Section", "Sheet", "Instruction", "Paragraphs", "Bullets", "Steps"]
    style_header_row(ws, 3, headers)
    row = 4
    for index, (section, sheet_name) in enumerate(zip(report["sections"], section_sheet_map), start=1):
        values = [
            index,
            section["heading"],
            sheet_name,
            section["instruction"],
            len(section["paragraphs"]),
            len(section["bullets"]),
            len(section["numbered"]),
        ]
        for column, value in enumerate(values, start=1):
            ws.cell(row=row, column=column).value = value
            style_value_cell(ws.cell(row=row, column=column))
        apply_hyperlink(ws.cell(row=row, column=2), f"#'{sheet_name}'!A1")
        apply_hyperlink(ws.cell(row=row, column=3), f"#'{sheet_name}'!A1")
        row += 1
    widths = [8, 30, 26, 40, 12, 12, 12]
    for index, width in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(index)].width = width
    if row > 4:
        for column in ["E", "F", "G"]:
            ws.conditional_formatting.add(
                f"{column}4:{column}{row - 1}",
                ColorScaleRule(
                    start_type="min",
                    start_color="F2F7FC",
                    mid_type="percentile",
                    mid_value=50,
                    mid_color="9CC2E5",
                    end_type="max",
                    end_color="1F4E78",
                ),
            )
        add_excel_table(ws, 3, row - 1, 7, "SectionIndexTable")
    finalize_sheet(ws, freeze_cell="A4", filter_row=3)


def write_operator_guide_sheet(workbook: Workbook, report: dict) -> None:
    ws = workbook.create_sheet("Operator Guide")
    style_title_row(ws, 1, 1, 2, "Operator Guide")
    add_sheet_back_link(ws, label="Back to Summary", target="#'Summary'!A1")
    style_header_row(ws, 3, ["Category", "Item"])
    row = 4
    for label, key in [
        ("Operator Checklist", "operator_checklist"),
        ("Common Failure Modes", "common_failure_modes"),
    ]:
        for item in normalize_string_list(report["operator_guide"].get(key)):
            ws.cell(row=row, column=1).value = label
            ws.cell(row=row, column=2).value = item
            style_label_cell(ws.cell(row=row, column=1))
            style_value_cell(ws.cell(row=row, column=2))
            row += 1
    ws.column_dimensions["A"].width = 28
    ws.column_dimensions["B"].width = 100
    if row > 4:
        add_excel_table(ws, 3, row - 1, 2, "OperatorGuideTable")
    finalize_sheet(ws, freeze_cell="A4", filter_row=3)


def write_context_lists_sheet(workbook: Workbook, report: dict) -> None:
    ws = workbook.create_sheet("Context Lists")
    style_title_row(ws, 1, 1, 2, "Working Context Lists")
    add_sheet_back_link(ws, label="Back to Summary", target="#'Summary'!A1")
    style_header_row(ws, 3, ["Category", "Item"])
    row = 4
    for label, key in [
        ("Inputs", "inputs"),
        ("Minimum Evidence", "minimum_evidence"),
        ("Ideal Evidence", "ideal_evidence"),
        ("Constraints", "constraints"),
        ("Requested Outputs", "requested_outputs"),
        ("Ready Checklist", "ready_checklist"),
    ]:
        for item in normalize_string_list(report["working_context"].get(key)):
            ws.cell(row=row, column=1).value = label
            ws.cell(row=row, column=2).value = item
            style_label_cell(ws.cell(row=row, column=1))
            style_value_cell(ws.cell(row=row, column=2))
            row += 1
    ws.column_dimensions["A"].width = 24
    ws.column_dimensions["B"].width = 100
    if row > 4:
        add_excel_table(ws, 3, row - 1, 2, "ContextListsTable")
    finalize_sheet(ws, freeze_cell="A4", filter_row=3)


def write_section_sheets(workbook: Workbook, report: dict, section_sheet_map: list[str]) -> None:
    for index, (section, sheet_title) in enumerate(zip(report["sections"], section_sheet_map), start=1):
        ws = workbook.create_sheet(sheet_title)
        style_title_row(ws, 1, 1, 4, section["heading"])
        add_sheet_back_link(ws, target="#'Section Index'!A1")
        row = 3

        if section["instruction"]:
            ws.cell(row=row, column=1).value = "Instruction"
            style_label_cell(ws.cell(row=row, column=1))
            ws.cell(row=row, column=2).value = section["instruction"]
            ws.merge_cells(start_row=row, start_column=2, end_row=row, end_column=4)
            style_value_cell(ws.cell(row=row, column=2))
            row += 2

        wrote_any = False
        for paragraph in section["paragraphs"]:
            ws.cell(row=row, column=1).value = "Paragraph"
            style_label_cell(ws.cell(row=row, column=1))
            ws.cell(row=row, column=2).value = paragraph
            ws.merge_cells(start_row=row, start_column=2, end_row=row, end_column=4)
            style_value_cell(ws.cell(row=row, column=2))
            row += 1
            wrote_any = True

        for item in section["bullets"]:
            ws.cell(row=row, column=1).value = "Bullet"
            style_label_cell(ws.cell(row=row, column=1))
            ws.cell(row=row, column=2).value = item
            ws.merge_cells(start_row=row, start_column=2, end_row=row, end_column=4)
            style_value_cell(ws.cell(row=row, column=2))
            row += 1
            wrote_any = True

        for order, item in enumerate(section["numbered"], start=1):
            ws.cell(row=row, column=1).value = f"Step {order}"
            style_label_cell(ws.cell(row=row, column=1))
            ws.cell(row=row, column=2).value = item
            ws.merge_cells(start_row=row, start_column=2, end_row=row, end_column=4)
            style_value_cell(ws.cell(row=row, column=2))
            row += 1
            wrote_any = True

        table = section["table"]
        if table["headers"]:
            if table["title"]:
                ws.cell(row=row, column=1).value = "Table"
                style_label_cell(ws.cell(row=row, column=1))
                ws.cell(row=row, column=2).value = table["title"]
                ws.merge_cells(start_row=row, start_column=2, end_row=row, end_column=4)
                style_value_cell(ws.cell(row=row, column=2))
                row += 1
            style_header_row(ws, row, table["headers"])
            row += 1
            for table_row in table["rows"]:
                padded = table_row + [""] * max(0, len(table["headers"]) - len(table_row))
                for column, value in enumerate(padded[: len(table["headers"])], start=1):
                    ws.cell(row=row, column=column).value = value
                    style_value_cell(ws.cell(row=row, column=column))
                row += 1
            wrote_any = True

        if not wrote_any:
            ws.cell(row=row, column=1).value = "Fill this section."
            ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=4)
            style_value_cell(ws.cell(row=row, column=1))

        for column in ["A", "B", "C", "D"]:
            ws.column_dimensions[column].width = 26 if column == "A" else 36
        if row > 3:
            add_excel_table(ws, 3, row - 1, 4, f"SectionTable{index}")
        finalize_sheet(ws, freeze_cell="A3")


def write_simple_list_sheet(workbook: Workbook, title: str, headers: list[str], rows: list[list[str]]) -> None:
    ws = workbook.create_sheet(title)
    style_title_row(ws, 1, 1, len(headers), title)
    add_sheet_back_link(ws, label="Back to Summary", target="#'Summary'!A1")
    style_header_row(ws, 3, headers)
    row = 4
    for values in rows:
        padded = values + [""] * max(0, len(headers) - len(values))
        for column, value in enumerate(padded[: len(headers)], start=1):
            ws.cell(row=row, column=column).value = value
            style_value_cell(ws.cell(row=row, column=column))
            text_value = str(value).strip()
            if text_value.startswith("http://") or text_value.startswith("https://"):
                apply_hyperlink(ws.cell(row=row, column=column), text_value)
            elif re.match(r"^[A-Za-z]:\\", text_value):
                apply_hyperlink(ws.cell(row=row, column=column), text_value)
        row += 1
    for column_index in range(1, len(headers) + 1):
        ws.column_dimensions[get_column_letter(column_index)].width = 38
    if row > 4:
        safe_name = re.sub(r"[^A-Za-z0-9]+", "", title) or "Sheet"
        add_excel_table(ws, 3, row - 1, len(headers), f"{safe_name}Table")
    finalize_sheet(ws, freeze_cell="A4", filter_row=3)


def write_xlsx(report: dict, output: Path) -> None:
    workbook = Workbook()
    section_sheet_map = build_section_sheet_map(report)
    write_summary_sheet(workbook, report)
    write_section_overview_sheet(workbook, report, section_sheet_map)
    write_section_index_sheet(workbook, report, section_sheet_map)
    write_operator_guide_sheet(workbook, report)
    write_context_lists_sheet(workbook, report)
    write_section_sheets(workbook, report, section_sheet_map)
    write_simple_list_sheet(
        workbook,
        "Evidence",
        ["Label", "Detail", "Source"],
        [[item["label"], item["detail"], item["source"]] for item in report["evidence"]],
    )
    write_simple_list_sheet(
        workbook,
        "Assets",
        ["Label", "Path", "Note"],
        [[item["label"], item["path"], item["note"]] for item in report["assets"]],
    )
    write_simple_list_sheet(workbook, "Notes", ["Note"], [[item] for item in report["notes"]])
    write_simple_list_sheet(workbook, "Sources", ["Source"], [[item] for item in report["sources"]])
    output.parent.mkdir(parents=True, exist_ok=True)
    workbook.save(output)


def main() -> None:
    args = parse_args()
    report = resolve_payload(args)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    base_name = infer_base_name(report, args.base_name)
    formats = [item.strip().lower() for item in args.formats.split(",") if item.strip()]

    written: dict[str, str] = {}
    if "md" in formats:
        path = output_dir / f"{base_name}.md"
        path.write_text(render_markdown_from_payload(report), encoding="utf-8")
        written["md"] = str(path)
    if "docx" in formats:
        path = output_dir / f"{base_name}.docx"
        write_docx(report, path)
        written["docx"] = str(path)
    if "xlsx" in formats:
        path = output_dir / f"{base_name}.xlsx"
        write_xlsx(report, path)
        written["xlsx"] = str(path)

    print(json.dumps(written, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
