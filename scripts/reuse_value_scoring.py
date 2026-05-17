from __future__ import annotations

import math
from typing import Any

from text_normalization import normalize_text


def clean_text(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        return " ".join(part for part in (clean_text(item) for item in value) if part).strip()
    return normalize_text(value)


def safe_int(value: object) -> int:
    if isinstance(value, bool):
        return int(value)
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return max(lower, min(upper, value))


def log_ratio(value: int, full_at: int) -> float:
    if value <= 0 or full_at <= 0:
        return 0.0
    return clamp(math.log10(value + 1) / math.log10(full_at + 1))


def looks_like_sentence(text: str) -> bool:
    letters = [char for char in text if char.isalnum()]
    return len(letters) >= 12


def contains_any(text: str, patterns: list[str]) -> bool:
    lowered = text.lower()
    return any(pattern in lowered for pattern in patterns)


def percent_score(value: float) -> int:
    return int(round(clamp(value) * 100))


def label_from_score(score: int) -> str:
    if score >= 80:
        return "strong"
    if score >= 60:
        return "good"
    if score >= 40:
        return "mixed"
    return "weak"


def candidate_text_fields(video: dict) -> list[str]:
    return [
        clean_text(video.get("caption_text")),
        clean_text(video.get("hook_text")),
        clean_text(video.get("core_topic")),
        clean_text(video.get("desc")),
    ]


def caption_completeness_score(video: dict) -> float:
    texts = candidate_text_fields(video)
    non_empty = [text for text in texts if text]
    distinct = list(dict.fromkeys(non_empty))
    long_fields = sum(1 for text in distinct if looks_like_sentence(text))
    hashtags = video.get("hashtags") or []
    base = len(distinct) / max(len(texts), 1)
    depth = clamp(long_fields / 2.0)
    hashtag_bonus = clamp(len(hashtags) / 4.0) * 0.15
    return clamp(base * 0.55 + depth * 0.30 + hashtag_bonus)


def enrichment_score(video: dict) -> float:
    points = 0.0
    if clean_text(video.get("downloaded_metadata_path")):
        points += 0.35
    if clean_text(video.get("metadata_source")):
        points += 0.10
    if clean_text(video.get("author_signature")):
        points += 0.15
    if clean_text(video.get("music_title")):
        points += 0.10
    if video.get("hashtags"):
        points += 0.15
    if clean_text(video.get("cover_url")):
        points += 0.05
    if clean_text(video.get("play_addr")):
        points += 0.10
    return clamp(points)


def authority_score(video: dict) -> float:
    score = 0.0
    if video.get("author_verified"):
        score += 0.55
    if clean_text(video.get("author_signature")):
        score += 0.20
    follower_count = safe_int(video.get("author_follower_count"))
    if follower_count:
        score += clamp(log_ratio(follower_count, 1_000_000) * 0.25)
    return clamp(score)


def commerce_signal_score(video: dict) -> float:
    text = " ".join(candidate_text_fields(video))
    keywords = [
        "shop",
        "tiktok shop",
        "amazon",
        "buy",
        "order",
        "discount",
        "link in bio",
        "cart",
        "price",
        "deal",
    ]
    raw_signal = safe_int(video.get("is_ec_video"))
    keyword_score = 0.55 if contains_any(text, keywords) else 0.0
    raw_score = 0.60 if raw_signal else 0.0
    return clamp(max(keyword_score, raw_score))


def comment_density_score(video: dict) -> float:
    digg_count = safe_int(video.get("digg_count"))
    comment_count = safe_int(video.get("comment_count"))
    share_count = safe_int(video.get("share_count"))
    play_count = safe_int(video.get("play_count"))
    comment_like_ratio = comment_count / max(digg_count, 1)
    share_like_ratio = share_count / max(digg_count, 1)
    comment_play_ratio = comment_count / max(play_count, 1)
    density = (
        clamp(comment_like_ratio / 0.03) * 0.45
        + clamp(share_like_ratio / 0.10) * 0.35
        + clamp(comment_play_ratio / 0.0025) * 0.20
    )
    return clamp(density)


def proof_strength_score(video: dict) -> float:
    text = " ".join(candidate_text_fields(video))
    proof_keywords = [
        "before",
        "after",
        "results",
        "tested",
        "review",
        "proof",
        "comparison",
        "vs",
        "did this work",
        "worth it",
    ]
    keyword_score = 0.45 if contains_any(text, proof_keywords) else 0.0
    return clamp(keyword_score + authority_score(video) * 0.30 + comment_density_score(video) * 0.35)


def series_potential_score(video: dict) -> float:
    text = " ".join(candidate_text_fields(video))
    patterns = [
        "part ",
        "episode",
        "day ",
        "ways to",
        "3 ",
        "5 ",
        "things",
        "how to",
        "pov",
        "?",
    ]
    pattern_score = 0.60 if contains_any(text, patterns) else 0.0
    hashtag_bonus = clamp(len(video.get("hashtags") or []) / 5.0) * 0.20
    hook_bonus = 0.20 if looks_like_sentence(clean_text(video.get("hook_text"))) else 0.0
    return clamp(pattern_score + hashtag_bonus + hook_bonus)


def portability_score(video: dict) -> float:
    hook = clean_text(video.get("hook_text"))
    desc = clean_text(video.get("desc"))
    text = f"{hook} {desc}".strip()
    base = 0.25
    if looks_like_sentence(hook):
        base += 0.30
    if clean_text(video.get("core_topic")):
        base += 0.15
    if video.get("hashtags"):
        base += 0.10
    if "@" in text:
        base -= 0.20
    if contains_any(text, ["follow me", "follow for", "subscribe", "my channel"]):
        base -= 0.15
    return clamp(base)


def topic_spread_score(video: dict) -> float:
    hashtags = video.get("hashtags") or []
    hashtag_score = clamp(len(hashtags) / 5.0) * 0.55
    topic_bonus = 0.25 if clean_text(video.get("core_topic")) else 0.0
    hook_bonus = 0.20 if clean_text(video.get("hook_text")) and clean_text(video.get("hook_text")) != clean_text(video.get("core_topic")) else 0.0
    return clamp(hashtag_score + topic_bonus + hook_bonus)


def popularity_score(video: dict) -> float:
    digg_count = safe_int(video.get("digg_count"))
    comment_count = safe_int(video.get("comment_count"))
    share_count = safe_int(video.get("share_count"))
    play_count = safe_int(video.get("play_count"))
    return clamp(
        log_ratio(digg_count, 2_000_000) * 0.45
        + log_ratio(comment_count, 50_000) * 0.20
        + log_ratio(share_count, 250_000) * 0.20
        + log_ratio(play_count, 120_000_000) * 0.15
    )


def popularity_first_rank_key(video: dict) -> tuple[int, int, int, int]:
    return (
        safe_int(video.get("digg_count")),
        safe_int(video.get("comment_count")),
        safe_int(video.get("share_count")),
        safe_int(video.get("play_count")),
    )


def reuse_value_rank_key(video: dict) -> tuple[int, int, int, int]:
    return (
        safe_int(video.get("reuse_value_score")),
        safe_int(video.get("commerce_confidence")),
        safe_int(video.get("popularity_score")),
        safe_int(video.get("digg_count")),
    )


def commerce_label(score: int) -> str:
    if score >= 70:
        return "clear"
    if score >= 40:
        return "possible"
    return "low"


def strongest_dimension_labels(breakdown: dict[str, int]) -> list[str]:
    labels = {
        "caption_completeness": "caption/hook completeness",
        "enrichment": "download enrichment",
        "comment_density": "comment density",
        "authority_signal": "authority signal",
        "proof_strength": "proof strength",
        "series_potential": "series potential",
        "portability": "portable format",
        "topic_spread": "topic spread",
        "commerce_signal": "commerce intent",
        "popularity": "market traction",
    }
    ordered = sorted(breakdown.items(), key=lambda item: item[1], reverse=True)
    winners: list[str] = []
    for key, value in ordered:
        if value < 45:
            continue
        label = labels.get(key, key)
        if label not in winners:
            winners.append(label)
        if len(winners) >= 3:
            break
    return winners


def decide_reuse_value_label(video: dict, breakdown: dict[str, int]) -> str:
    if breakdown.get("commerce_signal", 0) >= 65:
        return "Commerce / conversion teardown"
    if breakdown.get("authority_signal", 0) >= 65 or breakdown.get("proof_strength", 0) >= 65:
        return "Proof / authority teardown"
    if breakdown.get("series_potential", 0) >= 65:
        return "Series / format cloning study"
    if breakdown.get("caption_completeness", 0) >= 60:
        return "Hook / caption / packaging study"
    return "Hook / packaging study"


def decide_reuse_purpose(video: dict, breakdown: dict[str, int]) -> str:
    if breakdown.get("commerce_signal", 0) >= 65:
        return "Keep the conversion setup, then rewrite the offer proof and CTA with your own product facts."
    if breakdown.get("authority_signal", 0) >= 65:
        return "Map the authority cue and replace borrowed trust with one owned proof object, creator, or testimonial."
    if breakdown.get("series_potential", 0) >= 65:
        return "Turn the winning hook into a repeatable episode format and test multiple proof variants around it."
    if breakdown.get("portability", 0) >= 65:
        return "Preserve the recognition-first hook and swap the original topic or person for an owned use case."
    return "Study the hook, proof placement, and pacing before adapting the structure to your own asset set."


def explain_selection(video: dict, breakdown: dict[str, int]) -> str:
    reasons = strongest_dimension_labels(breakdown)
    if not reasons:
        reasons = ["market traction", "portable packaging"]
    metrics = []
    for label, key in [("likes", "digg_count"), ("comments", "comment_count"), ("shares", "share_count")]:
        value = safe_int(video.get(key))
        if value:
            metrics.append(f"{label}={value}")
    metric_text = ", ".join(metrics[:3])
    reason_text = ", ".join(reasons[:3])
    if metric_text:
        return f"Selected for {reason_text}; supporting traction: {metric_text}."
    return f"Selected for {reason_text}."


def score_breakdown(video: dict) -> dict[str, int]:
    return {
        "caption_completeness": percent_score(caption_completeness_score(video)),
        "enrichment": percent_score(enrichment_score(video)),
        "comment_density": percent_score(comment_density_score(video)),
        "authority_signal": percent_score(authority_score(video)),
        "proof_strength": percent_score(proof_strength_score(video)),
        "series_potential": percent_score(series_potential_score(video)),
        "portability": percent_score(portability_score(video)),
        "topic_spread": percent_score(topic_spread_score(video)),
        "commerce_signal": percent_score(commerce_signal_score(video)),
        "popularity": percent_score(popularity_score(video)),
    }


def final_score_from_breakdown(breakdown: dict[str, int]) -> int:
    weights = {
        "caption_completeness": 0.16,
        "enrichment": 0.10,
        "comment_density": 0.08,
        "authority_signal": 0.08,
        "proof_strength": 0.10,
        "series_potential": 0.10,
        "portability": 0.10,
        "topic_spread": 0.08,
        "commerce_signal": 0.08,
        "popularity": 0.12,
    }
    total = 0.0
    for key, weight in weights.items():
        total += breakdown.get(key, 0) * weight
    return int(round(total))


def apply_reuse_value_scoring(videos: list[dict]) -> list[dict]:
    rescored: list[dict] = []
    for video in videos:
        if not isinstance(video, dict):
            continue
        breakdown = score_breakdown(video)
        popularity = breakdown.get("popularity", 0)
        reuse_value = final_score_from_breakdown(breakdown)
        commerce_score = breakdown.get("commerce_signal", 0)
        enriched = dict(video)
        enriched["popularity_score"] = popularity
        enriched["reuse_value_score"] = reuse_value
        enriched["score"] = reuse_value
        enriched["score_breakdown"] = breakdown
        enriched["score_breakdown_text"] = ", ".join(f"{key}={value}" for key, value in breakdown.items())
        enriched["caption_quality"] = label_from_score(breakdown.get("caption_completeness", 0))
        enriched["proof_strength"] = label_from_score(breakdown.get("proof_strength", 0))
        enriched["shopping_intent"] = commerce_label(commerce_score)
        enriched["tkshop_signal"] = "present" if commerce_score >= 60 or safe_int(enriched.get("is_ec_video")) else "not_detected"
        enriched["commerce_confidence"] = commerce_score
        enriched["reuse_value_label"] = decide_reuse_value_label(enriched, breakdown)
        enriched["reuse_purpose"] = decide_reuse_purpose(enriched, breakdown)
        enriched["why_selected"] = explain_selection(enriched, breakdown)
        enriched["why_worth_studying"] = enriched["why_selected"]
        enriched["best_reuse_category"] = enriched["reuse_value_label"]
        enriched["scene03_reason"] = enriched["why_selected"]
        rescored.append(enriched)

    rescored.sort(key=reuse_value_rank_key, reverse=True)
    for index, item in enumerate(rescored, start=1):
        item["profile_rank"] = index
        item["reuse_rank"] = index
    return rescored


def align_qualified_to_ranked(ranked_videos: list[dict], qualified_videos: list[dict]) -> list[dict]:
    if not qualified_videos:
        return qualified_videos
    ranked_by_url = {
        clean_text(item.get("video_url")): item
        for item in ranked_videos
        if clean_text(item.get("video_url"))
    }
    rank_index = {url: index for index, url in enumerate(ranked_by_url)}
    aligned: list[dict] = []
    for item in qualified_videos:
        if not isinstance(item, dict):
            continue
        url = clean_text(item.get("video_url"))
        merged = dict(ranked_by_url.get(url, item))
        if url:
            merged["video_url"] = url
        aligned.append(merged)
    aligned.sort(key=lambda item: rank_index.get(clean_text(item.get("video_url")), 10_000))
    return aligned


def compare_rank_orders(videos: list[dict]) -> dict[str, Any]:
    popularity_order = [
        clean_text(item.get("video_url") or item.get("video_id"))
        for item in sorted(videos, key=popularity_first_rank_key, reverse=True)
        if clean_text(item.get("video_url") or item.get("video_id"))
    ]
    rescored = apply_reuse_value_scoring([dict(item) for item in videos])
    reuse_order = [
        clean_text(item.get("video_url") or item.get("video_id"))
        for item in rescored
        if clean_text(item.get("video_url") or item.get("video_id"))
    ]
    return {
        "popularity_first_order": popularity_order,
        "reuse_value_first_order": reuse_order,
        "order_changed": popularity_order != reuse_order,
        "top_reuse_value_score": safe_int(rescored[0].get("reuse_value_score")) if rescored else 0,
        "top_popularity_score": safe_int(rescored[0].get("popularity_score")) if rescored else 0,
    }
