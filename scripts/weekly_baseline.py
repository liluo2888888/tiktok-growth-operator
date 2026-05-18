from __future__ import annotations

import re
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

from text_normalization import normalize_text, write_json_file


def clean_text(value: object) -> str:
    return normalize_text(value)


def safe_int(value: object) -> int:
    if isinstance(value, bool):
        return int(value)
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def week_sort_key(week_label: str) -> tuple[int, int]:
    match = re.match(r"(\d{4})-W(\d{1,2})$", clean_text(week_label))
    if match:
        return int(match.group(1)), int(match.group(2))
    return (0, 0)


def parse_video_datetime(video: dict) -> datetime | None:
    raw = clean_text(video.get("created_at_utc"))
    if raw:
        try:
            return datetime.fromisoformat(raw.replace("Z", "+00:00"))
        except ValueError:
            pass
        for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
            try:
                return datetime.strptime(raw[: len(fmt)], fmt)
            except ValueError:
                continue
    raw_epoch = clean_text(video.get("create_time") or video.get("createTime") or video.get("publish_time"))
    if raw_epoch:
        try:
            return datetime.fromtimestamp(int(raw_epoch))
        except (TypeError, ValueError, OSError, OverflowError):
            pass
    return None


def publish_week_label(video: dict) -> str:
    explicit = clean_text(video.get("publish_week"))
    if explicit and explicit.lower() not in {"week unknown", "week-unknown", "unknown"}:
        return explicit
    dt = parse_video_datetime(video)
    if dt is None:
        return "week unknown"
    iso_year, iso_week, _ = dt.isocalendar()
    return f"{iso_year}-W{iso_week:02d}"


def group_videos_by_publish_week(videos: list[dict]) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = {}
    for video in videos:
        if not isinstance(video, dict):
            continue
        week = publish_week_label(video)
        grouped.setdefault(week, []).append(video)
    return grouped


def compare_latest_two_weeks(videos: list[dict]) -> dict[str, Any]:
    grouped = group_videos_by_publish_week(videos)
    ordered_weeks = sorted(
        [week for week in grouped.keys() if week and week != "week unknown"],
        key=week_sort_key,
        reverse=True,
    )
    if not ordered_weeks:
        return {
            "mode": "none",
            "latest_week": "",
            "prior_week": "",
            "latest_rows": [],
            "prior_rows": [],
        }
    latest_week = ordered_weeks[0]
    prior_week = ordered_weeks[1] if len(ordered_weeks) > 1 else ""
    return {
        "mode": "compare" if prior_week else "baseline",
        "latest_week": latest_week,
        "prior_week": prior_week,
        "latest_rows": grouped.get(latest_week, []),
        "prior_rows": grouped.get(prior_week, []) if prior_week else [],
    }


def packaging_lane(video: dict) -> str:
    label = clean_text(video.get("reuse_value_label") or video.get("core_topic") or video.get("hook_text"))
    return label or "未标记包装线"


def dominant_lane(videos: list[dict]) -> str:
    lanes = [packaging_lane(video) for video in videos if packaging_lane(video) != "未标记包装线"]
    if not lanes:
        return "未恢复"
    return Counter(lanes).most_common(1)[0][0]


def avg_metric(rows: list[dict], field: str) -> float:
    if not rows:
        return 0.0
    return sum(safe_int(item.get(field)) for item in rows) / len(rows)


def repeated_hook_ratio(videos: list[dict]) -> float:
    hooks: list[str] = []
    for video in videos:
        hook = clean_text(video.get("hook_text") or video.get("desc"))[:80].lower()
        if hook:
            hooks.append(hook)
    if not hooks:
        return 0.0
    counts = Counter(hooks)
    repeated = sum(count for count in counts.values() if count >= 2)
    return repeated / len(hooks)


def compute_weekly_baseline_delta(videos: list[dict]) -> dict[str, Any]:
    compare = compare_latest_two_weeks(videos)
    latest_rows = compare.get("latest_rows") or []
    prior_rows = compare.get("prior_rows") or []
    latest_lane = dominant_lane(latest_rows)
    prior_lane = dominant_lane(prior_rows)
    metrics = {
        "latest_post_count": len(latest_rows),
        "prior_post_count": len(prior_rows),
        "post_count_delta": len(latest_rows) - len(prior_rows),
        "latest_avg_score": round(avg_metric(latest_rows, "score"), 1),
        "prior_avg_score": round(avg_metric(prior_rows, "score"), 1),
        "avg_score_delta": round(avg_metric(latest_rows, "score") - avg_metric(prior_rows, "score"), 1),
        "latest_avg_likes": round(avg_metric(latest_rows, "digg_count"), 1),
        "prior_avg_likes": round(avg_metric(prior_rows, "digg_count"), 1),
        "avg_likes_delta": round(avg_metric(latest_rows, "digg_count") - avg_metric(prior_rows, "digg_count"), 1),
        "latest_top_lane": latest_lane,
        "prior_top_lane": prior_lane,
        "lane_shift": bool(prior_lane and latest_lane and prior_lane != latest_lane),
        "latest_repeated_hook_ratio": round(repeated_hook_ratio(latest_rows), 2),
        "prior_repeated_hook_ratio": round(repeated_hook_ratio(prior_rows), 2),
    }
    anomalies = build_weekly_anomalies(compare, metrics)
    return {
        **compare,
        "metrics": metrics,
        "anomalies": anomalies,
        "summary": baseline_delta_summary(compare, metrics, anomalies),
    }


def build_weekly_anomalies(compare: dict, metrics: dict) -> list[dict]:
    anomalies: list[dict] = []
    mode = clean_text(compare.get("mode"))
    latest_week = clean_text(compare.get("latest_week"))
    prior_week = clean_text(compare.get("prior_week"))

    if mode == "baseline":
        anomalies.append(
            {
                "alert_type": "baseline_only",
                "signal": "仅基线周",
                "severity": "medium",
                "detail": f"{latest_week} 尚无上周同字段对照",
                "meaning": "当前只能建立观察基线，不能断言策略已经切换。",
                "follow_up": "下周按同字段复采后再做 change-first 分发。",
            }
        )
        return anomalies

    if mode == "none":
        anomalies.append(
            {
                "alert_type": "insufficient_weeks",
                "signal": "周样本不足",
                "severity": "medium",
                "detail": "当前包里没有可比较的自然周标签",
                "meaning": "无法做 change-first 周度异动判断。",
                "follow_up": "补 publish_week 或 created_at_utc 后再复采。",
            }
        )
        return anomalies

    if mode != "compare":
        return anomalies

    if metrics.get("lane_shift"):
        anomalies.append(
            {
                "alert_type": "packaging_lane_shift",
                "signal": "包装主线切换",
                "severity": "high",
                "detail": f"{prior_week}={metrics.get('prior_top_lane')} -> {latest_week}={metrics.get('latest_top_lane')}",
                "meaning": "竞品/账号可能正在测试新的内容包装主线，而不只是单条爆点。",
                "follow_up": "优先拆本周头部样本，确认新主线是否可迁移。",
            }
        )

    if safe_int(metrics.get("post_count_delta")) >= 2:
        anomalies.append(
            {
                "alert_type": "posting_volume_jump",
                "signal": "发帖量上升",
                "severity": "medium",
                "detail": f"本周 {metrics.get('latest_post_count')} 条 vs 上周 {metrics.get('prior_post_count')} 条",
                "meaning": "发布节奏加快，可能是在押注某个新包装或新话题带。",
                "follow_up": "对照本周头部包装线，看放量是否集中在同一模式。",
            }
        )
    elif safe_int(metrics.get("post_count_delta")) <= -2:
        anomalies.append(
            {
                "alert_type": "posting_volume_drop",
                "signal": "发帖量回落",
                "severity": "medium",
                "detail": f"本周 {metrics.get('latest_post_count')} 条 vs 上周 {metrics.get('prior_post_count')} 条",
                "meaning": "发布节奏放缓，可能是测试收敛或账号进入观察期。",
                "follow_up": "不要把单周减量直接解读为策略失败，先看剩余样本质量。",
            }
        )

    if float(metrics.get("avg_likes_delta") or 0) >= 500:
        anomalies.append(
            {
                "alert_type": "engagement_lift",
                "signal": "互动均值抬升",
                "severity": "high",
                "detail": f"平均点赞 {metrics.get('prior_avg_likes')} -> {metrics.get('latest_avg_likes')}",
                "meaning": "整体互动抬升，说明本周内容不只是单条偶然爆点。",
                "follow_up": "继续追本周头部包装线，并检查是否伴随评论侧信任/质疑变化。",
            }
        )
    elif float(metrics.get("avg_likes_delta") or 0) <= -500:
        anomalies.append(
            {
                "alert_type": "engagement_drop",
                "signal": "互动均值回落",
                "severity": "medium",
                "detail": f"平均点赞 {metrics.get('prior_avg_likes')} -> {metrics.get('latest_avg_likes')}",
                "meaning": "整体互动走弱，需要区分是包装失效还是发布节奏变化。",
                "follow_up": "对照高低表现样本与发布时间窗，再决定下周测试方向。",
            }
        )

    hook_jump = float(metrics.get("latest_repeated_hook_ratio") or 0) - float(metrics.get("prior_repeated_hook_ratio") or 0)
    if hook_jump >= 0.25:
        anomalies.append(
            {
                "alert_type": "hook_convergence",
                "signal": "Hook 收敛",
                "severity": "medium",
                "detail": f"重复 hook 占比 {metrics.get('prior_repeated_hook_ratio')} -> {metrics.get('latest_repeated_hook_ratio')}",
                "meaning": "品类可能在跟风同一开头或同一包装句式。",
                "follow_up": "判断这是可复用规律还是已经拥挤的跟风角度。",
            }
        )

    if not anomalies:
        anomalies.append(
            {
                "alert_type": "stable_week",
                "signal": "周度稳定",
                "severity": "low",
                "detail": f"{latest_week} vs {prior_week} 未过异动阈值",
                "meaning": "本周没有明显策略级异常，适合沿用站立队列。",
                "follow_up": "保持同字段复采，等待下一轮显著变化再升级动作。",
            }
        )
    return anomalies


def baseline_delta_summary(compare: dict, metrics: dict, anomalies: list[dict]) -> str:
    if compare.get("mode") == "baseline":
        return f"Baseline week {clean_text(compare.get('latest_week'))}; hold strategy conclusions until next week."
    high_signals = [clean_text(item.get("signal")) for item in anomalies if clean_text(item.get("severity")) == "high"]
    if high_signals:
        return f"{clean_text(compare.get('latest_week'))} vs {clean_text(compare.get('prior_week'))}: " + ", ".join(high_signals)
    return (
        f"{clean_text(compare.get('latest_week'))} vs {clean_text(compare.get('prior_week'))}: "
        f"posts {metrics.get('post_count_delta'):+d}, avg likes {metrics.get('avg_likes_delta'):+.0f}"
    )


def weekly_anomaly_digest_rows(delta: dict, *, limit: int = 4) -> list[list[str]]:
    rows: list[list[str]] = []
    metrics = delta.get("metrics") or {}
    if delta.get("mode") == "compare":
        rows.append(
            [
                "周度基线",
                f"{clean_text(delta.get('latest_week'))} vs {clean_text(delta.get('prior_week'))}",
                (
                    f"发帖 {metrics.get('prior_post_count')}→{metrics.get('latest_post_count')}；"
                    f"均赞 {metrics.get('prior_avg_likes')}→{metrics.get('latest_avg_likes')}"
                ),
                "是" if any(item.get("severity") == "high" for item in delta.get("anomalies") or []) else "先观察",
            ]
        )
    for item in (delta.get("anomalies") or [])[:limit]:
        rows.append(
            [
                clean_text(item.get("signal")) or "异动",
                clean_text(item.get("detail")) or clean_text(item.get("meaning")),
                clean_text(item.get("follow_up")) or clean_text(item.get("meaning")),
                "是" if clean_text(item.get("severity")) == "high" else "视情况",
            ]
        )
    return rows[: limit + 1]


def ensure_weekly_baseline_artifact(capture_root: Path, videos: list[dict]) -> dict[str, Any]:
    delta = compute_weekly_baseline_delta(videos)
    if capture_root.exists():
        write_json_file(capture_root / "weekly_baseline_delta.json", delta)
    return delta
