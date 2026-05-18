from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime
from pathlib import Path

from feishu_delivery_helpers import deliver_feishu_report, resolve_feishu_registry_for_report
from text_normalization import normalize_text, read_json_file, write_json_file


ALLOWED_TARGETS = {"local-bundle", "feishu"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Deliver one TikTok Growth Operator scene run to local bundle and/or Feishu surfaces."
    )
    parser.add_argument("--run-root", default="", help="Scene run root containing run_manifest.json.")
    parser.add_argument("--report-json", default="", help="Optional explicit scene report JSON when run_root is omitted.")
    parser.add_argument(
        "--delivery-root",
        default="",
        help="Output directory for local-bundle delivery. Defaults to <run-root>/delivery when run_root is set.",
    )
    parser.add_argument(
        "--targets",
        default="local-bundle",
        help="Comma-separated delivery targets: local-bundle, feishu.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Plan delivery without writing files or calling Feishu.")
    parser.add_argument("--feishu-app-id", default="", help="Feishu app ID for feishu target.")
    parser.add_argument("--feishu-app-secret", default="", help="Feishu app secret for feishu target.")
    parser.add_argument("--feishu-title", default="", help="Optional Feishu Doc title.")
    parser.add_argument("--feishu-base-name", default="", help="Optional Feishu Bitable app name.")
    parser.add_argument(
        "--feishu-append-board",
        action="store_true",
        help="Append structured board rows (collection_board, patrol_board, …) to fixed-header Feishu Bitable tables.",
    )
    parser.add_argument("--feishu-run-date", default="", help="Optional YYYY-MM-DD stamp for board append rows.")
    parser.add_argument("--feishu-append-scope", default="", help="Optional append batch key (defaults to run date).")
    parser.add_argument(
        "--feishu-registry",
        default="",
        help="Optional feishu_delivery_registry.json path. Defaults next to capture root inferred from report assets.",
    )
    return parser.parse_args()


def parse_targets(raw: str) -> list[str]:
    targets = [normalize_text(item).lower() for item in raw.split(",") if normalize_text(item)]
    invalid = [item for item in targets if item not in ALLOWED_TARGETS]
    if invalid:
        raise SystemExit(f"Unsupported delivery target(s): {', '.join(invalid)}")
    if not targets:
        raise SystemExit("At least one delivery target is required.")
    return targets


def load_run_context(run_root: Path | None, report_json: str) -> dict:
    manifest_path = run_root / "run_manifest.json" if run_root else None
    manifest = read_json_file(manifest_path) if manifest_path and manifest_path.exists() else {}
    resolved_report = normalize_text(report_json) or normalize_text(manifest.get("report_json", ""))
    if not resolved_report:
        raise SystemExit("Missing report JSON. Provide --report-json or a run_root with run_manifest.json.")
    report_path = Path(resolved_report)
    if not report_path.exists():
        raise SystemExit(f"Report JSON not found: {report_path}")
    base_name = report_path.stem
    outputs_dir = (run_root / "outputs") if run_root else report_path.parent
    operator_packs_dir = (run_root / "operator-packs") if run_root else None
    return {
        "run_root": str(run_root) if run_root else "",
        "manifest": manifest,
        "report_json": str(report_path),
        "base_name": base_name,
        "outputs_dir": outputs_dir,
        "operator_packs_dir": operator_packs_dir,
    }


def discover_artifacts(context: dict) -> list[dict]:
    artifacts: list[dict] = [{"kind": "report-json", "path": context["report_json"]}]
    outputs_dir: Path = context["outputs_dir"]
    base_name = context["base_name"]
    for suffix, kind in [(".md", "report-md"), (".docx", "report-docx"), (".xlsx", "report-xlsx")]:
        candidate = outputs_dir / f"{base_name}{suffix}"
        if candidate.exists():
            artifacts.append({"kind": kind, "path": str(candidate)})
    operator_packs_dir = context.get("operator_packs_dir")
    if isinstance(operator_packs_dir, Path) and operator_packs_dir.exists():
        for pack_dir in sorted(operator_packs_dir.iterdir()):
            if not pack_dir.is_dir():
                continue
            for path in sorted(pack_dir.rglob("*")):
                if path.is_file():
                    artifacts.append(
                        {
                            "kind": f"operator-pack:{pack_dir.name}",
                            "path": str(path),
                        }
                    )
    manifest = context.get("manifest") or {}
    if context.get("run_root"):
        manifest_path = Path(context["run_root"]) / "run_manifest.json"
        if manifest_path.exists():
            artifacts.append({"kind": "run-manifest", "path": str(manifest_path)})
    readme_path = Path(context["run_root"]) / "README.md" if context.get("run_root") else None
    if readme_path and readme_path.exists():
        artifacts.append({"kind": "run-readme", "path": str(readme_path)})
    return artifacts


def deliver_local_bundle(context: dict, delivery_root: Path, dry_run: bool) -> dict:
    artifacts = discover_artifacts(context)
    planned_files: list[dict] = []
    for artifact in artifacts:
        source = Path(artifact["path"])
        relative = source.name
        if artifact["kind"].startswith("operator-pack:"):
            pack_name = artifact["kind"].split(":", 1)[1]
            pack_root = context["operator_packs_dir"] / pack_name
            relative = str(Path("operator-packs") / pack_name / source.relative_to(pack_root))
        elif artifact["kind"] == "run-manifest":
            relative = "run_manifest.json"
        elif artifact["kind"] == "run-readme":
            relative = "README.md"
        elif artifact["kind"].startswith("report-"):
            relative = str(Path("outputs") / source.name)
        elif artifact["kind"] == "report-json":
            relative = source.name
        destination = delivery_root / relative
        planned_files.append(
            {
                "kind": artifact["kind"],
                "source": str(source),
                "destination": str(destination),
            }
        )
        if not dry_run:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)

    delivery_manifest = {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "targets": ["local-bundle"],
        "dry_run": dry_run,
        "run_root": context.get("run_root", ""),
        "report_json": context["report_json"],
        "delivery_root": str(delivery_root),
        "files": planned_files,
        "scene_id": (context.get("manifest") or {}).get("scene_id", ""),
        "operator_packs": (context.get("manifest") or {}).get("operator_packs", []),
    }
    if not dry_run:
        write_json_file(delivery_root / "delivery_manifest.json", delivery_manifest)
    return delivery_manifest


def resolve_feishu_registry_path(context: dict, args: argparse.Namespace) -> Path:
    if normalize_text(args.feishu_registry):
        return Path(args.feishu_registry).expanduser().resolve()
    return resolve_feishu_registry_for_report(context["report_json"])


def deliver_feishu(context: dict, args: argparse.Namespace, dry_run: bool) -> dict:
    return deliver_feishu_report(
        context["report_json"],
        args.feishu_app_id,
        args.feishu_app_secret,
        title=args.feishu_title.strip(),
        base_name=args.feishu_base_name.strip(),
        append_board=bool(args.feishu_append_board),
        run_date=normalize_text(args.feishu_run_date),
        append_scope=normalize_text(args.feishu_append_scope),
        registry_file=resolve_feishu_registry_path(context, args),
        dry_run=dry_run,
    )


def main() -> None:
    args = parse_args()
    targets = parse_targets(args.targets)
    run_root = Path(args.run_root) if normalize_text(args.run_root) else None
    if run_root and not run_root.exists():
        raise SystemExit(f"Run root not found: {run_root}")
    context = load_run_context(run_root, args.report_json)
    delivery_root = Path(args.delivery_root) if normalize_text(args.delivery_root) else (
        (run_root / "delivery") if run_root else Path(context["report_json"]).parent / "delivery"
    )

    results: dict[str, object] = {
        "targets": targets,
        "dry_run": args.dry_run,
        "report_json": context["report_json"],
        "run_root": context.get("run_root", ""),
    }
    if "local-bundle" in targets:
        results["local_bundle"] = deliver_local_bundle(context, delivery_root, args.dry_run)
    if "feishu" in targets:
        results["feishu"] = deliver_feishu(context, args, args.dry_run)
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
