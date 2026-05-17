from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from start_capture_pack_run import create_capture_pack_run
from text_normalization import normalize_nested, normalize_text, read_json_file, write_json_file, write_utf8_text


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Collect one real TikTok video via TikMatrix, build a local single-video capture-pack, and run Scene 04 or 05 end to end."
    )
    parser.add_argument("--url", required=True, help="TikTok video URL.")
    parser.add_argument("--collect-json", default="", help="Optional existing TikMatrix single-video JSON fixture path.")
    parser.add_argument("--scene", default="04", choices=["04", "05"], help="Single-video operator scene to run.")
    parser.add_argument("--name", required=True, help="Short operator run name.")
    parser.add_argument("--project", required=True, help="Operator project title.")
    parser.add_argument("--output-root", default="", help="Optional explicit runtime root.")
    parser.add_argument("--platform", default="TikTok", help="Platform label for operator outputs.")
    parser.add_argument("--market", default="US", help="Market label for operator outputs.")
    parser.add_argument("--formats", default="md,docx,xlsx", help="Rendered output formats.")
    parser.add_argument(
        "--tikmatrix-python",
        default=r"E:\tiktok\TikMatrix\.venv\Scripts\python.exe",
        help="TikMatrix Python executable.",
    )
    parser.add_argument(
        "--tikmatrix-runner",
        default=r"E:\tiktok\TikMatrix\scripts\run_from_skill.py",
        help="TikMatrix run_from_skill.py path.",
    )
    parser.add_argument(
        "--download-video",
        action="store_true",
        help="Also run TikMatrix video-download so the pack keeps local media paths when available.",
    )
    return parser.parse_args()


def ensure_runtime_root(skill_root: Path, output_root: str, run_name: str) -> Path:
    if output_root.strip():
        root = Path(output_root).expanduser().resolve()
    else:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        root = skill_root / "tmp" / f"{stamp}-single-video-scene-{run_name}"
    root.mkdir(parents=True, exist_ok=True)
    return root


def run_json_command(command: list[str]) -> tuple[dict | list, subprocess.CompletedProcess[str]]:
    completed = subprocess.run(command, text=True, capture_output=True, check=True)
    payload = json.loads(normalize_text(completed.stdout, strip=False))
    return payload, completed


def build_single_video_capture_pack(
    *,
    capture_root: Path,
    collect_payload: dict,
    source_url: str,
    download_payload: dict | None,
) -> dict:
    video_id = normalize_text(collect_payload.get("video_id"))
    title = normalize_text(collect_payload.get("title"))
    author = collect_payload.get("author") or {}
    stats = collect_payload.get("stats") or {}
    media = collect_payload.get("media") or {}
    raw = collect_payload.get("raw") or {}
    music_title = normalize_text(collect_payload.get("music_title"))
    hashtags = [
        normalize_text(item.get("title"))
        for item in (raw.get("challenges") or [])
        if isinstance(item, dict) and normalize_text(item.get("title"))
    ]
    core_topic = title.split("#", 1)[0].strip() if title else ""
    if not core_topic and hashtags:
        core_topic = ", ".join(f"#{tag}" for tag in hashtags[:4])
    hook_text = title.split(".", 1)[0].strip() if title else core_topic

    ranked_video = normalize_nested(
        {
            "profile_url": source_url.rsplit("/video/", 1)[0] if "/video/" in source_url else source_url,
            "profile_index": 1,
            "profile_output_dir": str(capture_root),
            "video_url": source_url,
            "video_id": video_id,
            "unique_id": normalize_text(author.get("unique_id") or author.get("uniqueId")),
            "nickname": normalize_text(author.get("nickname")),
            "desc": title,
            "caption_text": title,
            "hook_text": hook_text,
            "core_topic": core_topic or title,
            "created_at_utc": normalize_text(collect_payload.get("create_time")),
            "digg_count": int(stats.get("digg_count") or 0),
            "comment_count": int(stats.get("comment_count") or 0),
            "collect_count": int((raw.get("stats") or {}).get("collectCount") or 0),
            "share_count": int(stats.get("share_count") or 0),
            "play_count": int(stats.get("play_count") or 0),
            "play_addr": normalize_text(media.get("url")),
            "download_addr": normalize_text(media.get("url")),
            "cover_url": normalize_text(media.get("cover")),
            "score": int(stats.get("digg_count") or 0) + int(stats.get("comment_count") or 0) * 20,
            "source": "tikmatrix_single_video_collect",
            "hashtags": hashtags,
            "author_signature": normalize_text(author.get("signature")),
            "author_verified": bool(author.get("verified")),
            "music_title": music_title,
        }
    )
    if download_payload:
        ranked_video["downloaded_metadata_path"] = str(capture_root / f"{video_id}.json")
        ranked_video["downloaded_media_path"] = str(capture_root / f"{video_id}.mp4")

    qualified_videos = [ranked_video]
    timestamp = datetime.now().astimezone().isoformat(timespec="seconds")
    summary = {
        "checked_at": timestamp,
        "platform": "tiktok",
        "reachable": True,
        "session_quality": "tikmatrix_single_video_collect",
        "base_status_code": 200,
        "profile_status_code": 200,
        "profile_final_url": source_url,
        "detail_collected_count": 1,
        "ranked_video_count": 1,
        "qualified_video_count": 1,
        "notes": [
            "Built from one real TikMatrix video-collect result.",
            "This pack is intended for single-video Scene 04/05 breakdown flows.",
        ],
    }
    aggregate_summary = {
        "started_at": timestamp,
        "ended_at": timestamp,
        "profile_count": 1,
        "aggregated_ranked_count": 1,
        "aggregated_qualified_count": 1,
        "min_likes": 0,
        "output_root": str(capture_root),
        "profile_summary_json": str(capture_root / "profile_summary.json"),
        "ranked_json": str(capture_root / "aggregate_ranked_videos.json"),
        "qualified_json": str(capture_root / "aggregate_qualified_videos.json"),
        "single_video_mode": True,
    }
    profile_summary = {
        "profile_url": ranked_video["profile_url"],
        "output_dir": str(capture_root),
        "exit_code": 0,
        "reachable": True,
        "session_quality": "tikmatrix_single_video_collect",
        "link_count": 1,
        "detail_collected_count": 1,
        "ranked_video_count": 1,
        "qualified_video_count": 1,
        "api_item_count": 1,
        "browser_api_item_count": 1,
        "comment_sampled_video_count": 0,
        "video_download_success_count": 1 if download_payload else 0,
        "cover_download_success_count": None,
        "checked_at": timestamp,
    }

    write_json_file(capture_root / "summary.json", summary)
    write_json_file(capture_root / "profile_summary.json", profile_summary)
    write_json_file(capture_root / "aggregate_summary.json", aggregate_summary)
    write_json_file(capture_root / "ranked_videos.json", [ranked_video])
    write_json_file(capture_root / "aggregate_ranked_videos.json", [ranked_video])
    write_json_file(capture_root / "aggregate_qualified_videos.json", qualified_videos)
    write_json_file(
        capture_root / "video_details.json",
        {
            "videos": [ranked_video],
            "source_video_collect_url": source_url,
        },
    )
    write_utf8_text(capture_root / "aggregate_ranked_links.txt", f"{source_url}\n")
    write_utf8_text(capture_root / "qualified_video_links.txt", f"{source_url}\n")
    write_json_file(
        capture_root / "source_manifest.json",
        {
            "created_at": timestamp,
            "source_url": source_url,
            "video_id": video_id,
            "video_collect_mode": True,
            "downloaded": bool(download_payload),
        },
    )
    write_utf8_text(
        capture_root / "aggregate_report.md",
        "\n".join(
            [
                "# TikMatrix Single Video Capture Pack",
                "",
                f"- source video: `{source_url}`",
                f"- video id: `{video_id}`",
                f"- title: `{title}`",
                f"- author: `{normalize_text(author.get('nickname') or author.get('unique_id') or author.get('uniqueId'))}`",
                f"- download attached: `{bool(download_payload)}`",
            ]
        )
        + "\n",
    )
    return ranked_video


def main() -> None:
    args = parse_args()
    skill_root = Path(__file__).resolve().parents[1]
    runtime_root = ensure_runtime_root(skill_root, args.output_root, args.name.strip())
    collect_root = runtime_root / "tikmatrix-collect"
    download_root = runtime_root / "tikmatrix-download"
    capture_root = runtime_root / "capture-pack"
    collect_root.mkdir(parents=True, exist_ok=True)
    capture_root.mkdir(parents=True, exist_ok=True)

    tikmatrix_python = Path(args.tikmatrix_python).expanduser()
    tikmatrix_runner = Path(args.tikmatrix_runner).expanduser()
    using_fixture = bool(args.collect_json.strip())
    if not using_fixture and not tikmatrix_python.exists():
        raise SystemExit(f"Missing TikMatrix Python: {tikmatrix_python}")
    if not tikmatrix_runner.exists():
        raise SystemExit(f"Missing TikMatrix runner: {tikmatrix_runner}")

    collect_command: list[str] = []
    collect_stdout = ""
    if using_fixture:
        collect_fixture = Path(args.collect_json).expanduser().resolve()
        if not collect_fixture.exists():
            raise SystemExit(f"Missing --collect-json fixture: {collect_fixture}")
        collect_payload_raw = read_json_file(collect_fixture)
        if not isinstance(collect_payload_raw, dict):
            raise SystemExit("--collect-json must point to a JSON object.")
        collect_payload = normalize_nested(collect_payload_raw)
        collect_command = ["fixture", str(collect_fixture)]
        collect_stdout = str(collect_fixture)
    else:
        collect_command = [
            str(tikmatrix_python),
            str(tikmatrix_runner),
            "video-collect",
            "--url",
            args.url,
        ]
        collect_payload_raw, collect_completed = run_json_command(collect_command)
        if not isinstance(collect_payload_raw, dict):
            raise SystemExit("TikMatrix video-collect did not return a JSON object.")
        collect_payload = normalize_nested(collect_payload_raw)
        collect_stdout = collect_completed.stdout.strip()
    video_id = normalize_text(collect_payload.get("video_id"))
    if not video_id:
        raise SystemExit("TikMatrix single-video source did not return a video_id.")
    write_json_file(collect_root / f"{video_id}.json", collect_payload)
    write_json_file(collect_root / "video_collect.json", collect_payload)

    download_payload: dict | None = None
    if args.download_video:
        download_root.mkdir(parents=True, exist_ok=True)
        download_command = [
            str(tikmatrix_python),
            str(tikmatrix_runner),
            "video-download",
            "--url",
            args.url,
            "--output-dir",
            str(download_root),
        ]
        download_payload_raw, download_completed = run_json_command(download_command)
        if isinstance(download_payload_raw, dict):
            download_payload = normalize_nested(download_payload_raw)
            write_json_file(download_root / "video_download.json", download_payload)
        else:
            raise SystemExit("TikMatrix video-download did not return a JSON object.")
        downloaded_metadata = download_root / f"{video_id}.json"
        if downloaded_metadata.exists():
            write_json_file(capture_root / f"{video_id}.json", read_json_file(downloaded_metadata))
        downloaded_mp4 = download_root / f"{video_id}.mp4"
        if downloaded_mp4.exists():
            write_utf8_text(capture_root / "downloaded_asset_path.txt", str(downloaded_mp4) + "\n")
        download_stdout = download_completed.stdout.strip()
    else:
        download_stdout = ""

    ranked_video = build_single_video_capture_pack(
        capture_root=capture_root,
        collect_payload=collect_payload,
        source_url=args.url,
        download_payload=download_payload,
    )
    operator_result = create_capture_pack_run(
        scene=args.scene,
        capture_root_raw=str(capture_root),
        name=args.name,
        project=args.project,
        output_root=str(runtime_root / "operator-run"),
        platform=args.platform,
        market=args.market,
        formats=args.formats,
        operator_packs_raw="",
    )
    write_json_file(
        runtime_root / "single_video_runtime_manifest.json",
        {
            "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
            "source_url": args.url,
            "scene": args.scene,
            "ranked_video": ranked_video,
            "collect_command": collect_command,
            "collect_stdout": collect_stdout,
            "download_stdout": download_stdout,
            "downloaded": bool(download_payload),
            "capture_root": str(capture_root),
            "operator_run_root": operator_result.get("run_root", ""),
        },
    )
    print(
        json.dumps(
            {
                "capture_root": str(capture_root),
                "tikmatrix_collect_root": str(collect_root),
                "operator_run": operator_result,
                "downloaded": bool(download_payload),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
