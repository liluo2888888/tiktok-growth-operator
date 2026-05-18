from __future__ import annotations

from pathlib import Path

from pack_video_text import clean_text, core_topic_text, hook_text, sentence_clip
from text_normalization import write_json_file


CATEGORY_ENTRY_BOARD_HEADERS = [
    "行类型",
    "进入判断",
    "需求热度",
    "供给拥挤度",
    "信号摘要",
    "代表内容",
    "建议动作",
    "优先级",
    "视频链接",
    "备注",
]


def build_category_entry_board_payload(
    *,
    saturation: dict,
    top_ranked: list[dict],
    comment_count: int = 0,
    append_scope_key: str = "",
    provenance_fn=None,
) -> dict:
    signals = saturation.get("signals") or {}
    rows: list[list[str]] = [
        [
            "类目判断",
            clean_text(saturation.get("verdict")) or "观察",
            clean_text(saturation.get("demand_heat")) or "中",
            clean_text(saturation.get("supply_pressure")) or "中",
            f"重复hook={signals.get('repeated_hook_share')} | 头部账号={signals.get('top_creator_share')} | 评论={comment_count}",
            "",
            clean_text(saturation.get("recommended_action")) or "",
            "高",
            "",
            clean_text(saturation.get("verdict_code")) or "",
        ]
    ]
    for index, video in enumerate(top_ranked[:3]):
        prov = provenance_fn(video) if provenance_fn else ""
        rows.append(
            [
                "头部样本",
                clean_text(saturation.get("verdict")) or "观察",
                clean_text(saturation.get("demand_heat")) or "中",
                clean_text(saturation.get("supply_pressure")) or "中",
                f"score={video.get('score', 0)} | likes={safe_int(video.get('digg_count'))}",
                sentence_clip(hook_text(video) or core_topic_text(video), limit=88) or "线索缺失",
                "优先做" if index == 0 else "做",
                "高" if index == 0 else "中",
                clean_text(video.get("video_url") or video.get("video_id")),
                prov,
            ]
        )
    return {
        "schema_version": "scene07-category-entry-board-v1",
        "headers": CATEGORY_ENTRY_BOARD_HEADERS,
        "rows": rows,
        "row_count": len(rows),
        "append_scope_key": append_scope_key,
        "verdict": clean_text(saturation.get("verdict")),
    }


def safe_int(value: object) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def persist_category_entry_board_exports(capture_root: Path, board: dict) -> dict[str, str]:
    json_path = capture_root / "category_entry_board.json"
    write_json_file(json_path, board)
    return {"json": str(json_path)}
