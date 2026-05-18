from __future__ import annotations

from pathlib import Path

from pack_video_text import clean_text, hook_text, sentence_clip
from text_normalization import write_json_file
from weekly_baseline import compare_latest_two_weeks, packaging_lane, safe_int


COMPETITOR_WEEKLY_BOARD_HEADERS = [
    "报告模式",
    "竞品账号",
    "比较窗口",
    "本周帖数",
    "头部视频",
    "包装线",
    "关键信号",
    "周度变化",
    "策略判断",
    "运营动作",
    "优先级",
    "证据等级",
]


def _video_url(video: dict) -> str:
    return clean_text(video.get("video_url") or video.get("url") or video.get("video_id"))


def _account_label(video: dict) -> str:
    unique_id = clean_text(video.get("unique_id") or video.get("author_unique_id"))
    nickname = clean_text(video.get("nickname"))
    profile_url = clean_text(video.get("profile_url"))
    if unique_id and nickname and nickname.lower() != unique_id.lower():
        return f"{unique_id} / {nickname}"
    return unique_id or nickname or profile_url or "未标记账号"


def _account_key(video: dict) -> str:
    return (
        clean_text(video.get("unique_id"))
        or clean_text(video.get("author_unique_id"))
        or clean_text(video.get("profile_url"))
        or clean_text(video.get("nickname"))
        or "unknown-account"
    )


def _ranked_account_groups(videos: list[dict]) -> list[tuple[str, list[dict]]]:
    grouped: dict[str, list[dict]] = {}
    for video in videos:
        if not isinstance(video, dict):
            continue
        grouped.setdefault(_account_key(video), []).append(video)
    return sorted(
        grouped.items(),
        key=lambda pair: max((safe_int(item.get("score")) for item in pair[1]), default=0),
        reverse=True,
    )


def _top_video(videos: list[dict]) -> dict:
    ordered = sorted(
        videos,
        key=lambda item: (safe_int(item.get("score")), safe_int(item.get("digg_count"))),
        reverse=True,
    )
    return ordered[0] if ordered else {}


def _lane_label(video: dict) -> str:
    explicit = clean_text(video.get("reuse_value_label") or video.get("core_topic"))
    if explicit:
        return explicit
    return packaging_lane(video)


def _strategy_note(video: dict) -> str:
    lane = _lane_label(video)
    if "权威" in lane:
        return "本周更偏向信任 / 权威型包装。"
    if "情绪" in lane:
        return "本周更偏向情绪或时刻感驱动包装。"
    if "选题" in lane or "角度" in lane:
        return "本周更像在测试新的选题角度或包装法。"
    return "延续识别优先的包装，只做轻量形式变化。"


def _cue_text(video: dict, *, limit: int = 88) -> str:
    return sentence_clip(hook_text(video) or clean_text(video.get("desc")), limit=limit) or "关键信号缺失"


def _metric_summary(video: dict) -> str:
    parts = []
    for label, key in [("点赞", "digg_count"), ("评论", "comment_count"), ("分享", "share_count"), ("播放", "play_count"), ("分数", "score")]:
        value = video.get(key)
        if value not in (None, "", 0, "0"):
            parts.append(f"{label}={value}")
    return " | ".join(parts)


def _trend_action(latest_likes: int, prior_likes: int, *, baseline: bool) -> tuple[str, str]:
    if baseline:
        return "建立基线", "中"
    if prior_likes and latest_likes >= int(prior_likes * 1.35):
        return "继续追", "高"
    if prior_likes and latest_likes <= int(prior_likes * 0.8):
        return "减少跟进", "中"
    return "观察", "中"


def _matrix_account_row(
    account_videos: list[dict],
    *,
    evidence_grade: str,
) -> list[str]:
    account_compare = compare_latest_two_weeks(account_videos)
    latest_rows = sorted(
        account_compare.get("latest_rows", []),
        key=lambda item: (safe_int(item.get("score")), safe_int(item.get("digg_count"))),
        reverse=True,
    )
    top_video = latest_rows[0] if latest_rows else _top_video(account_videos)
    prior_top = _top_video(account_compare.get("prior_rows", []))
    latest_week = clean_text(account_compare.get("latest_week")) or "week unknown"
    prior_week = clean_text(account_compare.get("prior_week"))
    latest_likes = safe_int(top_video.get("digg_count"))
    prior_likes = safe_int(prior_top.get("digg_count"))
    baseline = account_compare.get("mode") != "compare"
    if baseline:
        window = f"{latest_week} 基线周"
        shift = "仅基线周"
        strategy = "下周同字段复采后再判断是否为策略变化"
    else:
        window = f"{latest_week} vs {prior_week}"
        if prior_likes and latest_likes >= int(prior_likes * 1.35):
            shift = "本周明显增强"
        elif prior_likes and latest_likes <= int(prior_likes * 0.8):
            shift = "本周明显回落"
        else:
            shift = "本周相对持平"
        strategy = _strategy_note(top_video)
        if prior_top:
            strategy = f"{strategy}；上周头部线：{_lane_label(prior_top)}"
    action, priority = _trend_action(latest_likes, prior_likes, baseline=baseline)
    return [
        "竞品矩阵",
        _account_label(top_video or account_videos[0]),
        window,
        str(len(latest_rows) or len(account_videos)),
        _video_url(top_video),
        _lane_label(top_video),
        _cue_text(top_video),
        shift,
        strategy,
        action,
        priority,
        evidence_grade,
    ]


def _single_account_rows(
    ranked_videos: list[dict],
    compare: dict,
    dispatch_rows: list[list[str]],
    *,
    account_label: str,
    evidence_grade: str,
) -> list[list[str]]:
    rows: list[list[str]] = []
    latest_week = clean_text(compare.get("latest_week")) or "本周"
    prior_week = clean_text(compare.get("prior_week"))
    latest_rows = sorted(
        compare.get("latest_rows", []),
        key=lambda item: (safe_int(item.get("score")), safe_int(item.get("digg_count"))),
        reverse=True,
    )
    top_video = latest_rows[0] if latest_rows else _top_video(ranked_videos)
    prior_top = _top_video(compare.get("prior_rows", []))
    baseline = compare.get("mode") != "compare"
    window = f"{latest_week} vs {prior_week}" if not baseline else f"{latest_week} 基线周"
    shift = (
        _strategy_note(top_video)
        if baseline
        else (
            "本周明显增强"
            if prior_top and safe_int(top_video.get("digg_count")) >= int(safe_int(prior_top.get("digg_count")) * 1.35)
            else (
                "本周明显回落"
                if prior_top and safe_int(top_video.get("digg_count")) <= int(safe_int(prior_top.get("digg_count")) * 0.8)
                else "本周相对持平"
            )
        )
    )
    action, priority = _trend_action(
        safe_int(top_video.get("digg_count")),
        safe_int(prior_top.get("digg_count")),
        baseline=baseline,
    )
    rows.append(
        [
            "单账号周报",
            account_label,
            window,
            str(len(latest_rows) or len(ranked_videos)),
            _video_url(top_video),
            _lane_label(top_video),
            _cue_text(top_video),
            shift,
            _strategy_note(top_video),
            action,
            priority,
            evidence_grade,
        ]
    )
    for dispatch in dispatch_rows[:3]:
        if not isinstance(dispatch, list) or len(dispatch) < 4:
            continue
        rows.append(
            [
                "调度动作",
                account_label,
                clean_text(dispatch[1]),
                "",
                "",
                "",
                clean_text(dispatch[2]),
                clean_text(dispatch[3]),
                clean_text(dispatch[0]),
                "中",
                evidence_grade,
            ]
        )
    return rows


def build_competitor_weekly_board_payload(
    *,
    ranked_videos: list[dict],
    profile_summary: dict,
    comment_snapshot: dict,
    compare: dict,
    coverage: dict,
    evidence_grade: str,
    matrix_mode: bool,
    dispatch_rows: list[list[str]],
    append_scope_key: str = "",
    market: str = "",
    category: str = "",
) -> dict:
    _ = comment_snapshot, market, category
    rows: list[list[str]] = []
    if matrix_mode:
        for _, account_videos in _ranked_account_groups(ranked_videos)[:5]:
            rows.append(_matrix_account_row(account_videos, evidence_grade=evidence_grade))
    else:
        account_label = clean_text(profile_summary.get("profile_url")) or _account_label(_top_video(ranked_videos))
        rows.extend(
            _single_account_rows(
                ranked_videos,
                compare,
                dispatch_rows,
                account_label=account_label,
                evidence_grade=evidence_grade,
            )
        )

    if not rows and ranked_videos:
        fallback = _top_video(ranked_videos)
        rows.append(
            [
                "样本不足",
                _account_label(fallback),
                clean_text(compare.get("latest_week")) or "week unknown",
                str(safe_int(coverage.get("post_count")) or len(ranked_videos)),
                _video_url(fallback),
                _lane_label(fallback),
                _cue_text(fallback),
                "待补周对照",
                "先保留为观察项",
                "观察",
                "低",
                evidence_grade,
            ]
        )

    return {
        "schema_version": "scene18-competitor-weekly-board-v1",
        "headers": COMPETITOR_WEEKLY_BOARD_HEADERS,
        "rows": rows,
        "row_count": len(rows),
        "append_scope_key": append_scope_key,
        "matrix_mode": matrix_mode,
        "compare_mode": clean_text(compare.get("mode")),
        "latest_week": clean_text(compare.get("latest_week")),
        "evidence_grade": evidence_grade,
    }


def persist_competitor_weekly_board_exports(capture_root: Path, board: dict) -> dict[str, str]:
    json_path = capture_root / "competitor_weekly_board.json"
    write_json_file(json_path, board)
    return {"json": str(json_path)}
