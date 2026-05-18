from __future__ import annotations

from collections import Counter
from pathlib import Path

from pack_video_text import clean_text, core_topic_text, hashtags_text, hook_text, proof_style_text, sentence_clip
from text_normalization import write_json_file


def _rhythm_label(video: dict) -> str:
    caption = clean_text(video.get("caption_text") or video.get("desc"))
    if len(caption) > 140:
        return "中长 caption / 偏解释"
    if len(caption) < 40:
        return "短 caption / 识别优先"
    return "标准短节拍"


def _conversion_phrase(video: dict) -> str:
    tags = hashtags_text(video)
    shop = clean_text(video.get("tkshop_signal"))
    if shop and shop != "未检测到":
        return f"带货信号={shop}"
    if tags:
        return f"话题收口={tags}"
    return "延续式 CTA / 继续看"


def cross_video_matrix_rows(videos: list[dict]) -> list[list[str]]:
    rows: list[list[str]] = []
    for index, video in enumerate(videos[:3], start=1):
        rows.append(
            [
                f"样本 {index}",
                clean_text(video.get("video_url") or video.get("video_id")) or f"shortlist-{index}",
                sentence_clip(hook_text(video), limit=72) or "钩子待补",
                sentence_clip(core_topic_text(video), limit=64) or "主题待补",
                proof_style_text(video),
                _rhythm_label(video),
                _conversion_phrase(video),
                clean_text(video.get("shortlist_decision")) or "立即深拆",
            ]
        )
    return rows


def pattern_convergence_rows(videos: list[dict]) -> list[list[str]]:
    if not videos:
        return [["共性维度", "—", "样本不足", "—", "low"]]
    hooks = [sentence_clip(hook_text(video), limit=48) for video in videos if hook_text(video)]
    proofs = [proof_style_text(video) for video in videos]
    rhythms = [_rhythm_label(video) for video in videos]
    hook_counter = Counter(hooks)
    proof_counter = Counter(proofs)
    rhythm_counter = Counter(rhythms)
    dominant_hook = hook_counter.most_common(1)[0][0] if hook_counter else "钩子证据不足"
    dominant_proof = proof_counter.most_common(1)[0][0] if proof_counter else "证明装置不稳定"
    dominant_rhythm = rhythm_counter.most_common(1)[0][0] if rhythm_counter else "节奏标签不足"
    return [
        ["开头钩子", dominant_hook, "跨样本重复出现的首屏识别方式", "新脚本必须先复刻识别，再换主题", "medium"],
        ["证明段", dominant_proof, "跨样本共用的信任转移装置", "把借来的账号势能换成自有 proof", "medium"],
        ["节奏", dominant_rhythm, "caption 长度与节拍偏好", "避免把单条长解释误当成品类规律", "medium"],
        ["转化收口", _conversion_phrase(videos[0]), "当前 shortlist 更偏研究还是偏带货", "强卖 CTA 可能破坏原生适配", "low-to-medium"],
    ]


def build_creation_matrix_payload(videos: list[dict]) -> dict:
    matrix_rows = cross_video_matrix_rows(videos)
    pattern_rows = pattern_convergence_rows(videos)
    return {
        "schema_version": "scene03-creation-matrix-v1",
        "sample_count": len(videos[:3]),
        "matrix_rows": matrix_rows,
        "pattern_convergence": pattern_rows,
        "creation_ready": bool(matrix_rows) and bool(hook_text(videos[0]) if videos else False),
        "recommended_next": "把共性规律表直接映射到新脚本四段：钩子 / 铺垫 / 证明 / 收口",
    }


def write_scene03_creation_matrix(capture_root: Path | None, videos: list[dict]) -> Path | None:
    if capture_root is None:
        return None
    payload = build_creation_matrix_payload(videos)
    output = capture_root / "scene03_creation_matrix.json"
    write_json_file(output, payload)
    return output
