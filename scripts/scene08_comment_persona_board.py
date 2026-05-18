from __future__ import annotations

from pathlib import Path

from text_normalization import normalize_text, write_json_file


COMMENT_PERSONA_BOARD_HEADERS = [
    "聚类类型",
    "主题",
    "运营落点",
    "代表原话",
    "回复压力",
    "样本说明",
    "优先级",
    "负责人",
]


def _cluster_row(cluster_type: str, cluster: dict | None, *, landing: str, owner: str, priority: str) -> list[str]:
    cluster = cluster if isinstance(cluster, dict) else {}
    entry = cluster.get("top_entry") if isinstance(cluster.get("top_entry"), dict) else {}
    return [
        cluster_type,
        normalize_text(cluster.get("theme")) or "待补",
        landing,
        normalize_text(entry.get("quote_text"))[:120] or "待补",
        normalize_text(entry.get("reply_signal")) or normalize_text(cluster.get("reply_pressure")) or "",
        f"样本数={cluster.get('count', '')}",
        priority,
        owner,
    ]


def build_comment_persona_board_payload(
    *,
    comment_snapshot: dict,
    bridge_rows: list[list[str]],
    sampled_video_count: int = 0,
    append_scope_key: str = "",
) -> dict:
    rows: list[list[str]] = []
    for bridge in bridge_rows:
        if isinstance(bridge, list) and len(bridge) >= 4:
            rows.append(
                [
                    normalize_text(bridge[0]),
                    normalize_text(bridge[1]),
                    normalize_text(bridge[2]),
                    normalize_text(bridge[3]),
                    "",
                    f"视频数={sampled_video_count}",
                    "高",
                    "content / operator",
                ]
            )
    if not rows:
        rows.append(
            _cluster_row(
                "购买因素",
                comment_snapshot.get("top_purchase_cluster"),
                landing="卖点 / 首屏承诺",
                owner="content",
                priority="高",
            )
        )
        rows.append(
            _cluster_row(
                "差评痛点",
                comment_snapshot.get("top_complaint_cluster"),
                landing="FAQ / 客服",
                owner="operator",
                priority="高",
            )
        )
        rows.append(
            _cluster_row(
                "信任背书",
                comment_snapshot.get("top_trust_cluster"),
                landing="证明段",
                owner="content",
                priority="中",
            )
        )
    return {
        "schema_version": "scene08-comment-persona-board-v1",
        "headers": COMMENT_PERSONA_BOARD_HEADERS,
        "rows": rows,
        "row_count": len(rows),
        "append_scope_key": append_scope_key,
        "sampled_video_count": sampled_video_count,
    }


def persist_comment_persona_board_exports(capture_root: Path, board: dict) -> dict[str, str]:
    json_path = capture_root / "comment_persona_board.json"
    write_json_file(json_path, board)
    return {"json": str(json_path)}
