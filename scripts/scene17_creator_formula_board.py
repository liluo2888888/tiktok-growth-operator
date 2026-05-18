from __future__ import annotations

from pathlib import Path

from pack_video_text import clean_text, hook_text, sentence_clip
from text_normalization import write_json_file


CREATOR_FORMULA_BOARD_HEADERS = [
    "行类型",
    "公式/聚类",
    "包装线",
    "原始钩子",
    "可套用模板",
    "强势发布时间",
    "来源",
    "运营动作",
    "优先级",
]


def build_creator_formula_board_payload(
    *,
    formula_rows: list[list[str]],
    cluster_rows: list[list[str]],
    append_scope_key: str = "",
) -> dict:
    rows: list[list[str]] = []
    for item in formula_rows:
        if not isinstance(item, list) or len(item) < 5:
            continue
        rows.append(
            [
                "公式库",
                clean_text(item[0]),
                "",
                sentence_clip(clean_text(item[1]), limit=88),
                clean_text(item[2]),
                clean_text(item[3]),
                clean_text(item[4]),
                "写脚本 / 测版",
                "高",
            ]
        )
    for item in cluster_rows:
        if not isinstance(item, list) or len(item) < 4:
            continue
        rows.append(
            [
                "系列簇",
                clean_text(item[0]),
                f"样本数={clean_text(item[1])}",
                sentence_clip(clean_text(item[2]), limit=88),
                "",
                "",
                "",
                clean_text(item[3]),
                "高" if clean_text(item[3]) == "优先蒸馏" else "中",
            ]
        )
    if not rows:
        rows.append(["公式库", "待补", "", "", "先补创作者样本", "", "", "观察", "低"])
    return {
        "schema_version": "scene17-creator-formula-board-v1",
        "headers": CREATOR_FORMULA_BOARD_HEADERS,
        "rows": rows,
        "row_count": len(rows),
        "append_scope_key": append_scope_key,
    }


def persist_creator_formula_board_exports(capture_root: Path, board: dict) -> dict[str, str]:
    json_path = capture_root / "creator_formula_board.json"
    write_json_file(json_path, board)
    return {"json": str(json_path)}
