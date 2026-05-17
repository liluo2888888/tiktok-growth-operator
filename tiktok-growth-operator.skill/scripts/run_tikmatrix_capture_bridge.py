from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime
import math
from pathlib import Path

from start_capture_pack_run import create_capture_pack_run
from text_normalization import normalize_nested, normalize_text, read_json_file, write_json_file, write_utf8_text


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Bridge real TikMatrix exports into a tiktok-growth-operator capture-pack and run one operator scene."
    )
    parser.add_argument("--profile-posts-json", required=True, help="TikMatrix profile_posts.json export path.")
    parser.add_argument("--scene", required=True, help="Operator scene id or `auto`.")
    parser.add_argument("--name", required=True, help="Short operator run name.")
    parser.add_argument("--project", required=True, help="Operator project title.")
    parser.add_argument("--comments-json", default="", help="Optional TikMatrix comments.json export path for one video.")
    parser.add_argument("--downloads-json", default="", help="Optional TikMatrix downloads.json export path.")
    parser.add_argument("--output-root", default="", help="Optional bridge root. A capture-pack and operator-run folder will be created inside it.")
    parser.add_argument("--platform", default="TikTok", help="Platform label for operator outputs.")
    parser.add_argument("--market", default="US", help="Market label for operator outputs.")
    parser.add_argument("--formats", default="md,docx,xlsx", help="Rendered operator output formats.")
    parser.add_argument("--operator-packs", default="", help="Optional explicit operator packs override.")
    parser.add_argument("--target-markets", default="", help="Optional target markets for scene 13.")
    parser.add_argument("--target-languages", default="", help="Optional target languages for scene 15.")
    parser.add_argument("--min-likes", type=int, default=50000, help="Minimum likes threshold for qualified videos in the bridged pack.")
    parser.add_argument("--qualified-count", type=int, default=3, help="Maximum number of qualified videos to keep.")
    parser.add_argument("--comment-sample-size", type=int, default=5, help="Maximum sampled top-level comments to keep.")
    return parser.parse_args()


def clean_text(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        return " ".join(part for part in (clean_text(item) for item in value) if part).strip()
    if isinstance(value, dict):
        return json.dumps(normalize_nested(value), ensure_ascii=False)
    return normalize_text(value)


def safe_int(value: object) -> int:
    if isinstance(value, bool):
        return int(value)
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def load_json(path: Path) -> dict | list:
    return read_json_file(path)


def maybe_load_json(path: Path) -> dict | list | None:
    if not path.exists():
        return None
    return load_json(path)


def ensure_root(output_root: str, skill_root: Path, run_name: str) -> Path:
    if output_root.strip():
        root = Path(output_root).expanduser().resolve()
    else:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        root = skill_root / "tmp" / f"{stamp}-tikmatrix-bridge-{run_name}"
    root.mkdir(parents=True, exist_ok=True)
    return root


def extract_video_desc(video: dict) -> str:
    title = clean_text(video.get("title"))
    if title:
        return title
    raw = video.get("raw") or {}
    for candidate in [
        raw.get("desc"),
        (raw.get("itemInfos") or {}).get("text"),
    ]:
        text = clean_text(candidate)
        if text:
            return text
    contents = raw.get("contents") or []
    merged = " ".join(
        clean_text(item.get("desc"))
        for item in contents
        if isinstance(item, dict) and clean_text(item.get("desc"))
    ).strip()
    return merged


def derive_video_url(profile_url: str, video: dict) -> str:
    raw = video.get("raw") or {}
    for candidate in [
        video.get("video_url"),
        (raw.get("shareMeta") or {}).get("canonical"),
        (raw.get("shareMeta") or {}).get("title"),
        (raw.get("share_info") or {}).get("url"),
    ]:
        text = clean_text(candidate)
        if text.startswith("https://www.tiktok.com/"):
            return text
    video_id = clean_text(video.get("video_id") or (raw.get("itemInfos") or {}).get("id") or raw.get("id"))
    if profile_url and video_id:
        return f"{profile_url.rstrip('/')}/video/{video_id}"
    return ""


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

    rescored.sort(
        key=lambda item: (
            safe_int(item.get("reuse_value_score")),
            safe_int(item.get("commerce_confidence")),
            safe_int(item.get("popularity_score")),
            safe_int(item.get("digg_count")),
        ),
        reverse=True,
    )
    for index, item in enumerate(rescored, start=1):
        item["profile_rank"] = index
    return rescored


def normalize_ranked_videos(profile_payload: dict) -> list[dict]:
    profile_url = clean_text(profile_payload.get("source_url"))
    videos = profile_payload.get("videos") or []
    normalized: list[dict] = []
    for video in videos:
        if not isinstance(video, dict):
            continue
        stats = video.get("stats") or {}
        raw = video.get("raw") or {}
        raw_stats = raw.get("stats") or {}
        author = video.get("author") or {}
        media = video.get("media") or {}
        normalized.append(
            {
                "profile_url": profile_url,
                "profile_index": 1,
                "profile_output_dir": str(Path(profile_payload.get("_source_path", "")).parent),
                "video_url": derive_video_url(profile_url, video),
                "video_id": clean_text(video.get("video_id") or (raw.get("itemInfos") or {}).get("id") or raw.get("id")),
                "unique_id": clean_text(author.get("unique_id") or author.get("uniqueId")),
                "nickname": clean_text(author.get("nickname") or author.get("nickName")),
                "desc": extract_video_desc(video),
                "caption_text": extract_video_desc(video),
                "hook_text": extract_video_desc(video),
                "core_topic": extract_video_desc(video),
                "created_at_utc": clean_text(video.get("create_time")),
                "digg_count": safe_int(stats.get("digg_count") or raw_stats.get("diggCount")),
                "comment_count": safe_int(stats.get("comment_count") or raw_stats.get("commentCount")),
                "collect_count": safe_int(raw_stats.get("collectCount")),
                "share_count": safe_int(stats.get("share_count") or raw_stats.get("shareCount")),
                "play_count": safe_int(stats.get("play_count") or raw_stats.get("playCount")),
                "play_addr": clean_text(media.get("url")),
                "download_addr": clean_text(media.get("url")),
                "cover_url": clean_text(media.get("cover")),
                "hashtags": extract_hashtags(video),
                "author_signature": clean_text(author.get("signature")),
                "author_verified": bool(author.get("verified")),
                "music_title": clean_text(video.get("music_title")),
                "author_follower_count": safe_int((raw.get("authorStats") or {}).get("followerCount") or (raw.get("authorStatsV2") or {}).get("followerCount")),
                "is_ec_video": safe_int((raw.get("itemInfos") or {}).get("isECVideo") or raw.get("isECVideo")),
                "metadata_source": "",
                "downloaded_metadata_path": "",
                "popularity_score": 0,
                "reuse_value_score": 0,
                "score": 0,
                "source": "tikmatrix_profile_posts",
            }
        )
    return apply_reuse_value_scoring(normalized)


def extract_hashtags(video_payload: dict) -> list[str]:
    raw = video_payload.get("raw") or {}
    tags: list[str] = []
    for item in raw.get("challengeInfoList") or []:
        if isinstance(item, dict):
            name = clean_text(item.get("challengeName"))
            if name and name not in tags:
                tags.append(name)
    for item in raw.get("textExtra") or []:
        if isinstance(item, dict):
            name = clean_text(item.get("HashtagName"))
            if name and name not in tags:
                tags.append(name)
    return tags


def build_core_topic(video_payload: dict) -> str:
    title = clean_text(video_payload.get("title"))
    if title:
        topic = title.split("#", 1)[0].strip()
        if topic:
            return topic[:140]
    author = video_payload.get("author") or {}
    music_title = clean_text(video_payload.get("music_title"))
    hashtags = extract_hashtags(video_payload)
    author_name = clean_text(author.get("nickname") or author.get("unique_id"))
    if author_name and music_title:
        return f"{author_name} | {music_title}"
    if hashtags:
        return ", ".join(f"#{tag}" for tag in hashtags[:4])
    return ""


def infer_hook_text(video_payload: dict) -> str:
    title = clean_text(video_payload.get("title"))
    if title:
        first_clause = title.split(".")[0].strip()
        if first_clause:
            return first_clause[:160]
    desc = extract_video_desc(video_payload)
    if desc:
        return desc[:160]
    topic = build_core_topic(video_payload)
    return topic[:160]


def enrich_ranked_videos_from_downloads(ranked_videos: list[dict], downloads_payload: list[dict]) -> list[dict]:
    metadata_by_video_id: dict[str, tuple[dict, str]] = {}
    for item in downloads_payload:
        if not isinstance(item, dict):
            continue
        video_id = clean_text(item.get("video_id"))
        metadata_path = clean_text(item.get("metadata_path"))
        if not video_id or not metadata_path:
            continue
        metadata = maybe_load_json(Path(metadata_path))
        if isinstance(metadata, dict):
            metadata_by_video_id[video_id] = (metadata, metadata_path)

    enriched: list[dict] = []
    for video in ranked_videos:
        video_id = clean_text(video.get("video_id"))
        metadata_entry = metadata_by_video_id.get(video_id)
        if not metadata_entry:
            enriched.append(video)
            continue
        metadata, metadata_path = metadata_entry
        author = metadata.get("author") or {}
        raw = metadata.get("raw") or {}
        raw_item_infos = raw.get("itemInfos") or {}
        merged = dict(video)
        merged["metadata_source"] = clean_text(metadata.get("source_url"))
        merged["caption_text"] = clean_text(metadata.get("title") or raw_item_infos.get("text") or metadata.get("title"))
        merged["desc"] = clean_text(metadata.get("title")) or clean_text(video.get("desc")) or extract_video_desc(metadata)
        merged["hook_text"] = infer_hook_text(metadata)
        merged["core_topic"] = build_core_topic(metadata) or clean_text(video.get("core_topic"))
        merged["hashtags"] = extract_hashtags(metadata)
        merged["author_signature"] = clean_text(author.get("signature"))
        merged["author_verified"] = bool(author.get("verified"))
        merged["music_title"] = clean_text(metadata.get("music_title"))
        merged["author_follower_count"] = safe_int((raw.get("authorStats") or {}).get("followerCount") or (raw.get("authorStatsV2") or {}).get("followerCount") or merged.get("author_follower_count"))
        merged["is_ec_video"] = safe_int(raw_item_infos.get("isECVideo") or raw.get("isECVideo") or merged.get("is_ec_video"))
        merged["downloaded_metadata_path"] = metadata_path
        enriched.append(merged)
    return apply_reuse_value_scoring(enriched)


def build_qualified_videos(ranked_videos: list[dict], min_likes: int, qualified_count: int) -> list[dict]:
    winners = [
        dict(item)
        for item in ranked_videos
        if safe_int(item.get("digg_count")) >= min_likes or safe_int(item.get("reuse_value_score")) >= 60
    ]
    if not winners:
        winners = [dict(item) for item in ranked_videos[: max(1, min(qualified_count, len(ranked_videos)))]]
    winners.sort(
        key=lambda item: (
            safe_int(item.get("reuse_value_score")),
            safe_int(item.get("commerce_confidence")),
            safe_int(item.get("popularity_score")),
            safe_int(item.get("digg_count")),
        ),
        reverse=True,
    )
    shortlisted = winners[:qualified_count]
    for index, item in enumerate(shortlisted, start=1):
        item["shortlist_priority"] = f"P{index}"
        item["shortlist_bucket"] = "scene03_deep_teardown"
        item["shortlist_decision"] = "deep_teardown_now" if index <= 3 else "watchlist"
    return shortlisted


def top_level_comments(comment_payload: dict) -> list[dict]:
    comments = comment_payload.get("comments") or []
    top_level: list[dict] = []
    for item in comments:
        if not isinstance(item, dict):
            continue
        if item.get("is_reply"):
            continue
        if clean_text(item.get("parent_comment_id")):
            continue
        top_level.append(item)
    top_level.sort(key=lambda item: safe_int(item.get("digg_count")), reverse=True)
    return top_level


def build_comments_sampled(profile_url: str, comment_payload: dict, sample_size: int) -> list[dict]:
    source_url = clean_text(comment_payload.get("source_url")) or profile_url
    video_id = clean_text(comment_payload.get("video_id"))
    samples: list[dict] = []
    for item in top_level_comments(comment_payload)[:sample_size]:
        author = item.get("author") or {}
        samples.append(
            {
                "cid": clean_text(item.get("comment_id") or item.get("cid")),
                "text": clean_text(item.get("text")),
                "digg_count": safe_int(item.get("digg_count")),
                "reply_comment_total": safe_int(item.get("reply_comment_total")),
                "nickname": clean_text(author.get("nickname")),
                "unique_id": clean_text(author.get("unique_id")),
            }
        )
    return [
        {
            "video_url": source_url,
            "video_id": video_id,
            "unique_id": profile_url.rstrip("/").split("@")[-1] if "@" in profile_url else "",
            "comment_count": safe_int(comment_payload.get("item_count") or len(top_level_comments(comment_payload))),
            "sample_count": len(samples),
            "samples": samples,
        }
    ]


def write_json(path: Path, payload: object) -> None:
    write_json_file(path, payload)


def write_csv(path: Path, rows: list[dict]) -> None:
    fieldnames = [
        "video_id",
        "video_url",
        "comment_id",
        "text",
        "digg_count",
        "reply_comment_total",
        "nickname",
        "unique_id",
    ]
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def build_comments_flat_rows(comment_payload: dict) -> list[dict]:
    rows: list[dict] = []
    for item in top_level_comments(comment_payload):
        author = item.get("author") or {}
        rows.append(
            {
                "video_id": clean_text(comment_payload.get("video_id")),
                "video_url": clean_text(comment_payload.get("source_url")),
                "comment_id": clean_text(item.get("comment_id") or item.get("cid")),
                "text": clean_text(item.get("text")),
                "digg_count": safe_int(item.get("digg_count")),
                "reply_comment_total": safe_int(item.get("reply_comment_total")),
                "nickname": clean_text(author.get("nickname")),
                "unique_id": clean_text(author.get("unique_id")),
            }
        )
    return rows


def build_bridge_pack(
    *,
    profile_posts_json: Path,
    comments_json: Path | None,
    downloads_json: Path | None,
    bridge_root: Path,
    min_likes: int,
    qualified_count: int,
    comment_sample_size: int,
) -> dict:
    profile_payload = load_json(profile_posts_json)
    if not isinstance(profile_payload, dict):
        raise SystemExit("profile_posts.json must be a JSON object.")
    profile_payload["_source_path"] = str(profile_posts_json)
    profile_url = clean_text(profile_payload.get("source_url"))
    ranked_videos = normalize_ranked_videos(profile_payload)
    if not ranked_videos:
        raise SystemExit("No videos were found in the TikMatrix profile_posts.json export.")
    downloads_payload: list[dict] = []
    if downloads_json:
        loaded_downloads = load_json(downloads_json)
        if not isinstance(loaded_downloads, list):
            raise SystemExit("downloads.json must be a JSON array.")
        for item in loaded_downloads:
            if isinstance(item, dict):
                metadata_path = clean_text(item.get("metadata_path"))
                if metadata_path:
                    item["_source_path"] = metadata_path
        downloads_payload = loaded_downloads
        ranked_videos = enrich_ranked_videos_from_downloads(ranked_videos, downloads_payload)
    qualified_videos = build_qualified_videos(ranked_videos, min_likes=min_likes, qualified_count=qualified_count)

    profile_summary = {
        "profile_url": profile_url,
        "output_dir": str(profile_posts_json.parent),
        "exit_code": 0,
        "reachable": True,
        "session_quality": "tikmatrix_profile_posts_export",
        "link_count": len(ranked_videos),
        "detail_collected_count": len(ranked_videos),
        "ranked_video_count": len(ranked_videos),
        "qualified_video_count": len(qualified_videos),
        "api_item_count": None,
        "browser_api_item_count": len(ranked_videos),
        "comment_sampled_video_count": 1 if comments_json else 0,
        "video_download_success_count": 0,
        "cover_download_success_count": None,
        "checked_at": datetime.now().astimezone().isoformat(timespec="seconds"),
    }
    summary = {
        "checked_at": profile_summary["checked_at"],
        "platform": "tiktok",
        "reachable": True,
        "session_quality": profile_summary["session_quality"],
        "base_status_code": 200,
        "profile_status_code": 200,
        "profile_final_url": profile_url,
        "detail_collected_count": len(ranked_videos),
        "ranked_video_count": len(ranked_videos),
        "qualified_video_count": len(qualified_videos),
        "notes": [
            "Bridged from TikMatrix profile_posts.json into tiktok-growth-operator capture-pack format.",
            "This bridge preserves source file references instead of mutating the TikMatrix project.",
        ],
    }
    aggregate_summary = {
        "started_at": datetime.now().isoformat(timespec="seconds"),
        "ended_at": datetime.now().isoformat(timespec="seconds"),
        "profile_count": 1,
        "aggregated_ranked_count": len(ranked_videos),
        "aggregated_qualified_count": len(qualified_videos),
        "min_likes": min_likes,
        "output_root": str(bridge_root),
        "profile_summary_json": str(bridge_root / "profile_summary.json"),
        "ranked_json": str(bridge_root / "aggregate_ranked_videos.json"),
        "qualified_json": str(bridge_root / "aggregate_qualified_videos.json"),
    }

    write_json(bridge_root / "summary.json", summary)
    write_json(bridge_root / "profile_summary.json", profile_summary)
    write_json(bridge_root / "aggregate_summary.json", aggregate_summary)
    write_json(bridge_root / "ranked_videos.json", ranked_videos)
    write_json(bridge_root / "aggregate_ranked_videos.json", ranked_videos)
    write_json(bridge_root / "aggregate_qualified_videos.json", qualified_videos)
    write_json(bridge_root / "video_details.json", {"videos": ranked_videos, "source_profile_posts_json": str(profile_posts_json)})
    write_utf8_text(
        bridge_root / "aggregate_ranked_links.txt",
        "\n".join(item["video_url"] for item in ranked_videos if clean_text(item.get("video_url"))) + "\n",
    )
    write_utf8_text(
        bridge_root / "qualified_video_links.txt",
        "\n".join(item["video_url"] for item in qualified_videos if clean_text(item.get("video_url"))) + "\n",
    )

    report_lines = [
        "# TikMatrix Bridge Capture Pack",
        "",
        f"- source profile export: `{profile_posts_json}`",
        f"- profile url: `{profile_url}`",
        f"- ranked video count: `{len(ranked_videos)}`",
        f"- qualified video count: `{len(qualified_videos)}`",
    ]

    source_manifest = {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "profile_posts_json": str(profile_posts_json),
        "comments_json": str(comments_json) if comments_json else "",
        "downloads_json": str(downloads_json) if downloads_json else "",
        "bridge_root": str(bridge_root),
        "top_video_ids": [item["video_id"] for item in ranked_videos[:5]],
    }

    if comments_json:
        comment_payload = load_json(comments_json)
        if not isinstance(comment_payload, dict):
            raise SystemExit("comments.json must be a JSON object.")
        comments_sampled = build_comments_sampled(profile_url, comment_payload, sample_size=comment_sample_size)
        comments_flat_rows = build_comments_flat_rows(comment_payload)
        write_json(bridge_root / "comments_sampled.json", comments_sampled)
        write_json(
            bridge_root / "comments_summary.json",
            {
                "video_count": 1,
                "sampled_video_count": 1,
                "total_comment_count": safe_int(comment_payload.get("item_count")),
                "source_comments_json": str(comments_json),
            },
        )
        write_csv(bridge_root / "comments_flat.csv", comments_flat_rows)
        report_lines.extend(
            [
                f"- comment source: `{comments_json}`",
                f"- sampled top-level comments: `{len(comments_sampled[0]['samples'])}`",
            ]
        )

    if downloads_json:
        success_count = len([item for item in downloads_payload if isinstance(item, dict) and not item.get("skipped")])
        profile_summary["video_download_success_count"] = success_count
        write_json(bridge_root / "downloads_manifest.json", downloads_payload)
        write_json(
            bridge_root / "downloads_summary.json",
            {
                "download_count": success_count,
                "source_downloads_json": str(downloads_json),
            },
        )
        write_json(bridge_root / "profile_summary.json", profile_summary)
        report_lines.append(f"- download manifest source: `{downloads_json}`")

    write_json(bridge_root / "source_manifest.json", source_manifest)
    write_utf8_text(bridge_root / "aggregate_report.md", "\n".join(report_lines) + "\n")

    return {
        "bridge_root": str(bridge_root),
        "profile_url": profile_url,
        "ranked_count": len(ranked_videos),
        "qualified_count": len(qualified_videos),
        "has_comments": bool(comments_json),
        "top_video_ids": [item["video_id"] for item in ranked_videos[:3]],
    }


def main() -> None:
    args = parse_args()
    skill_root = Path(__file__).resolve().parents[1]
    bridge_base_root = ensure_root(args.output_root, skill_root, args.name.strip())
    bridge_root = bridge_base_root / "capture-pack"
    bridge_root.mkdir(parents=True, exist_ok=True)

    profile_posts_json = Path(args.profile_posts_json).expanduser().resolve()
    comments_json = Path(args.comments_json).expanduser().resolve() if args.comments_json.strip() else None
    downloads_json = Path(args.downloads_json).expanduser().resolve() if args.downloads_json.strip() else None

    bridge_result = build_bridge_pack(
        profile_posts_json=profile_posts_json,
        comments_json=comments_json,
        downloads_json=downloads_json,
        bridge_root=bridge_root,
        min_likes=args.min_likes,
        qualified_count=args.qualified_count,
        comment_sample_size=args.comment_sample_size,
    )

    operator_result = create_capture_pack_run(
        scene=args.scene,
        capture_root_raw=str(bridge_root),
        name=args.name,
        project=args.project,
        target_markets=args.target_markets,
        target_languages=args.target_languages,
        output_root=str(bridge_base_root / "operator-run"),
        platform=args.platform,
        market=args.market,
        formats=args.formats,
        operator_packs_raw=args.operator_packs,
    )

    print(
        json.dumps(
            {
                "bridge": bridge_result,
                "operator_run": operator_result,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
