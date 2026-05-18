from __future__ import annotations

from datetime import datetime
from pathlib import Path

from pack_video_text import clean_text
from text_normalization import read_json_file, write_json_file

LIBRARY_FILENAME = "asset_library.json"


def library_path(capture_root: Path) -> Path:
    return capture_root / LIBRARY_FILENAME


def load_library(capture_root: Path) -> dict:
    path = library_path(capture_root)
    if path.exists():
        payload = read_json_file(path)
        if isinstance(payload, dict):
            return payload
    return {"schema_version": "asset-library-v1", "assets": [], "carry_forward": []}


def save_library(capture_root: Path, library: dict) -> Path:
    path = library_path(capture_root)
    write_json_file(path, library)
    return path


def _asset_entry(kind: str, label: str, path: str, note: str, *, scene_origin: str = "") -> dict:
    return {
        "kind": kind,
        "label": label,
        "path": path,
        "note": note,
        "scene_origin": scene_origin,
        "registered_at": datetime.now().isoformat(timespec="seconds"),
    }


def sync_asset_library(
    capture_root: Path,
    *,
    ranked_videos: list[dict],
    profile_summary: dict,
    report_assets: list[dict] | None = None,
    scene_id: str = "",
) -> dict:
    library = load_library(capture_root)
    seen = {clean_text(item.get("path")) for item in library.get("assets", []) if isinstance(item, dict)}

    profile_url = clean_text(profile_summary.get("profile_url") or profile_summary.get("profile_final_url"))
    if profile_url and profile_url not in seen:
        library.setdefault("assets", []).append(
            _asset_entry("profile", "Source profile", profile_url, "Account baseline", scene_origin=scene_id)
        )
        seen.add(profile_url)

    for index, video in enumerate(ranked_videos[:10], start=1):
        for key, kind in [
            ("video_url", "reference_video"),
            ("cover_url", "cover_image"),
            ("download_addr", "download_source"),
            ("play_addr", "play_source"),
        ]:
            value = clean_text(video.get(key))
            if value and value not in seen:
                library.setdefault("assets", []).append(
                    _asset_entry(
                        kind,
                        f"Ranked video {index} {kind}",
                        value,
                        clean_text(video.get("hook_text") or video.get("core_topic")) or "ranked reference",
                        scene_origin=scene_id,
                    )
                )
                seen.add(value)

    for item in report_assets or []:
        if not isinstance(item, dict):
            continue
        path = clean_text(item.get("path"))
        if path and path not in seen:
            library.setdefault("assets", []).append(
                _asset_entry(
                    "report_artifact",
                    clean_text(item.get("label")) or "report artifact",
                    path,
                    clean_text(item.get("note")),
                    scene_origin=scene_id,
                )
            )
            seen.add(path)

    for name in (
        "collection_board.json",
        "patrol_board.json",
        "competitor_weekly_board.json",
        "competitor_product_board.json",
        "category_entry_board.json",
        "comment_persona_board.json",
        "creator_formula_board.json",
        "account_retro_board.json",
        "production_spec_handoff.json",
        "scene03_creation_matrix.json",
        "competitor_product_board.json",
        "content_graph.json",
    ):
        path = capture_root / name
        if path.exists() and str(path) not in seen:
            library.setdefault("assets", []).append(
                _asset_entry("capture_artifact", name, str(path), "Reusable capture-pack artifact", scene_origin=scene_id)
            )
            seen.add(str(path))

    library["carry_forward"] = [
        "reference_video",
        "cover_image",
        "download_source",
        "production_spec_handoff",
        "collection_board",
    ]
    library["updated_at"] = datetime.now().isoformat(timespec="seconds")
    save_library(capture_root, library)
    return library


def merge_library_assets(payload: dict, capture_root: Path | None) -> None:
    if capture_root is None:
        return
    library = load_library(capture_root)
    if not library.get("assets"):
        return
    payload["asset_library"] = library
    existing = {clean_text(item.get("path")) for item in payload.get("assets", []) if isinstance(item, dict)}
    for item in library.get("assets", []):
        path = clean_text(item.get("path"))
        if path and path not in existing:
            payload.setdefault("assets", []).append(
                {
                    "label": f"[library] {clean_text(item.get('label'))}",
                    "path": path,
                    "note": clean_text(item.get("note")),
                }
            )
            existing.add(path)
