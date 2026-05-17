from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

from feishu_naming import scene_label_zh
from feishu_push_runtime import maybe_push_feishu_bundle
from generate_operator_pack import generate_pack_output
from generate_scene_report import build_report_payload, load_catalog, resolve_scene
from render_scene_report import infer_base_name, render_markdown_from_payload, write_docx, write_xlsx
from text_normalization import read_utf8_text, write_json_file, write_utf8_text


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Bootstrap one TikTok Growth Operator scene run with workspace folders, structured report scaffold, starter deliverables, and optional operator packs."
    )
    parser.add_argument("--scene", required=True, help="Scene id or slug.")
    parser.add_argument("--name", required=True, help="Short run name, e.g. lip-combo-us.")
    parser.add_argument("--project", default="", help="Optional project title. Defaults to the run name.")
    parser.add_argument("--context-file", help="Optional UTF-8 brief file.")
    parser.add_argument(
        "--output-root",
        default="",
        help="Optional explicit run root. Defaults to <skill>/tmp/<timestamp>-scene-<id>-<name>.",
    )
    parser.add_argument(
        "--formats",
        default="md,docx,xlsx",
        help="Comma-separated starter deliverable formats: md, docx, xlsx.",
    )
    parser.add_argument(
        "--operator-packs",
        default="",
        help="Optional comma-separated operator packs to generate: publish-prep, live-assist, creative-production-handoff, account-ops-assist.",
    )
    parser.add_argument("--platform", default="Douyin", help="Platform label for derived operator packs.")
    parser.add_argument("--market", default="China", help="Target market label for derived operator packs.")
    parser.add_argument("--push-feishu", action="store_true", help="After generating the run, also push the report to Feishu.")
    parser.add_argument("--feishu-app-id", default="", help="Optional explicit Feishu app ID.")
    parser.add_argument("--feishu-app-secret", default="", help="Optional explicit Feishu app secret.")
    parser.add_argument("--feishu-title", default="", help="Optional explicit Feishu Doc title.")
    parser.add_argument("--feishu-base-name", default="", help="Optional explicit Feishu Bitable app name.")
    return parser.parse_args()


def create_run_root(skill_root: Path, scene: dict, run_name: str, output_root: str) -> Path:
    if output_root.strip():
        return Path(output_root).expanduser().resolve()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return skill_root / "tmp" / f"{timestamp}-scene-{scene['id']}-{run_name}"


def parse_operator_packs(raw: str) -> list[str]:
    allowed = {"publish-prep", "live-assist", "creative-production-handoff", "account-ops-assist"}
    values = [item.strip().lower() for item in raw.split(",") if item.strip()]
    invalid = [item for item in values if item not in allowed]
    if invalid:
        raise SystemExit(f"Unsupported operator pack(s): {', '.join(invalid)}")
    deduped: list[str] = []
    for item in values:
        if item not in deduped:
            deduped.append(item)
    return deduped


def default_operator_packs(scene_id: str) -> list[str]:
    if scene_id in {"09", "10", "11", "12", "13", "14", "15", "16"}:
        return ["publish-prep", "creative-production-handoff"]
    if scene_id in {"08", "18", "19"}:
        return ["live-assist"]
    return []


def write_manifest(
    run_root: Path,
    scene: dict,
    report_path: Path,
    operator_pack_results: list[dict],
) -> None:
    write_json_file(
        run_root / "run_manifest.json",
        {
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "scene_id": scene["id"],
            "scene_slug": scene["slug"],
            "scene_title": scene_label_zh(scene["id"]) or scene["title"],
            "scene_summary": scene["summary"],
            "deliverable_type": scene["deliverable_type"],
            "scenario_file": scene["scenario_file"],
            "report_json": str(report_path),
            "operator_packs": operator_pack_results,
        },
    )


def write_readme(run_root: Path, scene: dict, report_path: Path, operator_pack_results: list[dict]) -> None:
    scene_display_title = scene_label_zh(scene["id"]) or scene["title"]
    content = f"""# Scene 运行工作区

## 场景信息

- 场景编号：{scene["id"]}
- 场景标识：{scene["slug"]}
- 场景标题：{scene_display_title}
- 交付类型：{scene["deliverable_type"]}

## 文件夹用途

- `inputs/`：用户简报、产品信息、关键词列表、账号列表
- `evidence/`：链接、截图、导出文件、转写、补充笔记
- `outputs/`：渲染后的报告成品
- `notes/`：推理笔记、开放问题、复核备注
- `operator-packs/`：派生交付包，如 `publish-prep`、`live-assist`、`creative-production-handoff`

## 主文件

- 报告 JSON：`{report_path.name}`
- 场景剧本：`{scene["scenario_file"]}`
"""
    if operator_pack_results:
        content += "\n## 已生成的 Operator 交付包\n\n"
        for item in operator_pack_results:
            content += f"- {item['type']}: `{Path(item['output_path']).name}`\n"
    content += """

## 建议流程

1. 先把 brief 与原始素材放进 `inputs/` 和 `evidence/`。
2. 用真实结论与真实证据补全报告 JSON。
3. 通过 `scripts/render_scene_report.py` 重新渲染成品输出。
4. 如果已经生成 operator 交付包，再基于完整场景报告补强这些 handoff 包。
"""
    write_utf8_text(run_root / "README.md", content)


def main() -> None:
    args = parse_args()
    skill_root = Path(__file__).resolve().parents[1]
    catalog = load_catalog(skill_root)
    scene = resolve_scene(catalog, args.scene)
    run_name = args.name.strip()
    project = args.project.strip() or run_name
    context = read_utf8_text(Path(args.context_file)) if args.context_file else ""

    run_root = create_run_root(skill_root, scene, run_name, args.output_root)
    for relative in ["inputs", "evidence", "outputs", "notes", "operator-packs"]:
        (run_root / relative).mkdir(parents=True, exist_ok=True)

    payload = build_report_payload(scene, project, context)
    base_name = infer_base_name(payload, "")
    report_json_path = run_root / f"{base_name}.json"
    write_json_file(report_json_path, payload)

    formats = [item.strip().lower() for item in args.formats.split(",") if item.strip()]
    outputs_dir = run_root / "outputs"
    if "md" in formats:
        write_utf8_text(outputs_dir / f"{base_name}.md", render_markdown_from_payload(payload))
    if "docx" in formats:
        write_docx(payload, outputs_dir / f"{base_name}.docx")
    if "xlsx" in formats:
        write_xlsx(payload, outputs_dir / f"{base_name}.xlsx")

    requested_packs = parse_operator_packs(args.operator_packs) if args.operator_packs.strip() else default_operator_packs(scene["id"])
    operator_pack_results: list[dict] = []
    for pack_type in requested_packs:
        pack_output_dir = run_root / "operator-packs" / pack_type
        operator_pack_results.append(
            generate_pack_output(
                pack_type=pack_type,
                output_dir=pack_output_dir,
                project=project,
                platform=args.platform,
                market=args.market,
                context=context,
                source_report_path=report_json_path,
            )
        )

    write_manifest(run_root, scene, report_json_path, operator_pack_results)
    write_readme(run_root, scene, report_json_path, operator_pack_results)

    result = {
        "run_root": str(run_root),
        "report_json": str(report_json_path),
        "outputs_dir": str(outputs_dir),
        "operator_packs": operator_pack_results,
    }
    if args.push_feishu:
        result["feishu_push"] = maybe_push_feishu_bundle(
            str(report_json_path),
            args.feishu_app_id,
            args.feishu_app_secret,
            title=args.feishu_title.strip() or project,
            base_name=args.feishu_base_name.strip() or project,
        )

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
