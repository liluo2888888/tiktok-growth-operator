from __future__ import annotations

import json
import re

from text_normalization import normalize_nested, normalize_text


def clean_text(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        parts = [clean_text(item) for item in value]
        return "\n".join(item for item in parts if item)
    if isinstance(value, dict):
        return json.dumps(normalize_nested(value), ensure_ascii=False)
    return normalize_text(value)


def sentence_clip(text: str, limit: int = 120) -> str:
    cleaned = clean_text(text)
    if not cleaned:
        return ""
    compact = " ".join(cleaned.split())
    if len(compact) <= limit:
        return compact
    window = compact[:limit].rstrip()
    for marker in [". ", "! ", "? ", "。", "！", "？"]:
        pos = window.rfind(marker)
        if pos >= max(24, limit // 3):
            return window[: pos + 1].strip()
    if " " in window:
        return window.rsplit(" ", 1)[0].rstrip(" ,;:-") + "..."
    return window.rstrip(" ,;:-") + "..."


def hook_text(video: dict) -> str:
    for candidate in [video.get("hook_text"), video.get("caption_text"), video.get("desc"), video.get("core_topic")]:
        text = sentence_clip(clean_text(candidate), limit=128)
        if text:
            return text
    return ""


def core_topic_text(video: dict) -> str:
    for candidate in [video.get("core_topic"), video.get("caption_text"), video.get("desc")]:
        text = sentence_clip(clean_text(candidate), limit=92)
        if text:
            return text
    return ""


def author_signal_text(video: dict) -> str:
    verified = bool(video.get("author_verified"))
    unique_id = clean_text(video.get("unique_id"))
    if unique_id:
        return f"{unique_id}（{'已认证' if verified else '未认证'}）"
    if verified:
        return "已认证账号"
    signature = clean_text(video.get("author_signature"))
    return signature or "未认证账号"


def proof_style_text(video: dict) -> str:
    explicit = clean_text(video.get("reuse_value_label"))
    if explicit:
        return explicit
    if video.get("author_verified"):
        return "认证账号背书"
    if clean_text(video.get("author_signature")):
        return "创作者 / 品牌语境背书"
    return "以包装驱动为主，未恢复出强权威线索"


def hashtags_text(video: dict) -> str:
    tags = video.get("hashtags") or []
    if isinstance(tags, list):
        normalized = [f"#{clean_text(tag)}" for tag in tags if clean_text(tag)]
        if normalized:
            return ", ".join(normalized[:4])
    return ""
