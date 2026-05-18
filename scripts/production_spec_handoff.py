from __future__ import annotations

from pathlib import Path

from pack_video_text import author_signal_text, clean_text, core_topic_text, hook_text, proof_style_text, sentence_clip
from text_normalization import write_json_file


def pacing_map_rows(source: dict) -> list[list[str]]:
    hook = hook_text(source)
    topic = core_topic_text(source)
    proof = proof_style_text(source)
    return [
        ["0-3s", "hook_lock", "首屏识别锁定", hook or "首屏 cue 待补", "快切 / 硬切", "high", clean_text(source.get("video_url")) or "primary-video"],
        ["3-8s", "premise", "压缩前提", topic or "一句前提", "承接镜头", "medium", clean_text(source.get("video_url")) or "primary-video"],
        ["8-14s", "proof_push", "证明前置", proof, "证明物特写", "medium", clean_text(source.get("video_url")) or "primary-video"],
        ["14-20s", "soft_close", "轻收口", "继续看 / 保存 / 轻量关注", "回到主线索", "low", clean_text(source.get("video_url")) or "primary-video"],
    ]


def subtitle_beat_rows(source: dict) -> list[list[str]]:
    hook = hook_text(source)
    topic = core_topic_text(source)
    proof = proof_style_text(source)
    return [
        ["beat_01", "0-3s", "首屏字幕", hook or "识别句待补", "必须一眼可读", "medium"],
        ["beat_02", "3-8s", "前提字幕", sentence_clip(topic or hook, limit=72) or "前提句待补", "只补最少上下文", "medium"],
        ["beat_03", "8-14s", "证明字幕", sentence_clip(proof, limit=72), "证明优先于解释", "medium"],
        ["beat_04", "14-20s", "收口字幕", "继续看 / 了解更多", "低摩擦 CTA", "low"],
    ]


def proof_block_rows(source: dict) -> list[list[str]]:
    authority = author_signal_text(source)
    url = clean_text(source.get("video_url")) or "primary-video"
    return [
        ["proof_primary", "主证明块", proof_style_text(source), authority or "权威待补", "前半段必须出现", "medium", url],
        ["proof_support", "辅助证明", "结果 / 人物 / 凭证 / 动作", "可叠加但不抢主线索", "避免双主线", "low", url],
        ["proof_fallback", "无口播兜底", "字幕 + 切镜 + 动作节奏", "口播缺失时仍要能看懂", "需要截图或下载复核", "medium", url],
    ]


def asset_requirement_rows(source: dict) -> list[list[str]]:
    url = clean_text(source.get("video_url")) or "primary-video"
    has_download = bool(clean_text(source.get("download_addr")) or clean_text(source.get("play_addr")))
    return [
        ["hero_frame", "首屏主画面 / 封面", "必须", "high" if hook_text(source) else "medium", url],
        ["proof_asset", "证明物 / 人物 / 结果画面", "必须", "medium", url],
        ["subtitle_pack", "字幕叠字或 caption 证据", "建议", "medium", url],
        ["download_source", "可复核下载源", "建议" if has_download else "缺口", "low" if has_download else "high", url],
    ]


def generator_branch_payload(source: dict, *, scene_id: str) -> dict:
    hook = hook_text(source)
    topic = core_topic_text(source)
    proof = proof_style_text(source)
    shots = [
        {"id": "shot_01", "window": "0-3s", "role": "hero_hook", "visual": hook or "识别首屏", "dialogue": hook},
        {"id": "shot_02", "window": "3-8s", "role": "premise_setup", "visual": topic or "压缩前提", "dialogue": sentence_clip(topic, limit=84)},
        {"id": "shot_03", "window": "8-14s", "role": "proof_block", "visual": proof, "dialogue": proof},
        {"id": "shot_04", "window": "14-20s", "role": "cta_close", "visual": "软收口", "dialogue": "继续看 / 保存"},
    ]
    base_prompt = {
        "style": topic or "识别优先编辑包装",
        "environment": "社交原生、单前提、先识别后证明",
        "tone_pacing": "快 setup、早 proof、轻收口",
        "character": author_signal_text(source),
        "shots": shots,
        "confidence": "medium",
    }
    return {
        "scene_id": scene_id,
        "reference_video_url": clean_text(source.get("video_url")),
        "shot_list": shots,
        "pacing_map": [{"window": row[0], "beat": row[1], "goal": row[2], "cue": row[3]} for row in pacing_map_rows(source)],
        "subtitle_beats": [{"id": row[0], "window": row[1], "type": row[2], "line": row[3]} for row in subtitle_beat_rows(source)],
        "proof_blocks": [{"id": row[0], "label": row[1], "content": row[2]} for row in proof_block_rows(source)],
        "asset_requirements": [{"asset": row[0], "need": row[1], "priority": row[2]} for row in asset_requirement_rows(source)],
        "generator_branches": {
            "sora": {**base_prompt, "model_hint": "text-to-video", "duration_s": 20, "aspect": "9:16"},
            "veo": {**base_prompt, "model_hint": "text-to-video", "duration_s": 20, "aspect": "9:16"},
            "i2v": {
                **base_prompt,
                "model_hint": "image-to-video",
                "required_stills": ["hero_frame", "proof_asset"],
                "motion": "轻 zoom / pan，保持识别线索不被遮挡",
            },
        },
        "schema_version": "production-spec-handoff-v1",
    }


def write_production_handoff_artifacts(capture_root: Path | None, source: dict, *, scene_id: str) -> Path | None:
    if capture_root is None:
        return None
    pack = generator_branch_payload(source, scene_id=scene_id)
    output = capture_root / "production_spec_handoff.json"
    write_json_file(output, pack)
    return output


def handoff_table_bundle(source: dict) -> dict[str, list[list[str]]]:
    return {
        "pacing_map": pacing_map_rows(source),
        "subtitle_beats": subtitle_beat_rows(source),
        "proof_blocks": proof_block_rows(source),
        "asset_requirements": asset_requirement_rows(source),
    }
