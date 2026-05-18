from __future__ import annotations

from pathlib import Path

from pack_video_text import clean_text, hook_text, sentence_clip
from text_normalization import write_json_file


PATROL_BOARD_HEADERS = [
    "品类",
    "市场",
    "频率",
    "视频标签",
    "视频 / 链接",
    "钩子 / 主题",
    "表现信号",
    "变化标记",
    "告警摘要",
    "Scene 03 队列",
    "深拆负责人",
    "包装线",
]


def _patrol_url(entry: dict) -> str:
    return clean_text(entry.get("video_url") or entry.get("url"))


def _patrol_label(entry: dict) -> str:
    for candidate in [entry.get("source_label"), entry.get("field"), entry.get("video_id"), _patrol_url(entry)]:
        text = clean_text(candidate)
        if text:
            return text
    return "追踪项"


def _metric_summary(entry: dict) -> str:
    parts = []
    for label, key in [("点赞", "digg_count"), ("评论", "comment_count"), ("分享", "share_count"), ("播放", "play_count"), ("分数", "score")]:
        value = entry.get(key)
        if value not in (None, "", 0, "0"):
            parts.append(f"{label}={value}")
    return " | ".join(parts)


def _lane_label(entry: dict) -> str:
    topic = sentence_clip(clean_text(entry.get("core_topic") or entry.get("core_topic_text")), limit=48)
    hook = sentence_clip(hook_text(entry), limit=48)
    return topic or hook or "未分类"


def _candidate_owner(entry: dict) -> str:
    decision = clean_text(entry.get("shortlist_decision"))
    if decision in {"立即深拆", "deep_teardown_now"}:
        return "Analyst / creative"
    if safe_int(entry.get("commerce_confidence")) >= 60:
        return "Commerce / growth"
    return "Operator / strategist"


def safe_int(value: object) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def _change_mark(entry: dict, *, new_ids: set[str], breakout_ids: set[str], rising_ids: set[str]) -> str:
    video_id = clean_text(entry.get("video_id"))
    if video_id in breakout_ids:
        return "breakout"
    if video_id in new_ids:
        return "new"
    if video_id in rising_ids:
        return "rising"
    return "tracked"


def _alert_note(entry: dict, alerts: list[dict]) -> str:
    video_id = clean_text(entry.get("video_id"))
    for alert in alerts:
        if not isinstance(alert, dict):
            continue
        target = clean_text(alert.get("video_id") or alert.get("video_url"))
        if target and (target == video_id or target in clean_text(entry.get("video_url"))):
            return sentence_clip(
                f"{clean_text(alert.get('priority'))} | {clean_text(alert.get('signal'))} | {clean_text(alert.get('follow_up'))}",
                limit=120,
            )
    return ""


def _scene03_queue_note(entry: dict, next_scene03: list[dict]) -> tuple[str, str]:
    video_id = clean_text(entry.get("video_id"))
    url = clean_text(entry.get("video_url"))
    for index, candidate in enumerate(next_scene03[:3], start=1):
        if not isinstance(candidate, dict):
            continue
        if video_id and video_id == clean_text(candidate.get("video_id")):
            return f"P{index}", _candidate_owner(candidate)
        if url and url == clean_text(candidate.get("video_url")):
            return f"P{index}", _candidate_owner(candidate)
    return "", ""


def build_patrol_board_payload(
    *,
    category: str,
    market: str,
    cadence: str,
    tracked_videos: list[dict],
    alerts: list[dict],
    delta: dict,
    next_scene03: list[dict],
    append_scope_key: str = "",
) -> dict:
    new_ids = {clean_text(item.get("video_id")) for item in (delta.get("new_videos") or []) if isinstance(item, dict)}
    breakout_ids = {clean_text(item.get("video_id")) for item in (delta.get("breakout_videos") or []) if isinstance(item, dict)}
    rising_ids = {clean_text(item.get("video_id")) for item in (delta.get("rising_videos") or []) if isinstance(item, dict)}

    rows: list[list[str]] = []
    for entry in tracked_videos:
        if not isinstance(entry, dict):
            continue
        queue_rank, queue_owner = _scene03_queue_note(entry, next_scene03)
        rows.append(
            [
                category or "category pending",
                market or "market pending",
                cadence or "daily",
                _patrol_label(entry),
                _patrol_url(entry) or clean_text(entry.get("video_id")),
                sentence_clip(
                    hook_text(entry) or clean_text(entry.get("desc")) or clean_text(entry.get("core_topic")),
                    limit=88,
                )
                or "Hook/topic missing",
                _metric_summary(entry) or "metrics unavailable",
                _change_mark(entry, new_ids=new_ids, breakout_ids=breakout_ids, rising_ids=rising_ids),
                _alert_note(entry, alerts),
                queue_rank,
                queue_owner,
                _lane_label(entry),
            ]
        )

    if not rows and next_scene03:
        for index, candidate in enumerate(next_scene03[:3], start=1):
            rows.append(
                [
                    category or "category pending",
                    market or "market pending",
                    cadence or "daily",
                    clean_text(candidate.get("nickname")) or f"candidate-{index}",
                    clean_text(candidate.get("video_url") or candidate.get("video_id")),
                    sentence_clip(hook_text(candidate), limit=88) or "—",
                    _metric_summary(candidate),
                    "queue_only",
                    "",
                    f"P{index}",
                    _candidate_owner(candidate),
                    _lane_label(candidate),
                ]
            )

    return {
        "schema_version": "scene02-patrol-board-v1",
        "headers": PATROL_BOARD_HEADERS,
        "rows": rows,
        "row_count": len(rows),
        "append_scope_key": append_scope_key,
        "category": category,
        "market": market,
        "cadence": cadence,
    }


def persist_patrol_board_exports(capture_root: Path, board: dict) -> dict[str, str]:
    json_path = capture_root / "patrol_board.json"
    write_json_file(json_path, board)
    return {"json": str(json_path)}
