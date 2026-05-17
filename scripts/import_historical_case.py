from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

from generate_scene_report import build_report_payload, load_catalog, resolve_scene
from text_normalization import read_json_file, write_json_file


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Import a historical Douyin/TikTok case pack into a filled scene-report JSON for the TikTok Growth Operator package."
    )
    parser.add_argument("--scene", required=True, help="Scene id or slug. Recommended: 04 or 17.")
    parser.add_argument("--case-json", required=True, help="Historical case JSON, e.g. case_data_v3.json.")
    parser.add_argument("--source-manifest", default="", help="Optional source_manifest.json path.")
    parser.add_argument("--transcript-manifest", default="", help="Optional transcript_manifest.json path.")
    parser.add_argument("--project", default="", help="Optional explicit project name.")
    parser.add_argument("--output", required=True, help="Output scene-report JSON path.")
    return parser.parse_args()


def load_json(path: str) -> dict:
    if not path.strip():
        return {}
    loaded = read_json_file(Path(path))
    if not isinstance(loaded, dict):
        raise SystemExit(f"Expected JSON object: {path}")
    return loaded


def clean_text(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        parts = [clean_text(item) for item in value]
        return "\n".join(item for item in parts if item)
    if isinstance(value, dict):
        import json

        return json.dumps(value, ensure_ascii=False)
    return str(value).replace("\r\n", "\n").strip()


def list_of_dicts(payload: dict, key: str) -> list[dict]:
    value = payload.get(key, [])
    return value if isinstance(value, list) else []


def pick_transcript_excerpt(transcript_manifest: dict, limit: int = 12) -> list[str]:
    segments = (((transcript_manifest or {}).get("meta") or {}).get("segments")) or []
    lines: list[str] = []
    for segment in segments[:limit]:
        start = clean_text(segment.get("start"))
        end = clean_text(segment.get("end"))
        text = clean_text(segment.get("text_original") or segment.get("text"))
        if not text:
            continue
        stamp = f"{start}-{end}s" if start or end else ""
        lines.append(f"{stamp} {text}".strip())
    return lines


def summarize_story_beats(case_payload: dict, limit: int = 6) -> list[list[str]]:
    rows: list[list[str]] = []
    for beat in list_of_dicts(case_payload, "story_beats")[:limit]:
        rows.append(
            [
                clean_text(beat.get("title")),
                clean_text(beat.get("task")),
                clean_text(beat.get("why_key")),
                clean_text(beat.get("copy")),
            ]
        )
    return rows


def summarize_core_variables(case_payload: dict, limit: int = 5) -> list[list[str]]:
    rows: list[list[str]] = []
    for item in list_of_dicts(case_payload, "core_variables")[:limit]:
        rows.append(
            [
                clean_text(item.get("name")),
                clean_text(item.get("why")),
                clean_text(item.get("copy")),
                clean_text(item.get("risk")),
            ]
        )
    return rows


def summarize_diagnostics(case_payload: dict, limit: int = 6) -> list[list[str]]:
    rows: list[list[str]] = []
    for item in list_of_dicts(case_payload, "main_diagnostics")[:limit]:
        rows.append(
            [
                clean_text(item.get("dimension")),
                clean_text(item.get("judgment")),
                clean_text(item.get("evidence")),
                clean_text(item.get("action")),
            ]
        )
    return rows


def make_context(case_payload: dict, source_manifest: dict, transcript_manifest: dict) -> str:
    meta = case_payload.get("meta", {})
    executive = case_payload.get("executive", {})
    lines = [
        f"Historical case import for {clean_text(meta.get('account'))} on {clean_text(meta.get('platform'))}.",
        f"Video: {clean_text(meta.get('title'))}",
        f"URL: {clean_text(meta.get('url'))}",
        f"Content form: {clean_text(meta.get('content_form'))}",
        f"Duration: {clean_text(meta.get('duration'))}",
        f"Existing one-line judgment: {clean_text(executive.get('one_liner'))}",
        f"Best use: {clean_text(executive.get('best_use'))}",
        f"Biggest risk: {clean_text(executive.get('biggest_risk'))}",
    ]
    source_backend = clean_text(source_manifest.get("download_backend"))
    if source_backend:
        lines.append(f"Download backend: {source_backend}")
    transcript_provider = clean_text(transcript_manifest.get("provider_used") or transcript_manifest.get("provider"))
    if transcript_provider:
        lines.append(f"Transcript provider: {transcript_provider}")
    return "\n".join(line for line in lines if line)


def fill_metadata(payload: dict, case_payload: dict, project: str) -> None:
    meta = case_payload.get("meta", {})
    payload["metadata"]["project"] = project
    payload["metadata"]["title"] = f"Scene {payload['metadata']['scene']} Report - {project}"
    payload["metadata"]["generated_at"] = datetime.now().isoformat(timespec="seconds")
    payload["metadata"]["status"] = "imported"
    payload["sources"] = payload.get("sources", [])
    payload["sources"].extend(
        [
            clean_text(meta.get("url")),
            clean_text(meta.get("title")),
        ]
    )


def fill_working_context(payload: dict, case_payload: dict, source_manifest: dict, transcript_manifest: dict) -> None:
    meta = case_payload.get("meta", {})
    working = payload["working_context"]
    working["summary"] = make_context(case_payload, source_manifest, transcript_manifest)
    working["inputs"] = [
        f"Account: {clean_text(meta.get('account'))}",
        f"Platform: {clean_text(meta.get('platform'))}",
        f"Video URL: {clean_text(meta.get('url'))}",
        f"Evidence bundle: keyframes, storyboard, transcript, prior curated case pack",
    ]
    working["constraints"] = list(dict.fromkeys(working.get("constraints", []) + [
        "Historical project import. Preserve conclusions already supported by the evidence bundle.",
        "Do not overfit creator-specific charisma into reusable pattern claims.",
    ]))
    working["requested_outputs"] = list(dict.fromkeys(working.get("requested_outputs", []) + [
        "Imported structured report with reusable formula",
        "Evidence-linked adaptation rules",
    ]))
    working["minimum_evidence"] = list(dict.fromkeys(working.get("minimum_evidence", []) + [
        "Prior curated case JSON",
        "Original source manifest",
        "Transcript manifest excerpt",
    ]))
    working["ideal_evidence"] = list(dict.fromkeys(working.get("ideal_evidence", []) + [
        "Storyboard frames",
        "Historical report markdown and workbook",
    ]))
    working["ready_checklist"] = list(dict.fromkeys(working.get("ready_checklist", []) + [
        "Core mechanism grounded in the historical evidence pack",
        "Transferable pattern separated from creator-specific advantage",
    ]))


def fill_executive(payload: dict, case_payload: dict) -> None:
    executive = case_payload.get("executive", {})
    payload["executive_summary"]["conclusion"] = clean_text(executive.get("one_liner"))
    payload["executive_summary"]["why_it_matters"] = clean_text(executive.get("best_use"))
    payload["executive_summary"]["next_action"] = "Use the imported formula to create one safer adapted version and one more assertive version."
    payload["executive_summary"]["confidence"] = clean_text(case_payload.get("confidence_note") or "medium")


def build_evidence(case_payload: dict, source_manifest: dict, transcript_manifest: dict) -> list[dict]:
    meta = case_payload.get("meta", {})
    evidence = [
        {
            "label": "Historical case meta",
            "detail": f"{clean_text(meta.get('title'))} | {clean_text(meta.get('duration'))} | {clean_text(meta.get('content_form'))}",
            "source": clean_text(meta.get("url")),
        },
        {
            "label": "Source manifest",
            "detail": f"download_backend={clean_text(source_manifest.get('download_backend'))}; status={clean_text(source_manifest.get('status'))}",
            "source": clean_text(source_manifest.get("agent_reach_manifest") or source_manifest.get("normalized_output_dir")),
        },
        {
            "label": "Transcript manifest",
            "detail": f"provider={clean_text(transcript_manifest.get('provider_used') or transcript_manifest.get('provider'))}",
            "source": clean_text(transcript_manifest.get("video")),
        },
    ]
    excerpt = pick_transcript_excerpt(transcript_manifest, limit=5)
    if excerpt:
        evidence.append(
            {
                "label": "Transcript excerpt",
                "detail": " || ".join(excerpt),
                "source": clean_text(transcript_manifest.get("video")),
            }
        )
    return evidence


def build_assets(case_json_path: Path, source_manifest: dict) -> list[dict]:
    base_dir = case_json_path.parent
    capture_dir = Path(clean_text(source_manifest.get("normalized_output_dir"))) if clean_text(source_manifest.get("normalized_output_dir")) else Path()
    assets: list[dict] = []
    contact_sheet = capture_dir / "frames_contact_sheet.jpg" if capture_dir else Path()
    if contact_sheet.exists():
        assets.append(
            {
                "label": "Frame contact sheet",
                "path": str(contact_sheet),
                "note": "Historical frame board from the evidence pack.",
            }
        )
    report_md = base_dir / "anxiansheng_curated_report_v3.md"
    if report_md.exists():
        assets.append(
            {
                "label": "Curated report markdown",
                "path": str(report_md),
                "note": "Prior human-readable report used as supporting evidence.",
            }
        )
    workbook = base_dir / "anxiansheng_curated_workbook_v3.xlsx"
    if workbook.exists():
        assets.append(
            {
                "label": "Curated workbook",
                "path": str(workbook),
                "note": "Prior workbook evidence bundle.",
            }
        )
    return assets


def fill_scene_04(payload: dict, case_payload: dict) -> None:
    executive = case_payload.get("executive", {})
    copy_risk = case_payload.get("copy_vs_risk", {})
    sections = {section["heading"]: section for section in payload["sections"]}

    sections["Executive Conclusion"]["paragraphs"] = [
        clean_text(executive.get("one_liner")),
        clean_text(executive.get("biggest_risk")),
    ]

    sections["Structure Logic"]["table"]["rows"] = [
        ["Hook", "Result-first promise of becoming known / mastering traffic logic", "Immediate stop-scroll through ambition and control", "0:00-0:06"],
        ["Setup", "Names the model and the nine keywords / three arbitrary conditions", "Frames the video as a full system instead of loose tips", "0:06-0:30"],
        ["Proof", "Alternates theory with examples, cases, and platform-native screenshots", "Builds trust and keeps abstract ideas grounded", "0:30-4:28"],
        ["Close / CTA", "Returns to interaction design as part of the process, not only the ending", "Converts understanding into save/comment/share impulse", "4:28-5:35"],
    ]

    sections["Core Mechanism"]["paragraphs"] = [
        "The video wins by selling control and framework clarity before it sells knowledge density.",
        "Its attention engine is layered naming plus continuous forward motion: each concept opens the next concept instead of concluding cleanly and stopping momentum.",
    ]
    sections["Core Mechanism"]["bullets"] = [
        "Attention tension: viewers feel there is a deeper rule still coming, so they continue watching.",
        "Proof logic: abstract claims are repeatedly anchored with examples, screenshots, and reusable named concepts.",
    ]

    sections["Reusable Formula"]["table"]["rows"] = summarize_core_variables(case_payload, limit=4)

    safer = "Keep the result-first hook and 3-5 named concepts, but reduce abstraction by inserting more obvious examples earlier."
    aggressive = "Preserve the same result promise and layered naming, but compress it into a shorter, sharper version built around one flagship insight."
    sections["Risks And Adaptation Notes"]["table"]["rows"] = [
        ["Safer", safer, "Drop some density and add clearer proof beats for broader viewers", "May lose some intellectual prestige but improves accessibility"],
        ["More aggressive", aggressive, "Push harder on ambition and judgment, with fewer but stronger concepts", "Easy to become empty slogan content without enough proof"],
    ]

    sections["Next Action"]["paragraphs"] = [
        "Rewrite one topic in your own lane using this sequence: result promise -> named framework -> example proof -> next-layer judgment.",
    ]
    sections["Next Action"]["numbered"] = [
        "Draft a 20-40 second opener that sells a larger outcome before any explanation.",
        "Choose 3-5 concepts worth naming so the viewer can retell the framework.",
        "Insert one case or screenshot every time the script becomes too abstract.",
    ]

    notes = payload.get("notes", [])
    notes.extend(clean_text(item) for item in copy_risk.get("risk", []) if clean_text(item))
    payload["notes"] = list(dict.fromkeys(notes))


def fill_scene_17(payload: dict, case_payload: dict) -> None:
    executive = case_payload.get("executive", {})
    amplifiers = list_of_dicts(case_payload, "amplifiers")
    surface_vs_core = list_of_dicts(case_payload, "surface_vs_core")
    sections = {section["heading"]: section for section in payload["sections"]}

    sections["Executive Conclusion"]["paragraphs"] = [
        clean_text(executive.get("one_liner")),
        f"Best for: {clean_text(executive.get('best_for'))}",
    ]

    rows = [
        ["Hook formula", "Result promise before theory", "Opening 'you can become known once in this era' promise"],
        ["Visual rhythm", "Talking head -> black-card keyword -> proof example", "Bookcase talking head plus black cards plus native screenshots"],
        ["Proof style", "Theory alternates with concrete cases", "Awakening-lion pastry case, Chongqing photo example, interaction examples"],
        ["CTA style", "Interaction is embedded in the logic, not only asked for at the end", "Explains why comments and likes must be triggered during the process"],
    ]
    sections["Structure Logic"]["table"]["rows"] = rows

    sections["Core Mechanism"]["paragraphs"] = [
        "The creator repeatedly turns ambiguous creator anxiety into named conceptual units that can be saved, retold, and applied.",
        "The repeatable advantage is not only clean speaking. It is a packaging system: ambition hook, conceptual naming, proof alternation, and forward-pulling structure.",
    ]

    sections["Reusable Formula"]["table"]["rows"] = [
        ["Hook", "Lead with a bigger result and sense of control", "Ambition and mastery transfer across niches", "Swap 'become known' for the most urgent outcome in the target lane"],
        ["Pacing", "Each segment opens the next one", "Forward pull works in any instructional content", "Design second and third hooks instead of one long explanation"],
        ["Trust-building", "Alternate theory with screenshots and cases", "Concrete proof stabilizes abstract claims", "Use native examples from the user's product or market"],
        ["Conversion move", "Seed save/comment/share reasons throughout", "Interaction is stronger when emotionally prepared earlier", "Plant one save-worthy frame and one question-worthy frame before the close"],
    ]

    creator_specific = []
    for item in surface_vs_core:
        label = clean_text(item.get("label"))
        if label in {"不可直接照抄", "表面现象"}:
            creator_specific.append([label, clean_text(item.get("detail"))])
    if not creator_specific:
        creator_specific = [
            ["Creator credibility", "Stable teacher-like delivery and existing trust do not transfer automatically."],
            ["Surface style", "Bookcase, black shirt, and black-card slides are not the real formula."],
        ]
    sections["Risks And Adaptation Notes"]["table"]["rows"] = creator_specific[:4]

    top_takeaways = executive.get("top_takeaways", [])
    sections["Next Action"]["paragraphs"] = [
        "Migrate the creator formula into your own lane by preserving the structure skeleton and replacing the creator shell.",
    ]
    sections["Next Action"]["numbered"] = [clean_text(item) for item in top_takeaways if clean_text(item)]

    payload["notes"] = list(dict.fromkeys(payload.get("notes", []) + [
        clean_text(item.get("detail")) for item in amplifiers if clean_text(item.get("detail"))
    ]))


def main() -> None:
    args = parse_args()
    case_json_path = Path(args.case_json).resolve()
    case_payload = load_json(str(case_json_path))
    source_manifest = load_json(args.source_manifest)
    transcript_manifest = load_json(args.transcript_manifest)

    skill_root = Path(__file__).resolve().parents[1]
    catalog = load_catalog(skill_root)
    scene = resolve_scene(catalog, args.scene)

    meta = case_payload.get("meta", {})
    default_project = f"{clean_text(meta.get('account'))} - {clean_text(meta.get('title'))}".strip(" -")
    project = clean_text(args.project) or default_project or "historical-case-import"
    context = make_context(case_payload, source_manifest, transcript_manifest)
    payload = build_report_payload(scene, project, context)

    fill_metadata(payload, case_payload, project)
    fill_working_context(payload, case_payload, source_manifest, transcript_manifest)
    fill_executive(payload, case_payload)
    payload["evidence"] = build_evidence(case_payload, source_manifest, transcript_manifest)
    payload["assets"] = build_assets(case_json_path, source_manifest)

    diagnostics_rows = summarize_diagnostics(case_payload, limit=6)
    if diagnostics_rows:
        payload["notes"] = list(dict.fromkeys(payload.get("notes", []) + [
            f"{row[0]}: {row[1]} | {row[3]}" for row in diagnostics_rows if row[0] and row[1]
        ]))

    beat_rows = summarize_story_beats(case_payload, limit=6)
    if beat_rows:
        payload["notes"] = list(dict.fromkeys(payload.get("notes", []) + [
            f"Story beat - {row[0]}: {row[1]} | {row[2]}" for row in beat_rows if row[0]
        ]))

    if scene["id"] == "04":
        fill_scene_04(payload, case_payload)
    elif scene["id"] == "17":
        fill_scene_17(payload, case_payload)

    payload["sources"] = list(dict.fromkeys([item for item in payload.get("sources", []) if item]))

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    write_json_file(output, payload)
    print(output)


if __name__ == "__main__":
    main()
