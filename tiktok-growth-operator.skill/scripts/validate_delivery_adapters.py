from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

from generate_scene_report import build_report_payload, load_catalog, render_markdown_from_payload, resolve_scene
from render_scene_report import write_docx, write_xlsx
from text_normalization import write_json_file, write_utf8_text


def skill_root() -> Path:
    return Path(__file__).resolve().parents[1]


def run(command: list[str]) -> dict:
    completed = subprocess.run(command, text=True, capture_output=True, encoding="utf-8", check=False)
    return {
        "command": command,
        "returncode": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }


def build_fixture_run(run_root: Path) -> Path:
    catalog = load_catalog(skill_root())
    scene = resolve_scene(catalog, "11")
    payload = build_report_payload(scene, "Delivery Adapter Validation", "Bounded validation fixture for local-bundle delivery.")
    report_json = run_root / "scene-11-delivery-validation.json"
    write_json_file(report_json, payload)
    outputs_dir = run_root / "outputs"
    outputs_dir.mkdir(parents=True, exist_ok=True)
    base_name = report_json.stem
    write_utf8_text(outputs_dir / f"{base_name}.md", render_markdown_from_payload(payload))
    write_docx(payload, outputs_dir / f"{base_name}.docx")
    write_xlsx(payload, outputs_dir / f"{base_name}.xlsx")
    write_json_file(
        run_root / "run_manifest.json",
        {
            "scene_id": scene["id"],
            "scene_slug": scene["slug"],
            "report_json": str(report_json),
            "operator_packs": [],
        },
    )
    return report_json


def main() -> None:
    scripts_root = skill_root() / "scripts"
    with tempfile.TemporaryDirectory(prefix="tgo-validate-delivery-") as temp_dir:
        run_root = Path(temp_dir) / "scene-11-run"
        run_root.mkdir(parents=True, exist_ok=True)
        build_fixture_run(run_root)

        dry_run = run(
            [
                sys.executable,
                str(scripts_root / "deliver_operator_run.py"),
                "--run-root",
                str(run_root),
                "--targets",
                "local-bundle",
                "--dry-run",
            ]
        )
        if dry_run["returncode"] != 0:
            print(json.dumps({"success": False, "results": [dry_run]}, ensure_ascii=False, indent=2))
            raise SystemExit(1)
        dry_payload = json.loads(dry_run["stdout"])
        planned = dry_payload.get("local_bundle", {}).get("files", [])
        if len(planned) < 4:
            dry_run["returncode"] = 1
            dry_run["stderr"] = "dry-run should plan report json plus rendered outputs"
            print(json.dumps({"success": False, "results": [dry_run]}, ensure_ascii=False, indent=2))
            raise SystemExit(1)

        delivery_root = run_root / "delivery"
        deliver = run(
            [
                sys.executable,
                str(scripts_root / "deliver_operator_run.py"),
                "--run-root",
                str(run_root),
                "--delivery-root",
                str(delivery_root),
                "--targets",
                "local-bundle",
            ]
        )
        if deliver["returncode"] != 0:
            print(json.dumps({"success": False, "results": [dry_run, deliver]}, ensure_ascii=False, indent=2))
            raise SystemExit(1)
        manifest_path = delivery_root / "delivery_manifest.json"
        if not manifest_path.exists():
            deliver["returncode"] = 1
            deliver["stderr"] = "delivery_manifest.json was not created"
            print(json.dumps({"success": False, "results": [dry_run, deliver]}, ensure_ascii=False, indent=2))
            raise SystemExit(1)

        feishu_skip = run(
            [
                sys.executable,
                str(scripts_root / "deliver_operator_run.py"),
                "--run-root",
                str(run_root),
                "--targets",
                "feishu",
            ]
        )
        if feishu_skip["returncode"] != 0:
            print(json.dumps({"success": False, "results": [dry_run, deliver, feishu_skip]}, ensure_ascii=False, indent=2))
            raise SystemExit(1)
        feishu_payload = json.loads(feishu_skip["stdout"])
        if feishu_payload.get("feishu", {}).get("status") != "skipped":
            feishu_skip["returncode"] = 1
            feishu_skip["stderr"] = "feishu target without credentials should skip cleanly"
            print(json.dumps({"success": False, "results": [dry_run, deliver, feishu_skip]}, ensure_ascii=False, indent=2))
            raise SystemExit(1)

    print(json.dumps({"success": True, "results": [dry_run, deliver, feishu_skip]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
