from __future__ import annotations

from text_normalization import normalize_text
from scene_report_presets import evidence_ref


def clean_text(value: object) -> str:
    return normalize_text(value)


def clip_excerpt(value: object, limit: int = 160) -> str:
    text = clean_text(value)
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 1)].rstrip() + "…"


def video_hook_excerpt(video: dict) -> str:
    for key in ("hook_text", "caption_text", "core_topic", "desc", "why_selected"):
        text = clean_text(video.get(key))
        if text:
            return clip_excerpt(text)
    return ""


def merge_evidence_refs(section: dict, refs: list[dict]) -> None:
    if not refs:
        return
    bucket = section.setdefault("evidence_refs", [])
    seen: set[tuple[str, str, str]] = set()
    for item in bucket:
        if not isinstance(item, dict):
            continue
        seen.add(
            (
                clean_text(item.get("source_type")),
                clean_text(item.get("source_id")),
                clean_text(item.get("supports")),
            )
        )
    for item in refs:
        if not isinstance(item, dict):
            continue
        key = (
            clean_text(item.get("source_type")),
            clean_text(item.get("source_id")),
            clean_text(item.get("supports")),
        )
        if not key[0] or not key[2] or key in seen:
            continue
        bucket.append(item)
        seen.add(key)


def video_evidence_ref(
    video: dict,
    *,
    supports: str,
    time_range: str = "00:00-00:03",
    excerpt: str = "",
) -> dict:
    video_id = clean_text(video.get("video_id")) or clean_text(video.get("video_url")) or "video"
    return evidence_ref(
        "video",
        video_id,
        clean_text(video.get("video_url")),
        time_range,
        excerpt or video_hook_excerpt(video) or clean_text(video.get("desc")),
        supports,
    )


def creator_evidence_ref(
    video: dict,
    profile_summary: dict | None,
    *,
    supports: str,
    time_range: str = "account-sample-window",
    excerpt: str = "",
) -> dict:
    profile = profile_summary or {}
    source_id = clean_text(video.get("unique_id")) or clean_text(profile.get("profile_url")) or "creator"
    source_url = clean_text(profile.get("profile_url") or profile.get("profile_final_url") or video.get("profile_url"))
    if not excerpt:
        excerpt = clip_excerpt(
            f"{clean_text(video.get('nickname'))} | {clean_text(video.get('author_signature'))}".strip(" |")
        )
    return evidence_ref("creator", source_id, source_url, time_range, excerpt, supports)


def account_week_evidence_ref(
    *,
    week_label: str,
    source_url: str,
    source_id: str,
    supports: str,
    excerpt: str,
    time_range: str = "weekly-window",
) -> dict:
    return evidence_ref(
        "account_week",
        source_id or week_label or "account-week",
        source_url,
        time_range,
        clip_excerpt(excerpt),
        supports,
    )


def comment_evidence_ref(
    entry: dict,
    *,
    supports: str,
    time_range: str = "comment-thread",
    excerpt: str = "",
) -> dict:
    source_id = clean_text(entry.get("cid") or entry.get("comment_id") or entry.get("video_id")) or "comment"
    source_url = clean_text(entry.get("source_url") or entry.get("video_url"))
    if not excerpt:
        excerpt = clip_excerpt(entry.get("quote_text") or entry.get("text"))
    product = clean_text(entry.get("source_product") or entry.get("product_label"))
    if product:
        excerpt = f"{product}: {excerpt}".strip(": ").strip()
    return evidence_ref("comment", source_id, source_url, time_range, excerpt, supports)


def transcript_evidence_ref(
    video: dict,
    *,
    supports: str,
    time_range: str = "00:00-00:12",
    excerpt: str = "",
) -> dict:
    video_id = clean_text(video.get("video_id")) or "transcript"
    if not excerpt:
        excerpt = clip_excerpt(video.get("caption_text") or video.get("desc") or video.get("core_topic"))
    return evidence_ref(
        "transcript",
        f"{video_id}-script",
        clean_text(video.get("video_url")),
        time_range,
        excerpt,
        supports,
    )


def screenshot_evidence_ref(
    *,
    source_id: str,
    source_url: str,
    supports: str,
    excerpt: str,
    time_range: str = "visual-layer",
) -> dict:
    return evidence_ref("screenshot", source_id, source_url, time_range, clip_excerpt(excerpt), supports)
