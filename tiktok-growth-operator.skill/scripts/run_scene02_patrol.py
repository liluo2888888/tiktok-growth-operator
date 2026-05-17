from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from start_capture_pack_run import create_capture_pack_run
from text_normalization import normalize_nested, normalize_text, read_json_file, write_json_file, write_utf8_text


TIKMATRIX_RUNNER = Path(r"E:\tiktok\TikMatrix\scripts\run_from_skill.py")
DEFAULT_TIKMATRIX_OUTPUT = Path(r"E:\tiktok\TikMatrix\tmp")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run Scene 02 as a real TikMatrix-backed category patrol with snapshot persistence, delta detection, and Scene 03 handoff candidates."
    )
    parser.add_argument("--name", required=True, help="Short patrol run name.")
    parser.add_argument("--project", required=True, help="Patrol project title.")
    parser.add_argument("--category", required=True, help="Category label for the patrol.")
    parser.add_argument("--market", default="US", help="Primary market label.")
    parser.add_argument("--cadence", default="daily", help="Patrol cadence label.")
    parser.add_argument("--mode", default="mixed", choices=["search", "topic", "mixed"], help="Patrol source mode.")
    parser.add_argument("--queries", default="", help="Comma-separated search queries.")
    parser.add_argument("--topics", default="", help="Comma-separated topic tags without #.")
    parser.add_argument("--count", type=int, default=10, help="Requested TikMatrix item count per source.")
    parser.add_argument("--download-top", type=int, default=3, help="Download and enrich the top N videos per source.")
    parser.add_argument("--min-likes", type=int, default=1000, help="Minimum likes threshold for Scene 03 candidate bias.")
    parser.add_argument("--alert-like-jump", type=int, default=500, help="Minimum like delta for breakout alerting.")
    parser.add_argument("--alert-score-jump", type=int, default=1200, help="Minimum score delta for breakout alerting.")
    parser.add_argument("--shortlist-count", type=int, default=5, help="Maximum Scene 02 ranked shortlist size.")
    parser.add_argument("--scene03-count", type=int, default=3, help="Maximum Scene 03 handoff candidate count.")
    parser.add_argument("--query-root", default="", help="Optional existing TikMatrix search export root to import instead of collecting.")
    parser.add_argument("--topic-root", default="", help="Optional existing TikMatrix topic export root to import instead of collecting.")
    parser.add_argument("--output-root", default="", help="Optional explicit output root.")
    parser.add_argument("--tikmatrix-output-root", default="", help="Optional explicit TikMatrix tmp root for live collection outputs.")
    parser.add_argument("--formats", default="md,docx,xlsx", help="Rendered Scene 02 output formats.")
    parser.add_argument("--operator-packs", default="", help="Optional operator-pack override for the downstream scene run.")
    parser.add_argument("--skip-live", action="store_true", help="Use only supplied query/topic roots and do not call TikMatrix.")
    parser.add_argument("--also-run-scene03", action="store_true", help="Also generate a downstream Scene 03 run from the derived Scene 03 candidate pack.")
    return parser.parse_args()


def clean_text(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        return ", ".join(item for item in (clean_text(part) for part in value) if item)
    if isinstance(value, dict):
        return json.dumps(normalize_nested(value), ensure_ascii=False)
    return normalize_text(value)


def safe_int(value: object) -> int:
    if isinstance(value, bool):
        return int(value)
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def split_csv(raw: str) -> list[str]:
    deduped: list[str] = []
    for item in raw.split(","):
        text = normalize_text(item)
        if text and text not in deduped:
            deduped.append(text)
    return deduped


def slugify(value: str) -> str:
    cleaned = "".join(ch.lower() if ch.isalnum() else "-" for ch in normalize_text(value))
    while "--" in cleaned:
        cleaned = cleaned.replace("--", "-")
    return cleaned.strip("-")


def timestamp_slug() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def ensure_root(output_root: str, skill_root: Path, name: str) -> Path:
    if output_root.strip():
        root = Path(output_root).expanduser().resolve()
    else:
        root = skill_root / "tmp" / f"{timestamp_slug()}-scene02-patrol-{slugify(name) or 'run'}"
    root.mkdir(parents=True, exist_ok=True)
    return root


def ensure_state_root(skill_root: Path, project: str, category: str, market: str) -> Path:
    key = slugify(f"{project}-{category}-{market}") or "scene02-patrol"
    root = skill_root / "tmp" / "scene02-state" / key
    root.mkdir(parents=True, exist_ok=True)
    return root


def run_tikmatrix(workflow: str, url: str, count: int, output_dir: Path) -> None:
    if not TIKMATRIX_RUNNER.exists():
        raise SystemExit(f"TikMatrix runner not found: {TIKMATRIX_RUNNER}")
    output_dir.mkdir(parents=True, exist_ok=True)
    completed = subprocess.run(
        [
            sys.executable,
            str(TIKMATRIX_RUNNER),
            workflow,
            "--url",
            url,
            "--count",
            str(count),
            "--output-dir",
            str(output_dir),
            "--duplicate-policy",
            "overwrite",
            "--retries",
            "1",
        ],
        text=True,
        capture_output=True,
    )
    if completed.returncode != 0:
        raise SystemExit(
            f"TikMatrix workflow failed: {workflow} {url}\nSTDOUT:\n{completed.stdout}\nSTDERR:\n{completed.stderr}"
        )


def load_json(path: Path) -> dict | list:
    return read_json_file(path)


def resolve_export_root(root: Path, expected_file: str) -> Path:
    if (root / expected_file).exists():
        return root
    children = [child for child in root.iterdir() if child.is_dir() and (child / expected_file).exists()]
    if children:
        return children[0]
    raise SystemExit(f"Could not find {expected_file} under {root}")


def load_source_payloads(roots: list[Path], expected_file: str, source_kind: str) -> list[dict]:
    payloads: list[dict] = []
    for root in roots:
        export_root = resolve_export_root(root, expected_file)
        payload = load_json(export_root / expected_file)
        if not isinstance(payload, dict):
            continue
        payload["_export_root"] = str(export_root)
        payload["_source_kind"] = source_kind
        payloads.append(payload)
    return payloads


def metadata_by_video_id(root: Path) -> dict[str, tuple[dict, str]]:
    mapping: dict[str, tuple[dict, str]] = {}
    for path in sorted(root.glob("*.json")):
        if path.name in {"search_videos.json", "topic_videos.json", "downloads.json"}:
            continue
        try:
            payload = load_json(path)
        except Exception:
            continue
        if not isinstance(payload, dict):
            continue
        video_id = clean_text(payload.get("video_id") or payload.get("raw", {}).get("id"))
        if video_id:
            mapping[video_id] = (payload, str(path))
    return mapping


def extract_hashtags(video_payload: dict) -> list[str]:
    raw = video_payload.get("raw") or {}
    tags: list[str] = []
    for item in raw.get("challengeInfoList") or []:
        if isinstance(item, dict):
            tag = clean_text(item.get("challengeName"))
            if tag and tag not in tags:
                tags.append(tag)
    for item in raw.get("textExtra") or []:
        if isinstance(item, dict):
            tag = clean_text(item.get("hashtagName") or item.get("HashtagName"))
            if tag and tag not in tags:
                tags.append(tag)
    return tags


def first_text(*values: object) -> str:
    for value in values:
        text = clean_text(value)
        if text:
            return text
    return ""


def extract_desc(video_payload: dict) -> str:
    raw = video_payload.get("raw") or {}
    contents = raw.get("contents") or []
    merged_contents = " ".join(
        clean_text(item.get("desc"))
        for item in contents
        if isinstance(item, dict) and clean_text(item.get("desc"))
    ).strip()
    return first_text(
        video_payload.get("title"),
        raw.get("desc"),
        merged_contents,
        (video_payload.get("oembed") or {}).get("title"),
    )


def build_core_topic(video_payload: dict) -> str:
    desc = extract_desc(video_payload)
    if desc:
        first = desc.split("#", 1)[0].strip()
        if first:
            return first[:120]
    hashtags = extract_hashtags(video_payload)
    if hashtags:
        return ", ".join(f"#{item}" for item in hashtags[:4])
    music = clean_text(video_payload.get("music_title"))
    author = video_payload.get("author") or {}
    author_name = first_text(author.get("nickname"), author.get("unique_id"), author.get("uniqueId"))
    if author_name and music:
        return f"{author_name} | {music}"
    return ""


def infer_hook_text(video_payload: dict) -> str:
    desc = extract_desc(video_payload)
    if desc:
        first_clause = desc.split(".")[0].strip()
        if first_clause:
            return first_clause[:160]
        return desc[:160]
    return build_core_topic(video_payload)[:160]


def derive_video_url(video_payload: dict) -> str:
    raw = video_payload.get("raw") or {}
    return first_text(
        video_payload.get("source_url"),
        (raw.get("shareMeta") or {}).get("canonical"),
        (raw.get("share_info") or {}).get("url"),
    )


def compute_score(video: dict) -> int:
    likes = safe_int(video.get("digg_count"))
    comments = safe_int(video.get("comment_count"))
    shares = safe_int(video.get("share_count"))
    plays = safe_int(video.get("play_count"))
    collects = safe_int(video.get("collect_count"))
    return likes + comments * 20 + shares * 30 + collects * 10 + plays // 100


def normalize_video_row(video_payload: dict, *, source_kind: str, source_label: str, metadata_lookup: dict[str, tuple[dict, str]]) -> dict:
    author = video_payload.get("author") or {}
    stats = video_payload.get("stats") or {}
    raw = video_payload.get("raw") or {}
    raw_stats = raw.get("stats") or {}
    media = video_payload.get("media") or {}
    video_id = clean_text(video_payload.get("video_id") or raw.get("id"))
    metadata, metadata_path = metadata_lookup.get(video_id, ({}, ""))
    metadata_author = metadata.get("author") or {}

    row = {
        "source_kind": source_kind,
        "source_label": source_label,
        "video_id": video_id,
        "video_url": derive_video_url(video_payload),
        "desc": extract_desc(metadata or video_payload) or extract_desc(video_payload),
        "caption_text": extract_desc(metadata or video_payload) or extract_desc(video_payload),
        "hook_text": infer_hook_text(metadata or video_payload) or infer_hook_text(video_payload),
        "core_topic": build_core_topic(metadata or video_payload) or build_core_topic(video_payload),
        "hashtags": extract_hashtags(metadata or video_payload) or extract_hashtags(video_payload),
        "unique_id": first_text(metadata_author.get("unique_id"), metadata_author.get("uniqueId"), author.get("unique_id"), author.get("uniqueId")),
        "nickname": first_text(metadata_author.get("nickname"), metadata_author.get("nickName"), author.get("nickname"), author.get("nickName")),
        "author_signature": first_text(metadata_author.get("signature"), author.get("signature")),
        "author_verified": bool(metadata_author.get("verified") if metadata_author else author.get("verified")),
        "digg_count": safe_int(stats.get("digg_count") or raw_stats.get("diggCount")),
        "comment_count": safe_int(stats.get("comment_count") or raw_stats.get("commentCount")),
        "share_count": safe_int(stats.get("share_count") or raw_stats.get("shareCount")),
        "play_count": safe_int(stats.get("play_count") or raw_stats.get("playCount")),
        "collect_count": safe_int(raw_stats.get("collectCount")),
        "created_at_utc": clean_text(video_payload.get("create_time") or raw.get("createTime")),
        "music_title": first_text(metadata.get("music_title"), video_payload.get("music_title")),
        "cover_url": first_text(media.get("cover"), (video_payload.get("oembed") or {}).get("thumbnail_url")),
        "play_addr": clean_text(media.get("url")),
        "downloaded_metadata_path": metadata_path,
    }
    row["score"] = compute_score(row)
    return row


def dedupe_ranked_rows(rows: list[dict]) -> list[dict]:
    deduped: dict[str, dict] = {}
    for row in rows:
        key = clean_text(row.get("video_id")) or clean_text(row.get("video_url"))
        if not key:
            continue
        previous = deduped.get(key)
        if previous is None or safe_int(row.get("score")) > safe_int(previous.get("score")):
            deduped[key] = row
    ordered = list(deduped.values())
    ordered.sort(key=lambda item: (safe_int(item.get("score")), safe_int(item.get("digg_count"))), reverse=True)
    return ordered


def normalize_source_payloads(payloads: list[dict]) -> tuple[list[dict], list[dict]]:
    rows: list[dict] = []
    source_manifest: list[dict] = []
    for payload in payloads:
        source_root = Path(clean_text(payload.get("_export_root")))
        source_kind = clean_text(payload.get("_source_kind"))
        source_label = clean_text(payload.get("query") or payload.get("topic"))
        metadata_lookup = metadata_by_video_id(source_root)
        videos = payload.get("videos") or []
        if not isinstance(videos, list):
            continue
        source_manifest.append(
            {
                "source_kind": source_kind,
                "source_label": source_label,
                "export_root": str(source_root),
                "item_count": len(videos),
                "metadata_count": len(metadata_lookup),
            }
        )
        for item in videos:
            if isinstance(item, dict):
                rows.append(
                    normalize_video_row(
                        item,
                        source_kind=source_kind,
                        source_label=source_label,
                        metadata_lookup=metadata_lookup,
                    )
                )
    return dedupe_ranked_rows(rows), source_manifest


def load_previous_state(state_root: Path) -> dict:
    latest = state_root / "latest_snapshot.json"
    if latest.exists():
        payload = load_json(latest)
        if isinstance(payload, dict):
            return payload
    return {}


def build_repeated_hooks(rows: list[dict]) -> list[dict]:
    counts: dict[str, dict] = {}
    for row in rows:
        hook = clean_text(row.get("hook_text"))
        if not hook:
            continue
        key = hook.lower()[:120]
        entry = counts.setdefault(
            key,
            {
                "hook_text": hook[:160],
                "count": 0,
                "video_ids": [],
                "sources": [],
            },
        )
        entry["count"] += 1
        video_id = clean_text(row.get("video_id"))
        source_label = clean_text(row.get("source_label"))
        if video_id and video_id not in entry["video_ids"]:
            entry["video_ids"].append(video_id)
        if source_label and source_label not in entry["sources"]:
            entry["sources"].append(source_label)
    repeated = [entry for entry in counts.values() if safe_int(entry.get("count")) >= 2]
    repeated.sort(key=lambda item: safe_int(item.get("count")), reverse=True)
    return repeated


def build_delta(current_rows: list[dict], previous_snapshot: dict, *, alert_like_jump: int, alert_score_jump: int) -> dict:
    previous_rows = previous_snapshot.get("ranked_videos") or []
    previous_map = {
        clean_text(item.get("video_id") or item.get("video_url")): item
        for item in previous_rows
        if isinstance(item, dict)
    }
    new_videos: list[dict] = []
    breakout_videos: list[dict] = []
    changed_videos: list[dict] = []

    for row in current_rows:
        key = clean_text(row.get("video_id") or row.get("video_url"))
        previous = previous_map.get(key)
        if previous is None:
            new_videos.append(
                {
                    "video_id": clean_text(row.get("video_id")),
                    "video_url": clean_text(row.get("video_url")),
                    "hook_text": clean_text(row.get("hook_text")),
                    "score": safe_int(row.get("score")),
                    "digg_count": safe_int(row.get("digg_count")),
                    "source_label": clean_text(row.get("source_label")),
                }
            )
            continue
        like_jump = safe_int(row.get("digg_count")) - safe_int(previous.get("digg_count"))
        score_jump = safe_int(row.get("score")) - safe_int(previous.get("score"))
        if like_jump > 0 or score_jump > 0:
            changed_videos.append(
                {
                    "video_id": clean_text(row.get("video_id")),
                    "video_url": clean_text(row.get("video_url")),
                    "hook_text": clean_text(row.get("hook_text")),
                    "like_jump": like_jump,
                    "score_jump": score_jump,
                    "source_label": clean_text(row.get("source_label")),
                }
            )
        if like_jump >= alert_like_jump or score_jump >= alert_score_jump:
            breakout_videos.append(
                {
                    "video_id": clean_text(row.get("video_id")),
                    "video_url": clean_text(row.get("video_url")),
                    "hook_text": clean_text(row.get("hook_text")),
                    "like_jump": like_jump,
                    "score_jump": score_jump,
                    "source_label": clean_text(row.get("source_label")),
                }
            )

    repeated_hooks = build_repeated_hooks(current_rows)
    return {
        "previous_snapshot_at": clean_text(previous_snapshot.get("snapshot_at")),
        "current_snapshot_count": len(current_rows),
        "previous_snapshot_count": len(previous_rows),
        "new_videos": new_videos,
        "changed_videos": changed_videos,
        "breakout_videos": breakout_videos,
        "repeated_hooks": repeated_hooks,
        "summary_change": f"{len(new_videos)} new videos, {len(changed_videos)} positive movers",
        "summary_breakout": f"{len(breakout_videos)} videos crossed breakout thresholds",
        "watch_tomorrow": "Watch whether today's repeated hooks persist or collapse in the next cycle",
    }


def build_alerts(delta: dict) -> list[dict]:
    alerts: list[dict] = []
    for item in delta.get("breakout_videos") or []:
        alerts.append(
            {
                "alert_type": "breakout_video",
                "signal": "Breakout video",
                "label": clean_text(item.get("video_id") or item.get("video_url")),
                "detail": f"like_jump={safe_int(item.get('like_jump'))}, score_jump={safe_int(item.get('score_jump'))}",
                "meaning": "A known tracked post accelerated fast enough to merit deeper teardown.",
                "follow_up": "Add this post to the next Scene 03 shortlist.",
                "next_action": "Queue for Scene 03 deep teardown.",
            }
        )
    for item in (delta.get("new_videos") or [])[:3]:
        alerts.append(
            {
                "alert_type": "new_video",
                "signal": "New entrant",
                "label": clean_text(item.get("video_id") or item.get("video_url")),
                "detail": clean_text(item.get("hook_text")) or "New video detected in patrol pool",
                "meaning": "A new post entered the tracked category and may represent a fresh angle or creator.",
                "follow_up": "Compare it against current shortlist quality before escalating.",
                "next_action": "Keep if it outranks the current floor.",
            }
        )
    for item in (delta.get("repeated_hooks") or [])[:2]:
        alerts.append(
            {
                "alert_type": "repeated_hook",
                "signal": "Repeated hook across accounts",
                "label": clean_text(item.get("hook_text")),
                "detail": f"count={safe_int(item.get('count'))}",
                "meaning": "Multiple tracked posts are converging on similar packaging, which can indicate category drift or hook saturation.",
                "follow_up": "Compare whether the repeated wording is worth tearing down or should be avoided as a crowded angle.",
                "next_action": "Review in Scene 03 only if the examples also carry strong proof.",
            }
        )
    return alerts


def scene03_candidates(rows: list[dict], delta: dict, *, scene03_count: int, min_likes: int) -> list[dict]:
    breakout_ids = {
        clean_text(item.get("video_id") or item.get("video_url"))
        for item in (delta.get("breakout_videos") or [])
        if clean_text(item.get("video_id") or item.get("video_url"))
    }
    ordered: list[dict] = []
    for row in rows:
        key = clean_text(row.get("video_id") or row.get("video_url"))
        if breakout_ids and key in breakout_ids:
            ordered.append({**row, "scene03_reason": "Breakout video crossed alert threshold"})
    for row in rows:
        if len(ordered) >= scene03_count:
            break
        key = clean_text(row.get("video_id") or row.get("video_url"))
        if any(clean_text(item.get("video_id") or item.get("video_url")) == key for item in ordered):
            continue
        if safe_int(row.get("digg_count")) >= min_likes:
            ordered.append({**row, "scene03_reason": "High-likes candidate for deeper teardown"})
    for row in rows:
        if len(ordered) >= scene03_count:
            break
        key = clean_text(row.get("video_id") or row.get("video_url"))
        if any(clean_text(item.get("video_id") or item.get("video_url")) == key for item in ordered):
            continue
        ordered.append({**row, "scene03_reason": "Top-ranked fallback candidate"})
    return ordered[:scene03_count]


def infer_missing_fields(rows: list[dict]) -> list[dict]:
    checks = [
        ("caption_text", "Better Scene 03 teardown quality and clearer packaging recovery"),
        ("hook_text", "Faster hook clustering and repeated-angle detection"),
        ("core_topic", "Cleaner topic-level grouping across patrol cycles"),
        ("author_signature", "More reliable authority-versus-packaging separation"),
        ("downloaded_metadata_path", "Richer enrichment for top candidates"),
    ]
    missing: list[dict] = []
    for field, why in checks:
        missing_count = sum(1 for row in rows if not clean_text(row.get(field)))
        if missing_count:
            missing.append(
                {
                    "field": field,
                    "why": f"{missing_count} tracked rows are missing this field. {why}",
                    "required": "Yes" if field != "downloaded_metadata_path" else "Optional but recommended",
                }
            )
    return missing


def build_tracked_videos(rows: list[dict], *, cadence: str, shortlist_count: int) -> list[dict]:
    tracked: list[dict] = []
    for row in rows[:shortlist_count]:
        tracked.append(
            {
                "video_id": clean_text(row.get("video_id")),
                "video_url": clean_text(row.get("video_url")),
                "hook_text": clean_text(row.get("hook_text")),
                "core_topic": clean_text(row.get("core_topic")),
                "score": safe_int(row.get("score")),
                "digg_count": safe_int(row.get("digg_count")),
                "summary": clean_text(row.get("hook_text")) or clean_text(row.get("core_topic")),
                "why_it_matters": "Top-ranked category row worth monitoring across patrol cycles",
                "watch_reason": "High score or strong packaging signal in current patrol window",
                "movement_reason": "Potential Scene 03 candidate if it persists or accelerates",
                "cadence": cadence.capitalize(),
                "field": clean_text(row.get("video_url")) or clean_text(row.get("video_id")),
                "source_label": clean_text(row.get("source_label")),
            }
        )
    return tracked


def write_capture_pack(
    *,
    capture_root: Path,
    category: str,
    market: str,
    cadence: str,
    queries: list[str],
    topics: list[str],
    ranked_rows: list[dict],
    source_manifest: list[dict],
    previous_snapshot: dict,
    delta: dict,
    alerts: list[dict],
    scene03_rows: list[dict],
    min_likes: int,
    shortlist_count: int,
) -> dict:
    snapshot_at = datetime.now().isoformat(timespec="seconds")
    tracked = build_tracked_videos(ranked_rows, cadence=cadence, shortlist_count=shortlist_count)
    snapshot = {
        "snapshot_at": snapshot_at,
        "category": category,
        "market": market,
        "cadence": cadence,
        "queries": queries,
        "topics": topics,
        "ranked_videos": ranked_rows,
        "tracked_videos": tracked,
        "missing_fields": infer_missing_fields(ranked_rows),
    }
    profile_url = clean_text(ranked_rows[0].get("video_url")) if ranked_rows else ""
    profile_summary = {
        "profile_url": profile_url,
        "session_quality": "scene02_patrol_runtime",
        "ranked_video_count": len(ranked_rows),
        "qualified_video_count": len(scene03_rows),
        "checked_at": snapshot_at,
    }
    aggregate_summary = {
        "started_at": snapshot_at,
        "ended_at": snapshot_at,
        "category": category,
        "market": market,
        "cadence": cadence,
        "queries": queries,
        "topics": topics,
        "profile_count": len(source_manifest),
        "aggregated_ranked_count": len(ranked_rows),
        "aggregated_qualified_count": len(scene03_rows),
        "min_likes": min_likes,
        "output_root": str(capture_root),
        "append_mode": "append_to_same_board",
        "append_scope_key": f"{category}::{market}::{cadence}",
    }
    summary = {
        "checked_at": snapshot_at,
        "platform": "tiktok",
        "reachable": True,
        "session_quality": "scene02_patrol_runtime",
        "profile_final_url": profile_url,
        "ranked_video_count": len(ranked_rows),
        "qualified_video_count": len(scene03_rows),
        "notes": [
            "Scene 02 patrol runtime pack generated inside tiktok-growth-operator.skill.",
            "Snapshot delta is derived against the previous local patrol state when present.",
        ],
    }

    write_json_file(capture_root / "summary.json", summary)
    write_json_file(capture_root / "profile_summary.json", profile_summary)
    write_json_file(capture_root / "aggregate_summary.json", aggregate_summary)
    write_json_file(capture_root / "ranked_videos.json", ranked_rows)
    write_json_file(capture_root / "aggregate_ranked_videos.json", ranked_rows)
    write_json_file(capture_root / "aggregate_qualified_videos.json", scene03_rows)
    write_json_file(capture_root / "patrol_snapshot.json", snapshot)
    write_json_file(capture_root / "patrol_delta.json", delta)
    write_json_file(capture_root / "patrol_alerts.json", alerts)
    write_json_file(capture_root / "scene03_candidates.json", scene03_rows)
    write_json_file(capture_root / "source_manifest.json", source_manifest)
    write_json_file(
        capture_root / "patrol_config.json",
        {
            "category": category,
            "market": market,
            "cadence": cadence,
            "queries": queries,
            "topics": topics,
            "min_likes": min_likes,
            "shortlist_count": shortlist_count,
            "append_mode": "append_to_same_board",
            "append_scope_key": f"{category}::{market}::{cadence}",
            "append_strategy": "append each patrol run into the same logical board keyed by category + market + cadence",
            "append_columns": [
                "capture_date",
                "snapshot_at",
                "keyword_or_topic",
                "video_url",
                "video_id",
                "score",
                "digg_count",
                "comment_count",
                "share_count",
                "shortlist_status",
                "scene03_dispatch",
            ],
        },
    )
    write_utf8_text(
        capture_root / "qualified_video_links.txt",
        "\n".join(clean_text(item.get("video_url")) for item in scene03_rows if clean_text(item.get("video_url"))) + "\n",
    )
    write_utf8_text(
        capture_root / "aggregate_report.md",
        "\n".join(
            [
                "# Scene 02 Patrol Capture Pack",
                "",
                f"- category: `{category}`",
                f"- market: `{market}`",
                f"- cadence: `{cadence}`",
                f"- current ranked rows: `{len(ranked_rows)}`",
                f"- new videos: `{len(delta.get('new_videos') or [])}`",
                f"- breakout videos: `{len(delta.get('breakout_videos') or [])}`",
                f"- scene03 candidates: `{len(scene03_rows)}`",
                f"- previous snapshot: `{clean_text(previous_snapshot.get('snapshot_at')) or 'none'}`",
            ]
        )
        + "\n"
    )
    return snapshot


def write_state(state_root: Path, snapshot: dict, delta: dict) -> None:
    state_root.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_path = state_root / f"snapshot-{stamp}.json"
    write_json_file(archive_path, snapshot)
    write_json_file(state_root / "latest_snapshot.json", snapshot)
    write_json_file(state_root / "latest_delta.json", delta)
    write_json_file(
        state_root / "state_manifest.json",
        {
            "updated_at": datetime.now().isoformat(timespec="seconds"),
            "latest_snapshot": str(state_root / "latest_snapshot.json"),
            "latest_delta": str(state_root / "latest_delta.json"),
            "latest_archive_snapshot": str(archive_path),
        },
    )


def build_scene03_capture_pack(root: Path, base_snapshot: dict, rows: list[dict], category: str, market: str, min_likes: int) -> Path:
    capture_root = root / "scene03-capture-pack"
    capture_root.mkdir(parents=True, exist_ok=True)
    snapshot_at = datetime.now().isoformat(timespec="seconds")
    summary = {
        "checked_at": snapshot_at,
        "platform": "tiktok",
        "reachable": True,
        "session_quality": "scene02_scene03_handoff",
        "profile_final_url": clean_text(rows[0].get("video_url")) if rows else "",
        "ranked_video_count": len(rows),
        "qualified_video_count": len(rows),
    }
    profile_summary = {
        "profile_url": clean_text(rows[0].get("video_url")) if rows else "",
        "session_quality": "scene02_scene03_handoff",
        "ranked_video_count": len(rows),
        "qualified_video_count": len(rows),
        "checked_at": snapshot_at,
    }
    aggregate_summary = {
        "started_at": snapshot_at,
        "ended_at": snapshot_at,
        "profile_count": 1,
        "aggregated_ranked_count": len(rows),
        "aggregated_qualified_count": len(rows),
        "min_likes": min_likes,
        "category": category,
        "market": market,
        "handoff_from_scene": "02",
        "handoff_reason": "Scene 02 patrol shortlist",
    }
    write_json_file(capture_root / "summary.json", summary)
    write_json_file(capture_root / "profile_summary.json", profile_summary)
    write_json_file(capture_root / "aggregate_summary.json", aggregate_summary)
    write_json_file(capture_root / "ranked_videos.json", rows)
    write_json_file(capture_root / "aggregate_ranked_videos.json", rows)
    write_json_file(capture_root / "aggregate_qualified_videos.json", rows)
    write_json_file(capture_root / "source_manifest.json", {"scene02_snapshot_at": clean_text(base_snapshot.get("snapshot_at")), "source_scene": "02"})
    write_utf8_text(
        capture_root / "qualified_video_links.txt",
        "\n".join(clean_text(item.get("video_url")) for item in rows if clean_text(item.get("video_url"))) + "\n",
    )
    return capture_root


def main() -> None:
    args = parse_args()
    queries = split_csv(args.queries)
    topics = split_csv(args.topics)
    if args.mode in {"search", "mixed"} and not queries and not args.query_root.strip():
        raise SystemExit("Search or mixed mode requires --queries or --query-root.")
    if args.mode in {"topic", "mixed"} and not topics and not args.topic_root.strip():
        raise SystemExit("Topic or mixed mode requires --topics or --topic-root.")

    skill_root = Path(__file__).resolve().parents[1]
    run_root = ensure_root(args.output_root, skill_root, args.name)
    capture_root = run_root / "capture-pack"
    state_root = ensure_state_root(skill_root, args.project, args.category, args.market)
    capture_root.mkdir(parents=True, exist_ok=True)

    query_roots: list[Path] = []
    topic_roots: list[Path] = []
    tikmatrix_output_root = Path(args.tikmatrix_output_root).expanduser().resolve() if args.tikmatrix_output_root.strip() else DEFAULT_TIKMATRIX_OUTPUT

    if args.query_root.strip():
        query_roots.append(Path(args.query_root).expanduser().resolve())
    if args.topic_root.strip():
        topic_roots.append(Path(args.topic_root).expanduser().resolve())

    if not args.skip_live:
        for query in queries if args.mode in {"search", "mixed"} else []:
            slug = slugify(query) or "query"
            workflow = "video-search-download" if args.download_top > 0 else "video-search"
            requested_count = min(args.count, args.download_top) if args.download_top > 0 else args.count
            output_dir = tikmatrix_output_root / f"scene02-{workflow}-{slug}-{timestamp_slug()}"
            run_tikmatrix(workflow, query, requested_count, output_dir)
            query_roots.append(output_dir)
        for topic in topics if args.mode in {"topic", "mixed"} else []:
            slug = slugify(topic) or "topic"
            workflow = "topic-download" if args.download_top > 0 else "topic-videos"
            requested_count = min(args.count, args.download_top) if args.download_top > 0 else args.count
            output_dir = tikmatrix_output_root / f"scene02-{workflow}-{slug}-{timestamp_slug()}"
            run_tikmatrix(workflow, topic, requested_count, output_dir)
            topic_roots.append(output_dir)

    payloads: list[dict] = []
    if query_roots:
        payloads.extend(load_source_payloads(query_roots, "search_videos.json", "search"))
    if topic_roots:
        payloads.extend(load_source_payloads(topic_roots, "topic_videos.json", "topic"))
    if not payloads:
        raise SystemExit("No patrol source payloads were found.")

    ranked_rows, source_manifest = normalize_source_payloads(payloads)
    ranked_rows = ranked_rows[: max(args.shortlist_count * 3, args.scene03_count, 10)]
    previous_snapshot = load_previous_state(state_root)
    delta = build_delta(
        ranked_rows,
        previous_snapshot,
        alert_like_jump=args.alert_like_jump,
        alert_score_jump=args.alert_score_jump,
    )
    alerts = build_alerts(delta)
    scene03_rows = scene03_candidates(
        ranked_rows,
        delta,
        scene03_count=args.scene03_count,
        min_likes=args.min_likes,
    )
    snapshot = write_capture_pack(
        capture_root=capture_root,
        category=args.category,
        market=args.market,
        cadence=args.cadence,
        queries=queries,
        topics=topics,
        ranked_rows=ranked_rows,
        source_manifest=source_manifest,
        previous_snapshot=previous_snapshot,
        delta=delta,
        alerts=alerts,
        scene03_rows=scene03_rows,
        min_likes=args.min_likes,
        shortlist_count=args.shortlist_count,
    )
    write_state(state_root, snapshot, delta)

    scene02_result = create_capture_pack_run(
        scene="02",
        capture_root_raw=str(capture_root),
        name=args.name,
        project=args.project,
        output_root=str(run_root / "scene02-run"),
        platform="TikTok",
        market=args.market,
        formats=args.formats,
        operator_packs_raw=args.operator_packs,
    )

    scene03_result: dict | None = None
    if args.also_run_scene03 and scene03_rows:
        handoff_root = build_scene03_capture_pack(run_root, snapshot, scene03_rows, args.category, args.market, args.min_likes)
        scene03_result = create_capture_pack_run(
            scene="03",
            capture_root_raw=str(handoff_root),
            name=f"{args.name}-scene03",
            project=f"{args.project} Scene 03 Follow-up",
            output_root=str(run_root / "scene03-run"),
            platform="TikTok",
            market=args.market,
            formats=args.formats,
            operator_packs_raw=args.operator_packs,
        )

    manifest = {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "name": args.name,
        "project": args.project,
        "scene": "02",
        "resolved_mode": "capture-pack",
        "run_root": str(run_root),
        "capture_root": str(capture_root),
        "state_root": str(state_root),
        "category": args.category,
        "market": args.market,
        "cadence": args.cadence,
        "mode": args.mode,
        "queries": queries,
        "topics": topics,
        "source_manifest": source_manifest,
        "alert_count": len(alerts),
        "scene03_candidate_count": len(scene03_rows),
        "report_json": scene02_result.get("report_json", ""),
        "operator_packs": [item.get("type", "") for item in scene02_result.get("operator_packs", []) if item.get("type")],
        "scene02_result": scene02_result,
        "scene03_result": scene03_result or {},
    }
    write_json_file(run_root / "run_manifest.json", manifest)
    write_utf8_text(
        run_root / "README.md",
        "\n".join(
            [
                "# Scene 02 Patrol Run",
                "",
                f"- category: `{args.category}`",
                f"- market: `{args.market}`",
                f"- cadence: `{args.cadence}`",
                f"- queries: `{', '.join(queries) or 'none'}`",
                f"- topics: `{', '.join(topics) or 'none'}`",
                f"- alerts: `{len(alerts)}`",
                f"- scene03 candidates: `{len(scene03_rows)}`",
                "",
                "## Outputs",
                "",
                f"- capture pack: `{capture_root}`",
                f"- Scene 02 operator run: `{scene02_result['run_root']}`",
                f"- state root: `{state_root}`",
                f"- Scene 03 follow-up: `{scene03_result['run_root']}`" if scene03_result else "- Scene 03 follow-up: not generated",
            ]
        )
        + "\n"
    )

    print(
        json.dumps(
            {
                "run_root": str(run_root),
                "capture_root": str(capture_root),
                "scene02_result": scene02_result,
                "scene03_result": scene03_result or {},
                "alert_count": len(alerts),
                "scene03_candidate_count": len(scene03_rows),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
