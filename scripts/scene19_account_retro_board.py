from __future__ import annotations

from pathlib import Path

from pack_video_text import clean_text, sentence_clip
from text_normalization import write_json_file
from weekly_baseline import publish_week_label


ACCOUNT_RETRO_BOARD_HEADERS = [
    "调度动作",
    "内容模式",
    "时间窗口",
    "关键信号",
    "执行说明",
    "转化信号",
    "ROI信号",
    "比较周",
    "优先级",
]


def _signal_label(value: object) -> str:
    text = clean_text(value)
    if not text:
        return "未恢复"
    mapping = {
        "strong": "强",
        "medium": "中",
        "weak": "弱",
        "high": "高",
        "low": "低",
    }
    return mapping.get(text.lower(), text)


def _window_label(video: dict, *, fallback: str = "") -> str:
    return clean_text(video.get("publish_window")) or publish_week_label(video) or fallback or "未标记"


def build_account_retro_board_payload(
    *,
    dispatch_rows: list[list[str]],
    compare: dict,
    high_video: dict,
    low_video: dict,
    roi_cluster_rows: list[list[str]] | None = None,
    evidence_grade: str = "",
    append_scope_key: str = "",
) -> dict:
    latest_week = clean_text(compare.get("latest_week")) or "本周"
    prior_week = clean_text(compare.get("prior_week"))
    window = f"{latest_week} vs {prior_week}" if compare.get("mode") == "compare" and prior_week else f"{latest_week} 基线"
    rows: list[list[str]] = []
    for dispatch in dispatch_rows:
        if not isinstance(dispatch, list) or len(dispatch) < 4:
            continue
        action = clean_text(dispatch[0])
        priority = "高" if "多做" in action else ("低" if "停止" in action else "中")
        rows.append(
            [
                action,
                clean_text(dispatch[1]),
                window,
                sentence_clip(clean_text(dispatch[2]), limit=100),
                clean_text(dispatch[3]),
                _signal_label(high_video.get("conversion_proxy")) if "多做" in action else _signal_label(low_video.get("conversion_proxy")),
                _signal_label(high_video.get("roi_proxy")) if "多做" in action else _signal_label(low_video.get("roi_proxy")),
                window,
                priority,
            ]
        )
    for cluster in (roi_cluster_rows or [])[:2]:
        if not isinstance(cluster, list) or len(cluster) < 4:
            continue
        rows.append(
            [
                "模式簇",
                clean_text(cluster[0]),
                clean_text(cluster[3]) if len(cluster) > 3 else "",
                sentence_clip(clean_text(cluster[1]), limit=100),
                clean_text(cluster[2]) if len(cluster) > 2 else "",
                "",
                "",
                window,
                "中",
            ]
        )
    if not rows:
        rows.append(
            [
                "观察",
                "样本不足",
                window,
                "",
                "先补两周同字段样本",
                "",
                "",
                window,
                "低",
            ]
        )
    return {
        "schema_version": "scene19-account-retro-board-v1",
        "headers": ACCOUNT_RETRO_BOARD_HEADERS,
        "rows": rows,
        "row_count": len(rows),
        "append_scope_key": append_scope_key,
        "compare_mode": clean_text(compare.get("mode")),
        "latest_week": latest_week,
        "evidence_grade": evidence_grade,
    }


def persist_account_retro_board_exports(capture_root: Path, board: dict) -> dict[str, str]:
    json_path = capture_root / "account_retro_board.json"
    write_json_file(json_path, board)
    return {"json": str(json_path)}
