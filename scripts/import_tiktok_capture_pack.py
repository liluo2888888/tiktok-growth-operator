from __future__ import annotations

import argparse
import json
import re
import unicodedata
from collections import Counter
from datetime import datetime
from pathlib import Path

from generate_scene_report import build_report_payload, load_catalog, resolve_scene
from text_normalization import normalize_nested, normalize_text, read_json_file, read_utf8_text, write_json_file


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Import a real TikTok capture-pack directory into a filled scene-report JSON."
    )
    parser.add_argument("--scene", required=True, help="Scene id, slug, or `auto`.")
    parser.add_argument("--capture-root", required=True, help="Capture-pack root directory.")
    parser.add_argument("--project", default="", help="Optional explicit project name.")
    parser.add_argument("--target-markets", default="", help="Optional comma-separated target markets for scene 13 localization blueprints.")
    parser.add_argument("--target-languages", default="", help="Optional comma-separated target languages for scene 15 image-translation blueprints.")
    parser.add_argument("--output", required=True, help="Output scene-report JSON path.")
    return parser.parse_args()


def load_json(path: Path) -> dict | list:
    return read_json_file(path)


def clean_text(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        parts = [clean_text(item) for item in value]
        return "\n".join(item for item in parts if item)
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


def is_local_path_text(value: str) -> bool:
    text = clean_text(value)
    return bool(text) and (
        text.startswith("\\\\")
        or (len(text) > 2 and text[1] == ":" and text[2] in {"\\", "/"})
    )


def display_path(path: Path, anchor: Path | None = None) -> str:
    try:
        resolved = path.resolve()
    except OSError:
        resolved = path
    if anchor is not None:
        try:
            return resolved.relative_to(anchor.resolve()).as_posix()
        except ValueError:
            pass
    parts = list(resolved.parts)
    if len(parts) >= 3:
        return Path(*parts[-3:]).as_posix()
    return resolved.as_posix()


def format_source_reference(value: object, *, anchor: Path | None = None) -> str:
    text = clean_text(value)
    if not text:
        return ""
    if is_local_path_text(text):
        return display_path(Path(text), anchor=anchor)
    return text


def contains_dirty_zh_markers(value: object) -> bool:
    text = clean_text(value)
    if not text:
        return False
    markers = ("鎴", "锛", "銆", "馃", "", "杈", "缁", "浜", "鍏", "鏈")
    return any(marker in text for marker in markers)


def maybe_load(path: Path) -> dict | list | None:
    return load_json(path) if path.exists() else None


def maybe_read_text(path: Path) -> str | None:
    return read_utf8_text(path) if path.exists() else None


def existing_paths(paths: list[Path]) -> list[Path]:
    return [path for path in paths if path.exists()]


def candidate_capture_dirs(capture_root: Path) -> list[Path]:
    candidates = [capture_root]
    candidates.extend(sorted(path for path in capture_root.iterdir() if path.is_dir()))
    deduped: list[Path] = []
    seen: set[Path] = set()
    for path in candidates:
        resolved = path.resolve()
        if resolved not in seen:
            seen.add(resolved)
            deduped.append(resolved)
    return deduped


def first_existing_path(capture_root: Path, names: list[str]) -> Path | None:
    for directory in candidate_capture_dirs(capture_root):
        for name in names:
            path = directory / name
            if path.exists():
                return path
    return None


def load_pack_files(capture_root: Path) -> tuple[dict, dict, list[dict], list[dict]]:
    aggregate_summary = maybe_load(capture_root / "aggregate_summary.json")
    profile_summary = maybe_load(capture_root / "profile_summary.json")
    ranked_videos = maybe_load(capture_root / "aggregate_ranked_videos.json")
    qualified_videos = maybe_load(capture_root / "aggregate_qualified_videos.json")
    video_details = maybe_load(capture_root / "video_details.json")

    if aggregate_summary is None:
        aggregate_summary = maybe_load(capture_root / "summary.json") or {}
    if profile_summary is None:
        profile_summary = maybe_load(capture_root / "summary.json") or {}
    if ranked_videos is None:
        ranked_videos = maybe_load(capture_root / "ranked_videos.json") or []
    if qualified_videos is None:
        qualified_videos = []
        qualified_links = maybe_read_text(capture_root / "qualified_video_links.txt")
        if isinstance(ranked_videos, list):
            ranked_map = {clean_text(item.get("video_url")): item for item in ranked_videos if isinstance(item, dict)}
            if isinstance(qualified_links, str):
                for line in qualified_links.splitlines():
                    line = line.strip()
                    if line and line in ranked_map:
                        qualified_videos.append(ranked_map[line])
    elif isinstance(qualified_videos, dict):
        qualified_videos = [qualified_videos]

    detail_rows: list[dict] = []
    if isinstance(video_details, dict):
        raw_videos = video_details.get("videos")
        if isinstance(raw_videos, list):
            detail_rows = [item for item in raw_videos if isinstance(item, dict)]
    elif isinstance(video_details, list):
        detail_rows = [item for item in video_details if isinstance(item, dict)]

    if detail_rows:
        detail_map = {
            clean_text(item.get("video_url") or item.get("video_id")): item
            for item in detail_rows
            if clean_text(item.get("video_url") or item.get("video_id"))
        }

        def merge_detail_rows(rows: object) -> list[dict]:
            merged: list[dict] = []
            if not isinstance(rows, list):
                return merged
            for item in rows:
                if not isinstance(item, dict):
                    continue
                key = clean_text(item.get("video_url") or item.get("video_id"))
                detail = detail_map.get(key, {})
                merged.append({**detail, **item} if detail else item)
            return merged

        ranked_videos = merge_detail_rows(ranked_videos)
        qualified_videos = merge_detail_rows(qualified_videos)

    from content_graph import ensure_pack_content_graph
    from reuse_value_scoring import align_qualified_to_ranked, apply_reuse_value_scoring

    ranked_list = ranked_videos if isinstance(ranked_videos, list) else []
    qualified_list = qualified_videos if isinstance(qualified_videos, list) else []
    if ranked_list:
        ranked_list[:] = apply_reuse_value_scoring(ranked_list)
    if qualified_list and ranked_list:
        qualified_list[:] = align_qualified_to_ranked(ranked_list, qualified_list)
    ensure_pack_content_graph(capture_root, ranked_list, qualified_list)

    return (
        aggregate_summary if isinstance(aggregate_summary, dict) else {},
        profile_summary if isinstance(profile_summary, dict) else {},
        ranked_list,
        qualified_list,
    )


def top_videos(videos: list[dict], limit: int = 5) -> list[dict]:
    return videos[:limit]


def video_line(video: dict) -> str:
    return (
        f"{clean_text(video.get('video_url'))} | 点赞={video.get('digg_count', 0)} "
        f"评论={video.get('comment_count', 0)} 分享={video.get('share_count', 0)} "
        f"播放={video.get('play_count', 0)}"
    )


def compact_text(value: object) -> str:
    return " ".join(clean_text(value).split())


def strip_display_noise(text: str) -> str:
    cleaned_chars: list[str] = []
    for ch in text:
        code = ord(ch)
        if unicodedata.category(ch).startswith("C"):
            continue
        if 0x1F300 <= code <= 0x1FAFF:
            continue
        if 0x2600 <= code <= 0x27BF:
            continue
        if 0xFFFD == code:
            continue
        cleaned_chars.append(ch)
    return "".join(cleaned_chars)


DISPLAY_NOISE_REPLACEMENTS = {
    "鉂わ笍": " heart ",
    "棣冩問": "",
    "棣冩啨": "",
    "棣冩": "",
    "棣冦亯": "",
    "棣冩暉": "",
    "棣冩晬": "",
    "棣冩啠": "",
    "棣冩寱": "",
    "棣冩": "",
    "棣冩": "",
    "馃憖": "",
    "馃槀": "",
    "馃ぃ": "",
    "馃槶": "",
    "鈾": "",
}

DISPLAY_PHRASE_REPLACEMENTS = {
    "sing your out": "sing your heart out",
    "moments heart": "moments",
}

CAPTION_TAIL_MARKERS = [
    " tune into ",
    " on our page coming soon",
    " coming soon",
    " link in bio",
    " watch the full",
    " full episode",
    " full video",
    " full interview",
    " more on our page",
]


def finalize_caption_text(text: str) -> str:
    compact = " ".join(text.split())
    for source, target in DISPLAY_PHRASE_REPLACEMENTS.items():
        compact = compact.replace(source, target)
    compact = compact.replace(" heart .", ".")
    compact = compact.replace(" heart ,", ",")
    compact = compact.replace(" heart !", "!")
    compact = compact.replace(" heart ?", "?")
    if compact.lower().endswith(" heart"):
        compact = compact[:-6].rstrip(" ,;:-")
    compact = compact.replace("  ", " ")
    return compact.strip(" -|,:;")


def trim_caption_tail(text: str) -> str:
    compact = finalize_caption_text(text)
    lowered = compact.lower()
    cut_points = [lowered.find(marker) for marker in CAPTION_TAIL_MARKERS]
    valid_points = [point for point in cut_points if point >= 24]
    if valid_points:
        compact = compact[: min(valid_points)].rstrip(" ,;:-")
    return finalize_caption_text(compact)


def normalize_caption_candidate(value: object, *, hashtag_limit: int = 5) -> str:
    compact = strip_display_noise(compact_text(value))
    if not compact:
        return ""
    for source, target in DISPLAY_NOISE_REPLACEMENTS.items():
        compact = compact.replace(source, target)
    compact = re.sub(r"馃\S*", "", compact)
    for source, target in DISPLAY_PHRASE_REPLACEMENTS.items():
        compact = compact.replace(source, target)

    if "#" in compact:
        compact = compact.replace("#", " #")
        compact = " ".join(compact.split())

    tokens = compact.split()
    hashtag_tokens = [token for token in tokens if token.startswith("#")]
    non_hashtag_tokens = [token for token in tokens if not token.startswith("#")]

    if compact.startswith("#") and hashtag_tokens:
        if non_hashtag_tokens:
            lead_text = " ".join(non_hashtag_tokens).strip()
            if len(lead_text) >= 24:
                compact = lead_text
            else:
                sampled = " ".join(hashtag_tokens[:hashtag_limit])
                compact = sampled + (" ..." if len(hashtag_tokens) > hashtag_limit else "")
        else:
            sampled = " ".join(hashtag_tokens[:hashtag_limit])
            return sampled + (" ..." if len(hashtag_tokens) > hashtag_limit else "")

    if "#" in compact:
        lead = compact.split("#", 1)[0].rstrip(" -|,:;")
        if len(lead) >= 24:
            compact = lead

    compact = compact.replace("—", "-").replace("–", "-")
    compact = compact.replace("  ", " ")
    compact = compact.strip(" -|,:;")
    return finalize_caption_text(compact)


def report_caption_text(value: object, *, limit: int = 120) -> str:
    cleaned = normalize_caption_candidate(value)
    if not cleaned:
        return ""
    trimmed = trim_caption_tail(cleaned)
    return sentence_clip(trimmed, limit=limit)


def display_cue_text(video: dict, *, limit: int = 96, fallback: str = "") -> str:
    cue = hook_text(video) or core_topic_text(video) or report_caption_text(fallback, limit=limit)
    if not cue:
        return ""
    return sentence_clip(cue, limit=limit)


def hook_text(video: dict) -> str:
    for candidate in [
        video.get("hook_text"),
        video.get("caption_text"),
        video.get("desc"),
        video.get("core_topic"),
    ]:
        text = report_caption_text(candidate, limit=128)
        if text:
            return text
    return ""


def sentence_clip(text: str, limit: int = 120) -> str:
    cleaned = normalize_caption_candidate(text)
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


def core_topic_text(video: dict) -> str:
    for candidate in [
        video.get("core_topic"),
        video.get("caption_text"),
        video.get("desc"),
    ]:
        text = report_caption_text(candidate, limit=92)
        if text:
            return sentence_clip(text, limit=92)
    return ""


def hashtags_text(video: dict) -> str:
    tags = video.get("hashtags") or []
    if isinstance(tags, list):
        normalized = [f"#{clean_text(tag)}" for tag in tags if clean_text(tag)]
        if normalized:
            return ", ".join(normalized[:4])
    return ""


def author_signal_text(video: dict) -> str:
    verified = bool(video.get("author_verified"))
    raw_signature = clean_text(video.get("author_signature")).replace("\r", " ").replace("\n", " / ")
    signature = strip_display_noise(raw_signature)
    signature = finalize_caption_text(signature)
    signature = signature.replace(" /  / ", " / ").replace(" / / ", " / ")
    if signature in {".", "-", "_"}:
        signature = ""
    unique_id = clean_text(video.get("unique_id"))
    account_label = ""
    if unique_id:
        account_label = f"{unique_id}（{'已认证' if verified else '未认证'}）"
    elif verified:
        account_label = "已认证账号"
    elif signature:
        account_label = "未认证账号"

    if signature and signature != unique_id:
        return f"{account_label} - {signature}" if account_label else signature
    return account_label


def proof_style_text(video: dict) -> str:
    explicit = strip_display_noise(clean_text(video.get("reuse_value_label")))
    if explicit:
        return explicit
    if video.get("author_verified"):
        return "认证账号背书"
    if clean_text(video.get("author_signature")):
        return "创作者 / 品牌语境背书"
    return "以包装驱动为主，未恢复出强权威线索"


def reuse_value_label(video: dict) -> str:
    explicit = strip_display_noise(clean_text(video.get("reuse_value_label") or video.get("best_reuse_category")))
    if explicit:
        return explicit
    lane = teardown_lane_label(video)
    commerce = safe_int(video.get("commerce_confidence"))
    caption = hook_text(video)
    topic = core_topic_text(video)
    if commerce >= 70:
        return "适合带货转化包装复用"
    if "证明" in lane or "权威" in lane:
        return "适合证明物 / 权威替代改写"
    if "情绪" in lane:
        return "适合情绪钩子与时刻感包装复用"
    if "选题" in lane or "角度" in lane:
        return "适合选题角度与叙事切口借鉴"
    if caption and topic:
        return "适合开头钩子与主题包装复用"
    if caption:
        return "适合开头钩子与文案包装复用"
    return "适合首屏包装与结构参考"


def why_selected_text(video: dict) -> str:
    explicit = strip_display_noise(clean_text(video.get("why_selected") or video.get("why_worth_studying") or video.get("scene03_reason")))
    if explicit:
        return explicit
    parts = []
    if hook_text(video):
        parts.append("已恢复可用的 caption / hook 文本")
    if video.get("author_verified"):
        parts.append("带明显权威或认证信号")
    if hashtags_text(video):
        parts.append("带可复用的话题标签")
    if not parts:
        parts.append("综合表现强，且具备可复用包装潜力")
    return "; ".join(parts[:3])


def ranked_metric_summary(video: dict) -> str:
    return (
        f"点赞={video.get('digg_count', 0)} / "
        f"评论={video.get('comment_count', 0)} / "
        f"分享={video.get('share_count', 0)}"
    )


def music_style_text(video: dict) -> str:
    music = sentence_clip(clean_text(video.get("music_title")), limit=72)
    if music:
        return music
    if clean_text(video.get("play_addr")):
        return "原声或已恢复的原生平台音频"
    return "当前采集包未恢复出清晰音频线索"


def scene04_video_type(video: dict) -> str:
    lane = teardown_lane_label(video).lower()
    hook = hook_text(video).lower()
    desc = clean_text(video.get("desc")).lower()
    if "tutorial" in hook or "how to" in hook or "tutorial" in desc:
        return "演示型教程"
    if "proof" in lane or "authority" in lane:
        return "权威 / 证明驱动讲解"
    if "emotional" in lane or "moment" in desc or "story" in desc:
        return "字幕驱动的情绪拼贴"
    if clean_text(video.get("caption_text")) and not author_signal_text(video):
        return "字幕驱动的快节奏拼贴"
    return "识别优先的短讲解"


def scene04_no_voiceover_judgment(video: dict) -> str:
    if clean_text(video.get("caption_text")) and not clean_text(video.get("music_title")):
        return "即便几乎没有口播也能成立，因为字幕和画面线索已经把前提带出来了。"
    if clean_text(video.get("caption_text")):
        return "即使口播很轻，画面线索加字幕包装也足以支撑这条逻辑。"
    return "当前采集包里的口播置信度偏弱，应更多依赖切镜、证明物和字幕重建。"


def creator_positioning_text(video: dict) -> str:
    unique_id = clean_text(video.get("unique_id"))
    lane = teardown_lane_label(video)
    if unique_id:
        return f"{unique_id} 的内容定位偏向 {lane}。"
    return f"该账号样本整体偏向 {lane}。"


def creator_breakout_rate_text(videos: list[dict], average_likes: int) -> str:
    if not videos:
        return "样本内 0/0"
    breakout = len([video for video in videos if safe_int(video.get("digg_count")) >= average_likes and average_likes > 0])
    return f"样本内 {breakout}/{len(videos)}"


def content_mode_text(video: dict) -> str:
    lane = teardown_lane_label(video)
    video_type = scene04_video_type(video)
    if lane:
        return f"{lane} | {video_type}"
    return video_type


def growth_roi_relevance_text(video: dict) -> str:
    commerce = safe_int(video.get("commerce_confidence"))
    lane = teardown_lane_label(video)
    if commerce >= 60:
        return "更适合用于需要强化转化或 TikTok Shop 带货意图的账号。"
    if "权威" in lane:
        return "更适合用于依赖信任转移、凭证证明或强背书的增长目标。"
    if "情绪" in lane:
        return "更适合先拉触达、收藏或好感，再承接更强转化的场景。"
    if "选题" in lane or "角度" in lane:
        return "更适合用于需要新角度、但不想重建整套内容引擎的账号。"
    return "更适合用于需要更清晰包装和更早抓住注意力的账号。"


def strategy_change_text(video: dict) -> str:
    lane = teardown_lane_label(video)
    if "权威" in lane:
        return "本周更偏向信任 / 权威型包装。"
    if "情绪" in lane:
        return "本周更偏向情绪或时刻感驱动包装。"
    if "选题" in lane or "角度" in lane:
        return "本周更像在测试新的选题角度或包装法。"
    return "延续识别优先的包装，只做轻量形式变化。"


def teardown_lane_label(video: dict) -> str:
    explicit = strip_display_noise(clean_text(video.get("reuse_value_label")))
    if explicit:
        return explicit
    desc = clean_text(video.get("desc")).lower()
    if video.get("author_verified") or "@" in desc:
        return "证明 / 权威拆解"
    if any(token in desc for token in ["psa", "reminder", "little moments", "moment"]):
        return "钩子 / 情绪框架拆解"
    if any(token in desc for token in ["creativity", "stemtok", "breakthrough"]):
        return "选题 / 角度拆解"
    return "钩子 / 包装拆解"


def teardown_action_text(video: dict) -> str:
    lane = teardown_lane_label(video)
    if lane == "证明 / 权威拆解":
        return "先拆清信任来源，再在写脚本前换成一个自有证明物。"
    if lane == "钩子 / 情绪框架拆解":
        return "先保留首句关键信号，再补 2-3 个自有版本的开头改写，再动整体结构。"
    if lane == "选题 / 角度拆解":
        return "去掉账号势能并补强证明后，再验证这个选题角度是否还能成立。"
    return "保留识别优先的包装逻辑，再用自有素材重写证明层。"


def patrol_entry_url(entry: dict) -> str:
    return clean_text(entry.get("video_url") or entry.get("url"))


def patrol_entry_label(entry: dict) -> str:
    for candidate in [
        entry.get("source_label"),
        entry.get("field"),
        entry.get("video_id"),
        patrol_entry_url(entry),
    ]:
        text = clean_text(candidate)
        if text:
            return text
    return "追踪项"


def patrol_entry_metric_summary(entry: dict) -> str:
    metrics = []
    for label, key in [
        ("点赞", "digg_count"),
        ("评论", "comment_count"),
        ("分享", "share_count"),
        ("播放", "play_count"),
        ("分数", "score"),
    ]:
        value = entry.get(key)
        if value not in (None, "", 0, "0"):
            metrics.append(f"{label}={value}")
    return " | ".join(metrics)


def scene02_candidate_reason(entry: dict) -> str:
    explicit = clean_text(entry.get("scene03_reason"))
    if explicit:
        return explicit
    if metric_value(entry, "digg_count") >= 1000:
        return "点赞高，值得继续深拆"
    if metric_value(entry, "share_count") >= 50:
        return "分享高，可能带有可迁移的钩子或证明装置"
    if metric_value(entry, "comment_count") >= 20:
        return "评论活跃，值得继续挖用户语言"
    return "当前排序靠前的兜底候选"


def scene02_candidate_owner(entry: dict) -> str:
    lane = teardown_lane_label(entry)
    if lane == "证明 / 权威拆解":
        return "策略 / 分析"
    if lane == "钩子 / 情绪框架拆解":
        return "内容策略"
    if lane == "选题 / 角度拆解":
        return "研究 / 策略"
    return "运营 / 策略"


def build_scene02_watchlist_rows(
    queries: list[object],
    topics: list[object],
    source_manifest: list[dict],
) -> list[list[str]]:
    rows: list[list[str]] = []
    for query in queries:
        text = clean_text(query)
        if text:
            rows.append(["search query", text, "search", "P1", "固定关键词入口", "每日复用同一查询词", "是"])
    for topic in topics:
        text = clean_text(topic)
        if text:
            rows.append(["topic tag", f"#{text.lstrip('#')}", "topic", "P1", "固定话题入口", "每日复用同一话题标签", "是"])
    for item in source_manifest[:4]:
        if not isinstance(item, dict):
            continue
        rows.append(
            [
                clean_text(item.get("source_kind")) or "source",
                clean_text(item.get("source_label")) or "未命名来源",
                clean_text(item.get("source_kind")) or "mixed",
                "P2",
                f"本轮采集 {safe_int(item.get('item_count'))} 条",
                f"metadata={safe_int(item.get('metadata_count'))}",
                "视排名决定",
            ]
        )
    if not rows:
        rows.append(["watch item", "待补关键词或话题", "search", "P1", "先锁定品类入口", "下轮开始追加到同一主表", "否"])
    return rows[:8]


def build_scene02_alert_rows(
    alerts: list[dict],
    repeated_hooks: list[dict],
    next_scene03: list[dict],
    tracked_videos: list[dict],
) -> list[list[str]]:
    rows: list[list[str]] = []
    for alert in alerts[:6]:
        follow_up = clean_text(alert.get("follow_up") or alert.get("next_action"))
        rows.append(
            [
                clean_text(alert.get("priority") or "P1"),
                clean_text(alert.get("signal") or alert.get("label") or alert.get("alert_type")),
                clean_text(alert.get("meaning") or alert.get("detail") or alert.get("reason")),
                follow_up or "Review for shortlist or suppress as noise",
            ]
        )
    if repeated_hooks and len(rows) < 6:
        for hook in repeated_hooks[: max(0, 6 - len(rows))]:
            rows.append(
                [
                    "P2",
                    "Repeated hook across accounts",
                    clean_text(hook.get("hook_text") or hook.get("label") or "Repeated hook detected"),
                    "Compare packaging and decide whether this belongs in the next Scene 03 teardown batch",
                ]
            )
    if rows:
        return rows

    top_candidate = next_scene03[0] if next_scene03 else (tracked_videos[0] if tracked_videos else {})
    creator_counts: dict[str, int] = {}
    for entry in tracked_videos:
        uid = clean_text(entry.get("unique_id"))
        if uid:
            creator_counts[uid] = creator_counts.get(uid, 0) + 1
    repeated_creator = next((uid for uid, count in creator_counts.items() if count > 1), "")
    metadata_gap_count = sum(1 for entry in tracked_videos[:5] if not clean_text(entry.get("downloaded_metadata_path")))

    synthesized = [
        [
            "P1",
            "No live breakout, but the top teardown queue is still actionable",
            f"{clean_text(top_candidate.get('video_url')) or 'Top-ranked candidate'} remains the clearest scheduled escalation lane.",
            "Push the top queued candidate into Scene 03 now instead of waiting for a noisy spike.",
        ],
        [
            "P2",
            "Stable leaderboard with no delta spike",
            "The category looks steady rather than breaking open, so the team should learn from the standing winners instead of broadening collection blindly.",
            "Keep the patrol narrow and compare the same leaders on the next run.",
        ],
    ]
    if repeated_creator:
        synthesized.append(
            [
                "P2",
                "Creator concentration in the top board",
                f"{repeated_creator} appears multiple times in the tracked set, so some signal may come from account repetition rather than format novelty.",
                "Separate creator lift from portable packaging before adding more similar posts to the queue.",
            ]
        )
    if metadata_gap_count:
        synthesized.append(
            [
                "P3",
                "Download metadata path missing on tracked leaders",
                f"{metadata_gap_count} top tracked rows still lack downloaded detail enrichment, which weakens later teardown quality.",
                "Download or attach richer metadata for the top 3 candidates before the next Scene 03 pass.",
            ]
        )
    return synthesized[:6]


def build_scene02_escalation_rows(next_scene03: list[dict]) -> list[list[str]]:
    rows: list[list[str]] = []
    ordered_candidates = sorted(
        next_scene03,
        key=lambda entry: (
            1 if safe_int(entry.get("commerce_confidence")) >= 60 or clean_text(entry.get("tkshop_signal")).lower() not in {"", "未检测到", "not_detected"} else 0,
            1 if clean_text(entry.get("shortlist_decision")) in {"立即深拆", "deep_teardown_now"} else 0,
            safe_int(entry.get("score")),
            safe_int(entry.get("digg_count")),
            safe_int(entry.get("comment_count")),
        ),
        reverse=True,
    )
    for index, entry in enumerate(ordered_candidates[:3], start=1):
        rows.append(
            [
                f"P{index}",
                clean_text(entry.get("video_url") or entry.get("video_id")),
                f"{scene02_candidate_reason(entry)}; lane: {teardown_lane_label(entry)}; metrics: {ranked_metric_summary(entry)}",
                scene02_candidate_owner(entry),
            ]
        )
    if not rows:
        rows.append(
            [
                "P1",
                "Pick the top-ranked patrol row",
                "No explicit Scene 03 queue was generated, so choose the strongest ranked candidate manually.",
                "Operator / strategist",
            ]
        )
    return rows


def make_context(
    capture_root: Path,
    aggregate_summary: dict,
    profile_summary: dict,
    ranked_videos: list[dict],
    qualified_videos: list[dict],
) -> str:
    ranked_count = aggregate_summary.get("aggregated_ranked_count", aggregate_summary.get("ranked_video_count", 0))
    qualified_count = aggregate_summary.get("aggregated_qualified_count", aggregate_summary.get("qualified_video_count", 0))
    min_likes = aggregate_summary.get("min_likes", aggregate_summary.get("min_likes_threshold", ""))
    category = clean_text(aggregate_summary.get("category"))
    market = clean_text(aggregate_summary.get("market"))
    profile_url = clean_text(profile_summary.get("profile_url") or profile_summary.get("profile_final_url"))
    session_quality = clean_text(profile_summary.get("session_quality"))
    patrol_queries = aggregate_summary.get("queries") or []
    patrol_topics = aggregate_summary.get("topics") or []

    summary_line = (
        f"真实 TikTok capture-pack 导入自 {display_path(capture_root)}，当前用于"
        f"{category or '未分类赛道'}"
        + (f"，市场 {market}" if market else "")
        + "。"
        + f"当前看板规模：{ranked_count} 条已排序 / {qualified_count} 条达标"
        + (f"，最低点赞阈值 {min_likes}" if str(min_likes).strip() else "")
        + "."
    )
    operator_line = (
        f"来源账号：{profile_url or '待补'}; "
        f"会话质量：{display_session_quality(session_quality)}; "
        f"查询词：{display_optional_list(short_list_text(patrol_queries, limit=3))}; "
        f"主题：{display_optional_list(short_list_text(patrol_topics, limit=3))}."
    )

    lines = [summary_line, operator_line]
    if ranked_videos:
        top = ranked_videos[0]
        top_metric = compact_metric_snapshot(top) or ranked_metric_summary(top)
        lines.append(
            "头部候选："
            f"{clean_text(top.get('video_url')) or clean_text(top.get('video_id'))} | "
            f"{sentence_clip(hook_text(top), limit=104) or 'hook 缺失'} | "
            f"{top_metric}."
        )
    if qualified_videos:
        winner = qualified_videos[0]
        winner_metric = compact_metric_snapshot(winner) or ranked_metric_summary(winner)
        lines.append(
            "达标对照："
            f"{clean_text(winner.get('video_url')) or clean_text(winner.get('video_id'))} | "
            f"{sentence_clip(core_topic_text(winner), limit=92) or '主题缺失'} | "
            f"{winner_metric}."
        )
    lines.append(f"采集根目录：{display_path(capture_root)}")
    return "\n".join(line for line in lines if line)


def build_evidence(capture_root: Path, aggregate_summary: dict, profile_summary: dict, ranked_videos: list[dict]) -> list[dict]:
    summary_source = capture_root / ("aggregate_summary.json" if (capture_root / "aggregate_summary.json").exists() else "summary.json")
    profile_source = capture_root / ("profile_summary.json" if (capture_root / "profile_summary.json").exists() else "summary.json")
    evidence = [
        {
            "label": "汇总",
            "detail": (
                f"已排序={aggregate_summary.get('aggregated_ranked_count', aggregate_summary.get('ranked_video_count', 0))}; "
                f"达标={aggregate_summary.get('aggregated_qualified_count', aggregate_summary.get('qualified_video_count', 0))}; "
                f"最低点赞={aggregate_summary.get('min_likes', aggregate_summary.get('min_likes_threshold', ''))}"
            ),
            "source": format_source_reference(summary_source, anchor=capture_root),
        },
        {
            "label": "账号汇总",
            "detail": (
                f"账号={clean_text(profile_summary.get('profile_url') or profile_summary.get('profile_final_url'))}; "
                f"会话={display_session_quality(profile_summary.get('session_quality'))}; "
                f"已排序={profile_summary.get('ranked_video_count', 0)}"
            ),
            "source": format_source_reference(profile_source, anchor=capture_root),
        },
    ]
    for video in top_videos(ranked_videos, limit=3):
        evidence.append(
            {
                "label": f"排序视频 {video.get('video_id', '')}",
                "detail": hook_text(video) or clean_text(video.get("caption_text")) or clean_text(video.get("desc")) or video_line(video),
                "source": clean_text(video.get("video_url")),
            }
        )
    return evidence


def build_assets(capture_root: Path) -> list[dict]:
    assets: list[dict] = []
    for name, note in [
        ("aggregate_report.md", "真实 TikTok capture pack 的汇总 Markdown 报告。"),
        ("aggregate_analysis.xlsx", "真实 TikTok capture pack 的汇总工作簿。"),
        ("aggregate_ranked_videos.xlsx", "排序视频工作簿。"),
        ("aggregate_qualified_videos.xlsx", "达标视频工作簿。"),
        ("ranked_videos.xlsx", "单次 TikTok capture pack 的排序视频工作簿。"),
        ("comments_flat.csv", "单次 TikTok capture pack 的扁平评论导出。"),
        ("patrol_snapshot.json", "Scene 02 标准化巡检快照。"),
        ("patrol_delta.json", "Scene 02 相对上一轮的快照差异。"),
        ("patrol_alerts.json", "Scene 02 基于巡检差异得出的告警决策。"),
        ("scene03_candidates.json", "Scene 02 巡检后交给 Scene 03 的短名单。"),
        ("patrol_config.json", "本轮使用的 Scene 02 巡检配置。"),
    ]:
        path = first_existing_path(capture_root, [name])
        if path:
            assets.append({"label": name, "path": format_source_reference(path, anchor=capture_root), "note": note})
    return assets


def collect_comment_entries(capture_root: Path) -> list[dict]:
    entries: list[dict] = []
    seen_ids: set[str] = set()
    comments_sampled_path = first_existing_path(capture_root, ["comments_sampled.json"])
    comments_sampled = load_json(comments_sampled_path) if comments_sampled_path else []
    if isinstance(comments_sampled, list):
        for video in comments_sampled:
            samples = video.get("samples", []) or []
            for sample in samples:
                comment_id = clean_text(sample.get("cid") or sample.get("comment_id"))
                if comment_id and comment_id in seen_ids:
                    continue
                if comment_id:
                    seen_ids.add(comment_id)
                entries.append(
                    {
                        "comment_id": comment_id,
                        "video_id": clean_text(video.get("video_id")),
                        "video_url": clean_text(video.get("video_url")),
                        "text": clean_text(sample.get("text")),
                        "raw_text": clean_text(sample.get("text")),
                        "digg_count": sample.get("digg_count", 0),
                        "reply_comment_total": sample.get("reply_comment_total", 0),
                        "nickname": clean_text(sample.get("nickname")),
                        "unique_id": clean_text(sample.get("unique_id")),
                        "source_product": clean_text(video.get("source_product") or video.get("unique_id") or video.get("video_id")),
                        "sample_kind": clean_text(sample.get("sample_kind") or "top_level"),
                        "reply_summary": clean_text(sample.get("reply_summary")),
                        "is_reply": clean_text(sample.get("sample_kind")).lower() == "reply",
                        "comment_language": clean_text(sample.get("comment_language")),
                        "author_verified": bool(sample.get("verified") or sample.get("author_verified")),
                        "high_purchase_intent": bool(sample.get("is_high_purchase_intent")),
                    }
                )

    comments_json_path = first_existing_path(capture_root, ["comments.json"])
    comments_payload = load_json(comments_json_path) if comments_json_path else {}
    if isinstance(comments_payload, dict):
        source_product = clean_text(
            comments_payload.get("source_product")
            or comments_payload.get("unique_id")
            or comments_payload.get("video_id")
            or comments_payload.get("source_url")
        )
        for sample in comments_payload.get("comments", []) or []:
            if not isinstance(sample, dict):
                continue
            comment_id = clean_text(sample.get("comment_id") or sample.get("cid"))
            if comment_id and comment_id in seen_ids:
                continue
            if comment_id:
                seen_ids.add(comment_id)
            author = sample.get("author") if isinstance(sample.get("author"), dict) else {}
            raw_block = sample.get("raw") if isinstance(sample.get("raw"), dict) else {}
            raw_user = raw_block.get("user") if isinstance(raw_block.get("user"), dict) else {}
            entries.append(
                {
                    "comment_id": comment_id,
                    "video_id": clean_text(sample.get("video_id") or comments_payload.get("video_id")),
                    "video_url": clean_text(sample.get("source_url") or comments_payload.get("source_url")),
                    "text": clean_text(sample.get("text") or raw_block.get("text")),
                    "raw_text": clean_text(sample.get("text") or raw_block.get("text")),
                    "digg_count": sample.get("digg_count", raw_block.get("digg_count", 0)),
                    "reply_comment_total": sample.get("reply_comment_total", raw_block.get("reply_comment_total", 0)),
                    "nickname": clean_text(author.get("nickname") or raw_user.get("nickname")),
                    "unique_id": clean_text(author.get("unique_id") or raw_user.get("unique_id")),
                    "source_product": source_product or clean_text(sample.get("video_id") or comments_payload.get("video_id")),
                    "sample_kind": "reply" if sample.get("is_reply") else "top_level",
                    "reply_summary": clean_text(sample.get("reply_summary")),
                    "is_reply": bool(sample.get("is_reply")),
                    "parent_comment_id": clean_text(sample.get("parent_comment_id")),
                    "comment_language": clean_text(raw_block.get("comment_language") or sample.get("comment_language")),
                    "author_verified": bool(author.get("verified") or clean_text(raw_user.get("custom_verify"))),
                    "high_purchase_intent": bool(raw_block.get("is_high_purchase_intent")),
                }
            )
    return entries


def load_scene02_runtime_files(capture_root: Path) -> tuple[dict, dict, list[dict], list[dict]]:
    snapshot = maybe_load(capture_root / "patrol_snapshot.json")
    delta = maybe_load(capture_root / "patrol_delta.json")
    alerts = maybe_load(capture_root / "patrol_alerts.json")
    scene03_candidates = maybe_load(capture_root / "scene03_candidates.json")
    return (
        snapshot if isinstance(snapshot, dict) else {},
        delta if isinstance(delta, dict) else {},
        alerts if isinstance(alerts, list) else [],
        scene03_candidates if isinstance(scene03_candidates, list) else [],
    )


def load_scene03_runtime_candidates(capture_root: Path) -> list[dict]:
    candidates = maybe_load(capture_root / "scene03_candidates.json")
    return candidates if isinstance(candidates, list) else []


def compact_join(values: list[str]) -> str:
    return ", ".join(item for item in values if item)


def short_list_text(values: list[object], limit: int = 3) -> str:
    cleaned = [clean_text(item) for item in values if clean_text(item)]
    if not cleaned:
        return ""
    shown = cleaned[:limit]
    if len(cleaned) <= limit:
        return ", ".join(shown)
    return ", ".join(shown) + f" +{len(cleaned) - limit} more"


def display_session_quality(value: object) -> str:
    text = clean_text(value)
    mapping = {
        "browser_same_origin_api_ok": "浏览器同源接口正常",
        "tikmatrix_profile_posts_export": "TikMatrix 主页帖子导出",
        "unknown": "待补",
    }
    return mapping.get(text, text or "待补")


def display_optional_list(value: str, *, empty_label: str = "未提供") -> str:
    text = clean_text(value)
    return text or empty_label


def compact_metric_snapshot(video: dict) -> str:
    parts: list[str] = []
    likes = video.get("digg_count", 0)
    plays = video.get("play_count", 0)
    shares = video.get("share_count", 0)
    comments = video.get("comment_count", 0)
    if likes:
        parts.append(f"{likes} 点赞")
    if plays:
        parts.append(f"{plays} 播放")
    if shares:
        parts.append(f"{shares} 分享")
    if comments:
        parts.append(f"{comments} 评论")
    return "，".join(parts)


def scene02_dispatch_memo(next_scene03: list[dict], capture_rows: list[list[str]]) -> list[str]:
    queue_rows = build_scene02_escalation_rows(next_scene03)
    queue_summary = "; ".join(
        f"{row[0]} {row[1]}: {row[2]}"
        for row in queue_rows[:3]
    )
    backlog = ", ".join(clean_text(row[0]) for row in capture_rows[:5]) if capture_rows else "none"
    return [
        f"Dispatch board: {queue_summary}" if queue_summary else "Dispatch board: top-ranked patrol candidate pending manual selection.",
        f"Data backlog: {backlog}.",
        "Operating rule: keep alert thresholds stable, escalate from the standing queue, and treat missing enrichment as a fix list rather than a reason to stop the patrol.",
    ]


def scene03_dispatch_memo(top_ranked: list[dict], scene03_candidates: list[dict]) -> list[str]:
    rows: list[str] = []
    if top_ranked:
        winner = top_ranked[0]
        rows.append(
            "Primary teardown control: "
            f"{clean_text(winner.get('video_url') or winner.get('video_id'))} | "
            f"{sentence_clip(hook_text(winner), limit=84) or 'hook missing'} | "
            f"{compact_metric_snapshot(winner) or ranked_metric_summary(winner)}."
        )
    if len(top_ranked) > 1:
        contrast = top_ranked[1]
        rows.append(
            "Contrast reference: "
            f"{clean_text(contrast.get('video_url') or contrast.get('video_id'))} | "
            f"{teardown_lane_label(contrast)} | "
            f"{compact_metric_snapshot(contrast) or ranked_metric_summary(contrast)}."
        )
    if scene03_candidates:
        rows.append(
            f"Patrol handoff: {len(scene03_candidates)} prioritized candidate(s) entered Scene 03 from the standing patrol queue."
        )
    rows.append(
        "Adaptation rule: preserve the recognition-first hook, then swap borrowed authority for owned proof, owned talent, or owned product context."
    )
    return rows


def publish_window_text(video: dict) -> str:
    raw = clean_text(video.get("created_at_utc"))
    if not raw:
        return "date missing"
    try:
        timestamp = int(raw)
    except ValueError:
        return raw
    try:
        return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")
    except (OverflowError, OSError, ValueError):
        return raw


def parse_video_datetime(video: dict) -> datetime | None:
    raw = clean_text(video.get("created_at_utc"))
    if raw:
        try:
            return datetime.fromisoformat(raw.replace("Z", "+00:00"))
        except ValueError:
            pass
        for fmt in [
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
        ]:
            try:
                return datetime.strptime(raw[: len(fmt)], fmt)
            except ValueError:
                continue
    raw_epoch = clean_text(video.get("create_time") or video.get("createTime") or video.get("publish_time"))
    if raw_epoch:
        try:
            return datetime.fromtimestamp(int(raw_epoch))
        except (TypeError, ValueError, OSError, OverflowError):
            pass
    for fmt in [
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
    ]:
        try:
            return datetime.strptime(raw_epoch[: len(fmt)], fmt)
        except ValueError:
            continue
    return None


def publish_week_label(video: dict) -> str:
    dt = parse_video_datetime(video)
    if dt is None:
        return "week unknown"
    iso_year, iso_week, _ = dt.isocalendar()
    return f"{iso_year}-W{iso_week:02d}"


def shortlist_rule_text(videos: list[dict], explicit_count: int | None = None) -> str:
    if explicit_count:
        return f"按 reuse-value 排序后取 Top {explicit_count}"
    if len(videos) >= 3:
        return "按 reuse-value 排序后取 Top 3 深拆"
    if len(videos) >= 1:
        return f"按 reuse-value 排序后取 Top {len(videos)} 深拆"
    return "短名单规则待补"


def resolve_scene03_top_n(aggregate_summary: dict, candidate_pool: list[dict], fallback: int = 3) -> int:
    top_n = clean_text(
        aggregate_summary.get("scene03_top_n")
        or aggregate_summary.get("shortlist_count")
        or aggregate_summary.get("top_n")
    )
    try:
        parsed = int(top_n)
    except (TypeError, ValueError):
        parsed = fallback
    parsed = max(1, parsed)
    if candidate_pool:
        return min(parsed, len(candidate_pool))
    return parsed


def scene03_shortlist_rule_from_summary(aggregate_summary: dict, candidate_pool: list[dict]) -> str:
    top_n = resolve_scene03_top_n(aggregate_summary, candidate_pool)
    search_count = clean_text(
        aggregate_summary.get("scene03_search_count")
        or aggregate_summary.get("search_count")
        or aggregate_summary.get("candidate_count")
    ) or "10"
    commerce_candidates = [
        item
        for item in candidate_pool
        if safe_int(item.get("commerce_confidence")) >= 60
        or clean_text(item.get("tkshop_signal")).lower() not in {"", "未检测到", "not_detected"}
    ]
    if commerce_candidates:
        return f"先搜 {search_count} 条，优先只在带货 / 购物车候选里按点赞取 Top {top_n} 深拆；不足时再用高分候选补位"
    if candidate_pool:
        return f"先搜 {search_count} 条，当前无强带货候选，按综合分与点赞共同排序取 Top {top_n} 深拆"
    return f"先搜 {search_count} 条，再按带货 / 购物车信号优先，取点赞 Top {top_n} 深拆"


def strongest_scene03_candidates(candidate_pool: list[dict], limit: int = 3) -> list[dict]:
    commerce_candidates = [
        item
        for item in candidate_pool
        if safe_int(item.get("commerce_confidence")) >= 60
        or clean_text(item.get("tkshop_signal")).lower() not in {"", "未检测到", "not_detected"}
    ]
    ranked_source = commerce_candidates or candidate_pool
    ranked = sorted(
        ranked_source,
        key=lambda item: (
            safe_int(item.get("digg_count")),
            safe_int(item.get("score")),
            safe_int(item.get("comment_count")),
            safe_int(item.get("share_count")),
        ),
        reverse=True,
    )
    if len(ranked) < limit and ranked_source is not candidate_pool:
        seen = {clean_text(item.get("video_url") or item.get("video_id")) for item in ranked}
        fallback_ranked = sorted(
            [item for item in candidate_pool if clean_text(item.get("video_url") or item.get("video_id")) not in seen],
            key=lambda item: (
                safe_int(item.get("score")),
                safe_int(item.get("digg_count")),
                safe_int(item.get("comment_count")),
                safe_int(item.get("share_count")),
            ),
            reverse=True,
        )
        ranked.extend(fallback_ranked[: max(0, limit - len(ranked))])
    return ranked[:limit]


def week_growth_ratio(latest_top: dict, prior_top: dict) -> float:
    latest_score = safe_int(latest_top.get("score"))
    prior_score = safe_int(prior_top.get("score"))
    latest_likes = safe_int(latest_top.get("digg_count"))
    prior_likes = safe_int(prior_top.get("digg_count"))
    base_score = prior_score if prior_score > 0 else 1
    base_likes = prior_likes if prior_likes > 0 else 1
    score_ratio = latest_score / base_score if latest_score else 0.0
    like_ratio = latest_likes / base_likes if latest_likes else 0.0
    return (score_ratio * 0.6) + (like_ratio * 0.4)


def account_dispatch_strength(account_videos: list[dict]) -> tuple[float, dict, dict]:
    account_compare = compare_latest_two_weeks(account_videos)
    latest_top = weekly_top_video(account_compare.get("latest_rows", []) or account_videos)
    prior_top = weekly_top_video(account_compare.get("prior_rows", []))
    if account_compare.get("mode") == "compare" and prior_top:
        ratio = week_growth_ratio(latest_top, prior_top)
    else:
        ratio = 1.0 + (safe_int(latest_top.get("score")) / 1000.0)
    return ratio, latest_top, account_compare


def scene01_config_summary(capture_root: Path, aggregate_summary: dict) -> list[str]:
    config = maybe_load(capture_root / "patrol_config.json")
    if not isinstance(config, dict):
        config = {}
    lines: list[str] = []
    category = clean_text(aggregate_summary.get("category") or config.get("category"))
    market = clean_text(aggregate_summary.get("market") or config.get("market"))
    cadence = clean_text(aggregate_summary.get("cadence") or config.get("cadence"))
    queries = config.get("queries") or aggregate_summary.get("queries") or []
    topics = config.get("topics") or aggregate_summary.get("topics") or []
    if category:
        lines.append(f"类别：{category}")
    if market:
        lines.append(f"地区：{market}")
    if cadence:
        lines.append(f"频率：{cadence}")
    if queries:
        lines.append(f"关键词：{short_list_text(queries, limit=5)}")
    if topics:
        lines.append(f"主题：{short_list_text(topics, limit=5)}")
    return lines


def scene01_config_rows(capture_root: Path, aggregate_summary: dict) -> list[list[str]]:
    config = maybe_load(capture_root / "patrol_config.json")
    if not isinstance(config, dict):
        config = {}
    category = clean_text(aggregate_summary.get("category") or config.get("category")) or "未指定"
    market = clean_text(aggregate_summary.get("market") or config.get("market")) or "未指定"
    cadence = clean_text(aggregate_summary.get("cadence") or config.get("cadence")) or "未指定"
    queries = short_list_text(config.get("queries") or aggregate_summary.get("queries") or [], limit=5) or "未提供"
    topics = short_list_text(config.get("topics") or aggregate_summary.get("topics") or [], limit=5) or "未提供"
    min_likes = clean_text(
        config.get("min_likes")
        or config.get("min_likes_threshold")
        or aggregate_summary.get("min_likes")
        or aggregate_summary.get("min_likes_threshold")
    ) or "未设"
    shortlist_count = clean_text(config.get("shortlist_count") or aggregate_summary.get("shortlist_count")) or "未设"
    sort_rule = clean_text(config.get("sort_by") or aggregate_summary.get("sort_by")) or "按综合得分 / reuse-value"
    publish_window = clean_text(
        config.get("publish_window")
        or config.get("date_window")
        or config.get("time_window")
        or aggregate_summary.get("publish_window")
        or aggregate_summary.get("date_window")
    ) or "本批抓取包未显式记录"
    shop_only_raw = config.get("shop_only")
    if shop_only_raw in (None, ""):
        shop_only_raw = config.get("only_shop")
    if shop_only_raw in (None, ""):
        shop_only_raw = config.get("only_cart")
    if shop_only_raw in (None, ""):
        shop_only_raw = aggregate_summary.get("shop_only")
    if shop_only_raw in (None, ""):
        shop_only_raw = aggregate_summary.get("only_cart")
    lowered_shop = clean_text(shop_only_raw).lower()
    if shop_only_raw is True or lowered_shop in {"true", "1", "yes", "y"}:
        shop_only = "是，仅看带购物车 / 带货信号视频"
        shop_required = "强约束"
    elif shop_only_raw is False or lowered_shop in {"false", "0", "no", "n"}:
        shop_only = "否，普通热视频也纳入"
        shop_required = "强约束"
    else:
        shop_only = "缺失，需补齐"
        shop_required = "必须补齐"
    publish_required = "强约束" if publish_window != "本批抓取包未显式记录" else "必须补齐"
    market_required = "强约束" if market != "未指定" else "必须补齐"
    sort_required = "强约束" if sort_rule != "按综合得分 / reuse-value" else "建议显式指定"
    return [
        ["采集类别", category, "锁定本次要看的品类板块，避免把不同内容池混在一起。"],
        ["地区 / 市场", market, f"让后续复用判断和竞争强度都落在同一市场语境里。当前要求：{market_required}。"],
        ["巡检频率", cadence, "决定这是一次性搜爆款，还是持续追加到同一张看板。"],
        ["关键词", queries, "保留本次到底搜了什么，便于复跑与补采。"],
        ["主题 / 标签", topics, "说明这批热视频来自哪些话题入口或标签池。"],
        ["发布时间窗口", publish_window, f"确保榜单是在同一时间窗内比较，而不是混入旧热视频。当前要求：{publish_required}。"],
        ["排序规则", sort_rule, f"明确 shortlist 是按什么逻辑排序，不把高播放误当高复用。当前要求：{sort_required}。"],
        ["最低点赞门槛", min_likes, "说明这批样本进入榜单前已经过了哪道热度筛选。"],
        ["短名单数量", shortlist_count, "决定后续 Scene 03 / 04 应该优先深拆多少条。"],
        ["只看购物车视频", shop_only, f"区分泛爆款研究和偏带货研究，避免分析目标漂移。当前要求：{shop_required}。"],
    ]


def scene01_required_input_rows(capture_root: Path, aggregate_summary: dict) -> list[list[str]]:
    config = maybe_load(capture_root / "patrol_config.json")
    if not isinstance(config, dict):
        config = {}
    publish_window = clean_text(
        config.get("publish_window")
        or config.get("date_window")
        or config.get("time_window")
        or aggregate_summary.get("publish_window")
        or aggregate_summary.get("date_window")
    )
    market = clean_text(aggregate_summary.get("market") or config.get("market"))
    sort_rule = clean_text(config.get("sort_by") or aggregate_summary.get("sort_by"))
    shop_only_raw = config.get("shop_only")
    if shop_only_raw in (None, ""):
        shop_only_raw = config.get("only_shop")
    if shop_only_raw in (None, ""):
        shop_only_raw = config.get("only_cart")
    if shop_only_raw in (None, ""):
        shop_only_raw = aggregate_summary.get("shop_only")
    if shop_only_raw in (None, ""):
        shop_only_raw = aggregate_summary.get("only_cart")
    lowered_shop = clean_text(shop_only_raw).lower()
    shop_value = "是" if shop_only_raw is True or lowered_shop in {"true", "1", "yes", "y"} else ("否" if shop_only_raw is False or lowered_shop in {"false", "0", "no", "n"} else "")
    rows = [
        ["发布时间窗口", publish_window or "缺失", "必须补齐", "缺了就无法保证榜单新鲜度可比"],
        ["地区 / 市场", market or "缺失", "必须补齐", "缺了就会把不同市场热视频混在一起"],
        ["sort_by", sort_rule or "缺失", "必须补齐", "缺了就不知道是按相关度还是按最多点赞筛选"],
        ["只看购物车视频", shop_value or "缺失", "必须补齐", "缺了就分不清泛热视频与带货研究目标"],
    ]
    return rows


def scene01_missing_required_inputs(required_rows: list[list[str]]) -> list[str]:
    missing: list[str] = []
    for row in required_rows:
        field_name = clean_text(row[0])
        current_value = clean_text(row[1])
        requirement = clean_text(row[2])
        if requirement == "必须补齐" and current_value in {"", "缺失"}:
            missing.append(field_name)
    return missing


def scene01_handoff_gate_text(required_rows: list[list[str]]) -> str:
    missing = scene01_missing_required_inputs(required_rows)
    if missing:
        return f"暂不建议直接全量交接 Scene 03；需先补齐：{compact_join(missing)}。"
    return "可以直接交接 Scene 03；强约束输入已齐，可按短名单优先级进入深拆。"


def scene01_gate_passed(required_rows: list[list[str]]) -> bool:
    return not scene01_missing_required_inputs(required_rows)


def scene01_row_handoff_status(video: dict, required_rows: list[list[str]]) -> str:
    if not scene01_gate_passed(required_rows):
        return "待补强约束输入"
    has_hook = bool(hook_text(video))
    has_topic = bool(core_topic_text(video))
    commerce = safe_int(video.get("commerce_confidence"))
    if has_hook and has_topic and commerce >= 70:
        return "允许直送 Scene 03"
    if has_hook or has_topic:
        return "允许入池，优先补文本"
    return "允许入池，作为对照样本"


def scene01_recommended_teardown_direction(video: dict) -> str:
    lane = teardown_lane_label(video)
    next_scene = scene01_best_next_scene(video)
    return f"{lane} | {next_scene}"


def scene19_best_publish_window_rows(videos: list[dict]) -> list[list[str]]:
    grouped: dict[str, list[dict]] = {}
    for video in videos:
        window = scene19_window_label(clean_text(video.get("publish_window")) or publish_week_label(video) or "窗口未标记")
        grouped.setdefault(window, []).append(video)
    rows: list[list[str]] = []
    for window, items in sorted(
        grouped.items(),
        key=lambda pair: max(safe_int(video.get("score")) for video in pair[1]) if pair[1] else 0,
        reverse=True,
    ):
        avg_score = int(sum(safe_int(item.get("score")) for item in items) / max(len(items), 1))
        avg_likes = int(sum(safe_int(item.get("digg_count")) for item in items) / max(len(items), 1))
        best = sorted(items, key=lambda item: (safe_int(item.get("score")), safe_int(item.get("digg_count"))), reverse=True)[0]
        rows.append(
            [
                window,
                f"{len(items)} 条样本 | 平均分 {avg_score} | 平均点赞 {avg_likes}",
                display_cue_text(best, limit=76, fallback=best.get("desc")) or clean_text(best.get("video_url")) or "代表样本待补",
                f"转化信号 / ROI 信号：{scene19_signal_label(best.get('conversion_proxy'))} / {scene19_signal_label(best.get('roi_proxy'))}",
            ]
        )
    return rows


def scene01_video_reason(video: dict) -> str:
    base = why_selected_text(video)
    reuse = clean_text(video.get("reuse_purpose"))
    if reuse:
        return f"{base} 适合复用：{reuse}"
    return base


def scene01_reuse_fit_text(video: dict) -> str:
    explicit = clean_text(video.get("reuse_purpose")) or clean_text(video.get("best_reuse_category") or video.get("reuse_value_label"))
    if explicit:
        return strip_display_noise(explicit)
    return reuse_value_label(video)


def scene01_best_next_scene(video: dict) -> str:
    explicit = clean_text(video.get("shortlist_decision"))
    if explicit:
        return strip_display_noise(explicit)
    lane = teardown_lane_label(video)
    if "证明" in lane or "权威" in lane:
        return "Scene 03 深拆证明链与权威替代"
    if "情绪" in lane:
        return "Scene 03 深拆情绪钩子与转化节奏"
    if "选题" in lane or "角度" in lane:
        return "Scene 03 深拆选题角度与结构共性"
    return "Scene 03 深拆首屏包装与脚本节奏"


def scene01_study_value_text(video: dict) -> str:
    explicit = clean_text(video.get("why_worth_studying")) or clean_text(video.get("why_selected"))
    if explicit:
        return strip_display_noise(explicit)
    parts: list[str] = []
    if hook_text(video):
        parts.append("首屏钩子已恢复")
    if core_topic_text(video):
        parts.append("主题线清晰")
    if safe_int(video.get("commerce_confidence")) >= 70:
        parts.append("带货意图强")
    if video.get("author_verified"):
        parts.append("有权威背书")
    if not parts:
        parts.append("综合表现强且具备复用价值")
    return "；".join(parts[:3])


def no_voiceover_support_line(video: dict) -> str:
    cue = display_cue_text(video, limit=86, fallback=video.get("desc"))
    if clean_text(video.get("caption_text")):
        return f"即使口播很弱，也能依靠字幕/首屏提示成立：{cue or '字幕或动作线索'}。"
    return f"这条更像无口播或弱口播视频，应从动作、切镜和证明物来还原：{cue or '动作与证明物线索待人工补充'}。"


def group_videos_by_publish_week(videos: list[dict]) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = {}
    for video in videos:
        week = publish_week_label(video)
        grouped.setdefault(week, []).append(video)
    return grouped


def weekly_account_summary_rows(videos: list[dict], *, label: str) -> list[list[str]]:
    rows: list[list[str]] = []
    grouped = group_videos_by_publish_week(videos)
    for week, week_videos in sorted(grouped.items(), reverse=True):
        ordered = sorted(
            week_videos,
            key=lambda item: (safe_int(item.get("score")), safe_int(item.get("digg_count"))),
            reverse=True,
        )
        top_video = ordered[0] if ordered else {}
        rows.append(
            [
                label,
                week,
                str(len(week_videos)),
                clean_text(top_video.get("video_url") or top_video.get("video_id")),
                display_cue_text(top_video, limit=84, fallback=top_video.get("desc")) or "头部关键信号缺失",
                teardown_lane_label(top_video) if top_video else "拆解方向缺失",
                compact_metric_snapshot(top_video) or ranked_metric_summary(top_video),
            ]
        )
    return rows


def video_account_key(video: dict) -> str:
    return (
        clean_text(video.get("unique_id"))
        or clean_text(video.get("author_unique_id"))
        or clean_text(video.get("profile_url"))
        or clean_text(video.get("nickname"))
        or clean_text(video.get("author_signature"))
    )


def video_account_label(video: dict) -> str:
    label = author_signal_text(video)
    if label:
        return label
    unique_id = clean_text(video.get("unique_id"))
    nickname = clean_text(video.get("nickname"))
    profile_url = clean_text(video.get("profile_url"))
    if unique_id and nickname and nickname.lower() != unique_id.lower():
        return f"{unique_id} / {nickname}"
    return unique_id or nickname or profile_url or "未标记账号"


def group_videos_by_account(videos: list[dict]) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = {}
    for video in videos:
        key = video_account_key(video) or "unknown-account"
        grouped.setdefault(key, []).append(video)
    return grouped


def distinct_account_count(videos: list[dict]) -> int:
    return len([key for key in group_videos_by_account(videos).keys() if key and key != "unknown-account"])


def ranked_account_groups(videos: list[dict]) -> list[tuple[str, list[dict]]]:
    grouped = group_videos_by_account(videos)
    return sorted(
        grouped.items(),
        key=lambda pair: max((safe_int(item.get("score")) for item in pair[1]), default=0),
        reverse=True,
    )


def compare_latest_two_weeks(videos: list[dict]) -> dict:
    grouped = group_videos_by_publish_week(videos)
    ordered_weeks = sorted(grouped.keys(), reverse=True)
    if not ordered_weeks:
        return {
            "mode": "none",
            "latest_week": "",
            "prior_week": "",
            "latest_rows": [],
            "prior_rows": [],
        }
    latest_week = ordered_weeks[0]
    prior_week = ordered_weeks[1] if len(ordered_weeks) > 1 else ""
    latest_rows = grouped.get(latest_week, [])
    prior_rows = grouped.get(prior_week, []) if prior_week else []
    return {
        "mode": "compare" if prior_week else "baseline",
        "latest_week": latest_week,
        "prior_week": prior_week,
        "latest_rows": latest_rows,
        "prior_rows": prior_rows,
    }


def weekly_coverage_summary(videos: list[dict], profile_summary: dict, comment_snapshot: dict) -> dict:
    grouped = group_videos_by_publish_week(videos)
    usable_weeks = [week for week in grouped.keys() if week and week != "week unknown"]
    return {
        "week_count": len(usable_weeks),
        "post_count": len(videos),
        "comment_count": safe_int(comment_snapshot.get("cleaned_count")),
        "comment_video_count": safe_int(profile_summary.get("comment_sampled_video_count")),
        "download_count": safe_int(profile_summary.get("video_download_success_count")),
        "account_count": max(safe_int(profile_summary.get("profile_count")), distinct_account_count(videos), 1),
    }


def weekly_evidence_grade(coverage: dict) -> str:
    if (
        safe_int(coverage.get("week_count")) >= 2
        and safe_int(coverage.get("comment_count")) >= 10
        and safe_int(coverage.get("download_count")) >= 1
    ):
        return "可直接周对比"
    if safe_int(coverage.get("week_count")) >= 2:
        return "可做轻周对比"
    if safe_int(coverage.get("week_count")) == 1:
        return "仅基线周"
    return "样本不足"


def weekly_evidence_note(coverage: dict) -> str:
    return (
        f"{safe_int(coverage.get('account_count'))} 个账号 / "
        f"{safe_int(coverage.get('week_count'))} 个自然周 / "
        f"{safe_int(coverage.get('post_count'))} 条帖子 / "
        f"{safe_int(coverage.get('comment_count'))} 条评论样本 / "
        f"{safe_int(coverage.get('download_count'))} 条下载成功"
    )


def weekly_shift_rows(videos: list[dict]) -> list[list[str]]:
    compare = compare_latest_two_weeks(videos)
    latest_rows = sorted(
        compare.get("latest_rows", []),
        key=lambda item: (safe_int(item.get("score")), safe_int(item.get("digg_count"))),
        reverse=True,
    )
    prior_rows = sorted(
        compare.get("prior_rows", []),
        key=lambda item: (safe_int(item.get("score")), safe_int(item.get("digg_count"))),
        reverse=True,
    )
    rows: list[list[str]] = []
    latest_week = clean_text(compare.get("latest_week"))
    prior_week = clean_text(compare.get("prior_week"))
    if compare.get("mode") == "baseline":
        for video in latest_rows[:3]:
            rows.append(
            [
                "仅基线周",
                clean_text(video.get("video_url") or video.get("video_id")),
                f"{latest_week} 基线周出现的强样本",
                strategy_change_text(video),
                "需要下一周同字段对比后再判断是否为策略变化",
                ]
            )
        return rows
    for index, video in enumerate(latest_rows[:3], start=1):
        prior_video = prior_rows[index - 1] if index - 1 < len(prior_rows) else {}
        rows.append(
            [
                f"{latest_week} vs {prior_week}",
                clean_text(video.get("video_url") or video.get("video_id")),
                f"本周：{display_cue_text(video, limit=72, fallback=video.get('desc')) or '线索缺失'}",
                f"上周：{display_cue_text(prior_video, limit=72, fallback=prior_video.get('desc')) or '无同层样本'}",
                f"变化判断：{strategy_change_text(video)}",
            ]
        )
    return rows


def scene18_multi_week_focus_rows(videos: list[dict]) -> list[list[str]]:
    rows: list[list[str]] = []
    for row in multi_week_pattern_rows(videos)[:2]:
        rows.append(
            [
                f"{row[0]} 周趋势",
                row[2],
                f"{row[1]} 条样本；头部线索：{row[3]}",
                row[4],
                row[5],
            ]
        )
    return rows


def scene18_matrix_summary_rows(videos: list[dict]) -> list[list[str]]:
    rows: list[list[str]] = []
    for _, account_videos in ranked_account_groups(videos)[:5]:
        account_compare = compare_latest_two_weeks(account_videos)
        latest_week = clean_text(account_compare.get("latest_week")) or "week unknown"
        prior_week = clean_text(account_compare.get("prior_week"))
        latest_rows = sorted(
            account_compare.get("latest_rows", []),
            key=lambda item: (safe_int(item.get("score")), safe_int(item.get("digg_count"))),
            reverse=True,
        )
        top_video = latest_rows[0] if latest_rows else weekly_top_video(account_videos)
        top_prior = weekly_top_video(account_compare.get("prior_rows", []))
        latest_likes = safe_int(top_video.get("digg_count"))
        prior_likes = safe_int(top_prior.get("digg_count"))
        if account_compare.get("mode") == "compare":
            week_note = f"{latest_week} {len(latest_rows)} 条"
            shift_note = f"{latest_week} vs {prior_week}"
            if prior_likes and latest_likes >= int(prior_likes * 1.35):
                trend_prefix = "本周明显增强"
            elif prior_likes and latest_likes <= int(prior_likes * 0.8):
                trend_prefix = "本周明显回落"
            else:
                trend_prefix = "本周相对持平"
            strategy_note = f"{trend_prefix}；{strategy_change_text(top_video) or '继续观察这条包装线是否会再复现一周'}"
        else:
            week_note = f"{latest_week} {len(latest_rows) or len(account_videos)} 条"
            shift_note = "仅基线周"
            strategy_note = "先把这周记为基线周，下周按同字段复采后再判断是否真的发生策略变化"
        rows.append(
            [
                video_account_label(top_video or account_videos[0]),
                week_note,
                clean_text(top_video.get("video_url") or top_video.get("video_id")),
                teardown_lane_label(top_video) or "未恢复主主题",
                display_cue_text(top_video, limit=76, fallback=top_video.get("desc")) or "本周关键信号缺失",
                shift_note,
                strategy_note if not top_prior else f"{strategy_note}；上周头部线：{teardown_lane_label(top_prior) or '未恢复'}",
            ]
        )
    return rows


def scene18_matrix_shift_rows(videos: list[dict]) -> list[list[str]]:
    rows: list[list[str]] = []
    for _, account_videos in ranked_account_groups(videos)[:4]:
        account_compare = compare_latest_two_weeks(account_videos)
        latest_rows = sorted(
            account_compare.get("latest_rows", []),
            key=lambda item: (safe_int(item.get("score")), safe_int(item.get("digg_count"))),
            reverse=True,
        )
        latest_top = latest_rows[0] if latest_rows else weekly_top_video(account_videos)
        prior_top = weekly_top_video(account_compare.get("prior_rows", []))
        label = video_account_label(latest_top or account_videos[0])
        latest_week = clean_text(account_compare.get("latest_week")) or "当前周"
        prior_week = clean_text(account_compare.get("prior_week")) or "上周"
        latest_likes = safe_int(latest_top.get("digg_count"))
        prior_likes = safe_int(prior_top.get("digg_count"))
        if account_compare.get("mode") == "compare":
            if prior_likes and latest_likes >= int(prior_likes * 1.35):
                implication = "这是明显增强，不只是小波动，值得优先看它是否真的改了包装主线。"
            elif prior_likes and latest_likes <= int(prior_likes * 0.8):
                implication = "这是明显回落，说明上周打法可能失效，或本周执行没有延续优势。"
            else:
                implication = "这是轻波动或相对持平，更像同一路线的小幅调整。"
            rows.append(
                [
                    f"{label} 周度变化",
                    f"{latest_week} vs {prior_week}",
                    implication,
                    f"本周：{display_cue_text(latest_top, limit=68, fallback=latest_top.get('desc')) or '线索缺失'}；上周：{display_cue_text(prior_top, limit=56, fallback=prior_top.get('desc')) or '无同层样本'}",
                    strategy_change_text(latest_top) or "继续看这条包装线是否在下一周延续。",
                ]
            )
        else:
            rows.append(
                [
                    f"{label} 基线周",
                    latest_week,
                    "当前只有一周样本，更适合作为后续周报的基线周起点，而不是直接下长期趋势判断。",
                    display_cue_text(latest_top, limit=76, fallback=latest_top.get('desc')) or "线索缺失",
                    "下周优先按同字段复采，再判断它是不是竞对真的在切策略。",
                ]
            )
    return rows


def scene18_matrix_dispatch_rows(videos: list[dict], comment_snapshot: dict) -> list[list[str]]:
    groups = ranked_account_groups(videos)
    if not groups:
        return [["继续观察", "暂无账号样本", "中", "先补账号帖子数据再决定动作"]]
    scored_groups = [account_dispatch_strength(account_videos) + ({},) for _, account_videos in groups]
    scored_groups = [(ratio, latest_top, compare, account_videos) for (ratio, latest_top, compare), (_, account_videos) in zip([account_dispatch_strength(g[1]) for g in groups], groups)]
    scored_groups.sort(key=lambda item: item[0], reverse=True)
    strongest_ratio, strongest_top, strongest_compare, strongest_group = scored_groups[0]
    weakest_ratio, weakest_top, weakest_compare, weakest_group = scored_groups[-1]
    strongest_label = video_account_label(strongest_top or strongest_group[0])
    weakest_label = video_account_label(weakest_top or weakest_group[0])
    comment_theme = (
        clean_text((comment_snapshot.get("top_reply_pattern") or {}).get("theme"))
        or clean_text((comment_snapshot.get("top_purchase_cluster") or {}).get("theme"))
        or "评论样本不足"
    )
    return [
        ["继续追", f"优先跟踪 {strongest_label}", "高", (strategy_change_text(strongest_top) or "这条包装线最像值得继续周度监控的主线。") + f" 强度系数={strongest_ratio:.2f}"],
        ["减少跟进", f"本周回落或弱势账号：{weakest_label}", "中", f"对明显回落的包装线先降优先级，除非它提供了别家没有的新证明结构。当前强度系数={weakest_ratio:.2f}"],
        ["忽略噪音", comment_theme, "中", "如果评论压力主要指向争议、误解或单次事件，不要直接把它当成长期内容升级信号。"],
    ]


def scene18_dispatch_rows(compare: dict, top_ranked: list[dict], comment_snapshot: dict) -> list[list[str]]:
    latest_week = clean_text(compare.get("latest_week")) or "本周"
    prior_week = clean_text(compare.get("prior_week")) or "上周"
    latest_rows = sorted(
        compare.get("latest_rows", []),
        key=lambda item: (safe_int(item.get("score")), safe_int(item.get("digg_count"))),
        reverse=True,
    )
    prior_rows = sorted(
        compare.get("prior_rows", []),
        key=lambda item: (safe_int(item.get("score")), safe_int(item.get("digg_count"))),
        reverse=True,
    )
    watch_video = latest_rows[0] if latest_rows else (top_ranked[0] if top_ranked else {})
    prior_top = prior_rows[0] if prior_rows else {}
    comment_theme = (
        clean_text((comment_snapshot.get("top_reply_pattern") or {}).get("theme"))
        or clean_text((comment_snapshot.get("top_purchase_cluster") or {}).get("theme"))
        or "评论样本不足"
    )
    if compare.get("mode") == "compare":
        watch_lane = teardown_lane_label(watch_video)
        prior_lane = teardown_lane_label(prior_top) if prior_top else "上周样本不足"
        shift_note = strategy_change_text(watch_video) or "继续观察本周包装是否会复现到下周"
        return [
            ["本周继续追", f"{latest_week} 的头部包装线", f"{watch_lane} | {display_cue_text(watch_video, limit=76, fallback=watch_video.get('desc')) or '缺少关键信号'}", shift_note],
            ["本周值得借鉴", f"{latest_week} 对比 {prior_week}", f"本周 {watch_lane}；上周 {prior_lane}", "只复制可迁移的开头信号、证明方式和镜头节奏，不复制账号权威壳。"],
            ["本周应忽略", "疑似一次性分发放大", comment_theme, "若优势只来自账号体量、官方身份或单次事件流量，不要直接当成可复制公式；先等下一周复采确认。"],
        ]
    return [
        ["本周继续追", "当前基线头部包装线", f"{teardown_lane_label(watch_video)} | {display_cue_text(watch_video, limit=76, fallback=watch_video.get('desc')) or '缺少关键信号'}", "把这条当基线，下周同字段复采后再判断是否稳定连胜。"],
        ["本周值得借鉴", "可迁移的内容包装", proof_style_text(watch_video) or "证明方式待补", "先试较小账号版本，观察包装是否仍成立。"],
        ["本周应忽略", "基线阶段的噪音信号", comment_theme, "还没有第二周对照时，不要把单周异常误判成长期策略升级；先把它记为观察项。"],
    ]


def scene02_change_digest_rows(
    alerts: list[dict],
    new_videos: list[dict],
    breakout_videos: list[dict],
    repeated_hooks: list[dict],
    next_scene03: list[dict],
    rising_videos: list[dict] | None = None,
) -> list[list[str]]:
    rows: list[list[str]] = []
    rising_videos = rising_videos or []
    if new_videos:
        top_new = new_videos[0]
        rows.append(
            [
                "今日新增",
                f"新增 {len(new_videos)} 条进入监控面板；代表样本：{clean_text(top_new.get('video_url') or top_new.get('video_id'))}",
                sentence_clip(
                    display_cue_text(top_new, limit=88, fallback=top_new.get("desc")) or "新样本文案待补",
                    limit=88,
                ),
                "是，优先看是否进入 Scene 03 队列" if next_scene03 else "先继续观察是否形成稳定上升",
            ]
        )
    if breakout_videos:
        top_breakout = breakout_videos[0]
        rows.append(
            [
                "今日上升",
                f"爆发或明显上升 {len(breakout_videos)} 条；代表样本：{clean_text(top_breakout.get('video_url') or top_breakout.get('video_id'))}",
                compact_metric_snapshot(top_breakout) or ranked_metric_summary(top_breakout),
                "是，进入深拆候选",
            ]
        )
    elif rising_videos:
        top_rising = rising_videos[0]
        rows.append(
            [
                "今日温和上升",
                f"有 {len(rising_videos)} 条指标在涨但未过爆发阈值；代表样本：{clean_text(top_rising.get('video_url') or top_rising.get('video_id'))}",
                f"like_jump={safe_int(top_rising.get('like_jump'))}, score_jump={safe_int(top_rising.get('score_jump'))}",
                "先观察一轮，若继续加速再进 Scene 03",
            ]
        )
    if alerts:
        top_alert = alerts[0]
        rows.append(
            [
                clean_text(top_alert.get("signal") or top_alert.get("label") or "异常信号"),
                clean_text(top_alert.get("meaning") or top_alert.get("detail") or top_alert.get("reason")) or "本轮触发了需人工复核的异常变化。",
                clean_text(top_alert.get("follow_up") or top_alert.get("next_action")) or "先复核后决定是否升级到 Scene 03",
                "视信号强度决定",
            ]
        )
    if repeated_hooks:
        hook = repeated_hooks[0]
        rows.append(
            [
                "重复 hook",
                clean_text(hook.get("hook_text") or hook.get("label") or "多个账号出现相近开头"),
                "说明品类正在收敛到更固定的包装方式，需要判断是可复用规律还是跟风噪音。",
                "是，适合作为 Scene 03 的共性拆解入口",
            ]
        )
    if not rows:
        top_candidate = next_scene03[0] if next_scene03 else {}
        rows.append(
            [
                "今日无强变动",
                "没有新增、爆发或异常超过阈值，本轮以站立队列为主。",
                clean_text(top_candidate.get("video_url") or top_candidate.get("video_id")) or "沿用当前排名第一候选",
                "保持 Scene 03 站立队列，不扩大搜集面",
            ]
        )
    return rows[:4]


def scene03_reusable_formula_rows(videos: list[dict]) -> list[list[str]]:
    evidence_ref = clean_text(videos[0].get("video_url")) if videos else "top-ranked-reference"
    return [
        [
            "开头钩子",
            "沿用让人一眼看懂的首句识别信号",
            "保留首句承诺，但把原视频的人 / 物 / 主题替换成自有版本",
            "不要用泛化铺垫开场",
            evidence_ref,
        ],
        [
            "证明段",
            "用权威、出镜人或可识别社会线索承接证明",
            "把借来的账号势能换成自有证明物、创作者或使用场景",
            "证明太弱，整套结构就会塌",
            evidence_ref,
        ],
        [
            "包装方式",
            "文案保持短、原生、主题一眼可懂",
            "保留压缩后的主题 cue，减少解释性废话",
            "解释过多会把结构拉平",
            evidence_ref,
        ],
        [
            "软收口 / CTA",
            "优先用延续式收口或下一次点击引导",
            "更适合引导继续看、收藏、去主页，而不是硬卖",
            "强转化 CTA 可能破坏原生适配",
            evidence_ref,
        ],
    ]


def scene03_risk_rows(videos: list[dict]) -> list[list[str]]:
    top = videos[0] if videos else {}
    second = videos[1] if len(videos) > 1 else {}
    return [
        [
            "Authority inflation",
            clean_text(top.get("video_url") or top.get("video_id")) or "Top ranked post",
            "Check whether the format still works after removing verified-account or featured-person lift.",
        ],
        [
            "Thin caption recovery",
            clean_text(second.get("video_url") or second.get("video_id")) or "Backup sample",
            "If the hook text is thin, require screenshot, subtitle, or downloaded metadata before overlearning structure.",
        ],
        [
            "Topic overfit",
            "Shortlist-level pattern",
            "Preserve the packaging move, but rewrite the topic and proof lane before calling the format reusable.",
        ],
    ]


def scene03_next_action_rows(videos: list[dict]) -> list[list[str]]:
    rows: list[list[str]] = []
    for index, video in enumerate(videos[:3], start=1):
        rows.append(
            [
                f"优先深拆 {index}",
                clean_text(video.get("video_url") or video.get("video_id")) or f"shortlist-{index}",
                clean_text(video.get("shortlist_decision")) or teardown_lane_label(video),
                scene02_candidate_owner(video),
            ]
        )
    if not rows:
        rows.append(
            [
                "优先深拆 1",
                "未恢复 shortlist 链接",
                "先人工指定当前最强候选，再补深拆入口",
                "运营 / 策略",
            ]
        )
    return rows


def scene04_production_spec_rows(source: dict, source_url: str, source_hook: str, source_topic: str, authority: str) -> list[list[str]]:
    proof_line = authority or no_voiceover_support_line(source)
    return [
        [
            "镜头 1",
            "首屏必须先让人一眼看懂谁/什么值得看",
            "开头认知建立",
            source_hook or "一句能立刻看懂的首屏提示",
            "人物 / 对象 / 情绪 cue",
            "首屏画面、字幕或标题卡",
            "medium",
        ],
        [
            "镜头 2",
            source_topic or "用极短场景或上下文补齐前提",
            "场景设定",
            source_topic or "一句补全前提的话",
            "压缩解释，避免拖慢",
            "承接镜头或环境线索",
            "medium",
        ],
        [
            "镜头 3",
            proof_line,
            "证明段",
            proof_style_text(source) if authority else no_voiceover_support_line(source),
            "把信任放到前半段",
            "证明物、结果、人物或动作",
            "medium",
        ],
        [
            "镜头 4",
            "回到主画面并给一个轻量软收口",
            "收口 / CTA",
            "看下一条 / 保存 / 继续看 / 轻量关注",
            "维持 TikTok 原生节奏",
            source_url or "收口镜头",
            "low-to-medium",
        ],
    ]


def scene04_structure_rows(source: dict, source_url: str, source_desc: str, source_hook: str, source_topic: str, authority: str) -> list[list[str]]:
    visual_hook = display_cue_text(source, limit=90, fallback=source_desc) or "首屏画面或字幕 cue 待人工补"
    setup_line = source_topic or source_desc or "用一句极短前提交代场景，让观众知道这条在讲什么"
    proof_line = authority or proof_style_text(source) or no_voiceover_support_line(source)
    spoken_hook = source_hook or sentence_clip(source_desc, limit=86) or "首屏字幕 / 口播待补"
    proof_script = proof_style_text(source) if authority else no_voiceover_support_line(source)
    asset_hint = "优先保留首屏截图、封面、下载视频或关键帧"
    return [
        [
            "00:00-00:03",
            "开头钩子",
            visual_hook,
            spoken_hook,
            "先让观众在第一眼看懂谁 / 什么值得继续看",
            asset_hint,
            source_url or "primary-video",
        ],
        [
            "00:03-00:08",
            "场景设定",
            setup_line,
            sentence_clip(setup_line, limit=90),
            "补足最少必要前提，避免观众在理解前流失",
            "需要场景承接画面、字幕或环境线索",
            source_url or "primary-video",
        ],
        [
            "00:08-00:14",
            "证明段",
            proof_line,
            proof_script,
            "把信任、结果或权威尽量前置，不靠长解释推进",
            "需要证明物、人物、结果画面或可复核下载源",
            source_url or "primary-video",
        ],
        [
            "00:14-00:20",
            "收口 / CTA",
            "回到主画面并给一个轻量软收口",
            "继续看 / 保存 / 轻量关注 / 去主页看完整内容",
            "用 TikTok 原生节奏收口，而不是硬切强转化",
            "需要收口镜头或主页 / 继续看指向",
            source_url or "primary-video",
        ],
    ]


def scene04_mechanism_rows(source: dict, video_type: str, authority: str, source_url: str) -> list[list[str]]:
    return [
        [
            "视频类型",
            video_type,
            "先判定这是哪类单视频，再决定后续复刻该保什么、不该抄什么。",
            "如果类型判断错了，后续会把情绪拼贴、教程、权威背书混为一谈。",
            source_url or "primary-video",
        ],
        [
            "注意力张力",
            "首屏识别优先，前半段尽快进入证明",
            "观众在解释开始前就知道为什么该继续看。",
            "首屏如果只铺垫不兑现，停留和后续证明都会一起变弱。",
            source_url or "primary-video",
        ],
        [
            "证明装置",
            authority or proof_style_text(source),
            "用人、权威、结果、动作或文化线索做快速可信度转移。",
            "如果证明只停留在口头描述，这条结构就会变成普通讲解。",
            source_url or "primary-video",
        ],
        [
            "无口播兜底",
            scene04_no_voiceover_judgment(source),
            "即使没有完整口播，也能依靠字幕、切镜和动作把逻辑传出去。",
            "如果字幕和画面 cue 都弱，就必须补更多截图 / 下载细节后再深拆。",
            source_url or "primary-video",
        ],
    ]


def scene04_storyboard_handoff_rows(source: dict, source_url: str, source_hook: str, source_topic: str, authority: str) -> list[list[str]]:
    visual_hook = display_cue_text(source, limit=88, fallback=source.get("desc")) or "首屏识别线索待补"
    proof_line = authority or proof_style_text(source) or no_voiceover_support_line(source)
    return [
        [
            "shot_01",
            "0-3s",
            "首屏识别",
            visual_hook,
            source_hook or "一句让人立刻看懂的开头",
            "hero_hook",
            "首屏主画面 / 封面 / 标题卡",
        ],
        [
            "shot_02",
            "3-8s",
            "补前提",
            source_topic or "用一句极短前提交代场景",
            sentence_clip(source_topic or source.get("desc"), limit=84) or "补一行澄清性字幕",
            "premise_setup",
            "承接镜头 / 场景线索 / 字幕",
        ],
        [
            "shot_03",
            "8-14s",
            "证明段",
            proof_line,
            proof_style_text(source) if authority else no_voiceover_support_line(source),
            "proof_block",
            "证明物 / 结果 / 人物 / 凭证",
        ],
        [
            "shot_04",
            "14-20s",
            "软收口",
            "回到主线索并引导继续看 / 保存 / 轻量关注",
            "给一个低摩擦延续动作，不要硬卖",
            "cta_close",
            source_url or "收口镜头 / 主页指向",
        ],
    ]


def scene05_generator_schema_rows(source: dict, source_url: str, source_hook: str, source_topic: str, proof_style: str, music_style: str) -> list[list[str]]:
    return [
        ["Style", source_topic or "识别优先的编辑型包装", "保留识别优先，但换成你的产品主张", "style", source_url or "primary-video", "medium"],
        ["Environment", "社交原生、前提单一、先识别后证明", "只保留真实能拍到 / 能生成的场景", "environment", "真实场景或产品图", "low"],
        ["Tone & Pacing", "快 setup、早 proof、轻收口", "避免长解释，优先让人秒懂", "tone_pacing", "节奏脚本", "medium"],
        ["Camera", "首屏先给最强识别线索，再围绕证明收紧", "如果没有真人镜头，就用产品 / 证明物替代", "camera", "镜头计划", "low"],
        ["Lighting", "清楚可信优先，不追求过度电影感", "保证证明层可见、可读、可信", "lighting", "画面风格约束", "low"],
        ["Character", author_signal_text(source) or "识别对象 / 创作者 / 证明物", "换成自有创作者、用户、产品或凭证", "character", "人物或证明物清单", "medium"],
        ["Shots", f"{source_hook or '开头'} -> {source_topic or '铺垫'} -> {proof_style} -> 软收口", "按 shot_01 到 shot_04 逐镜头改写", "shots", "分镜表", "medium"],
        ["Background Sound", music_style, "保留 editorial 原生感，但不要盖过主线索", "background_sound", "音频选择", "low"],
        ["Transition", "短节拍、少空镜、在看点清楚前不做长铺垫", "所有转场都服务于清晰推进", "transition", "剪辑约束", "medium"],
    ]


def scene05_product_adapt_rows(source: dict, source_hook: str, source_topic: str, proof_style: str) -> list[list[str]]:
    return [
        ["hook", source_hook or "识别优先开头", "换成你的产品承诺或用户痛点", "需要一眼能懂的首屏物件 / 人物 / 结果", "若首屏不可识别，就必须加重证明"],
        ["premise", source_topic or "压缩前提", "只保留让观众继续看的最小前提", "需要一句极短澄清性字幕", "不要把 premise 写成长说明"],
        ["proof", proof_style, "把账号权威换成自有证明物 / 凭证 / 口碑", "需要真实 proof asset", "证明不足时不要假装有权威"],
        ["cta_close", "轻量延续式收口", "改成继续看 / 收藏 / 了解更多 / 去主页", "需要真实 CTA 去向", "强卖式 CTA 会破坏原生节奏"],
    ]


def scene17_publish_slot_label(video: dict) -> str:
    raw_window = clean_text(video.get("publish_window"))
    if raw_window:
        return scene19_window_label(raw_window)
    dt = parse_video_datetime(video)
    if dt is None:
        return "窗口未标记"
    weekday = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][dt.weekday()]
    hour = dt.hour
    if hour < 12:
        part = "上午"
    elif hour < 18:
        part = "下午"
    else:
        part = "晚间"
    return f"{weekday}{part}"


def scene17_update_frequency_text(videos: list[dict]) -> str:
    dts = [dt for dt in [parse_video_datetime(video) for video in videos] if dt is not None]
    if len(dts) < 2:
        return "当前样本时间点不足，只能给出粗略更新频率。"
    ordered = sorted(dts)
    gaps_hours = [(ordered[index] - ordered[index - 1]).total_seconds() / 3600 for index in range(1, len(ordered))]
    avg_gap = sum(gaps_hours) / len(gaps_hours)
    if avg_gap <= 18:
        return f"高频更新，平均间隔约 {avg_gap:.0f} 小时。"
    if avg_gap <= 36:
        return f"接近日更，平均间隔约 {avg_gap:.0f} 小时。"
    if avg_gap <= 96:
        return f"周内多更，平均间隔约 {avg_gap/24:.1f} 天。"
    return f"更新偏稀，平均间隔约 {avg_gap/24:.1f} 天。"


def scene17_best_publish_window_text(videos: list[dict]) -> str:
    grouped: dict[str, list[dict]] = {}
    for video in videos:
        grouped.setdefault(scene17_publish_slot_label(video), []).append(video)
    if not grouped:
        return "发布时间窗样本不足"
    ranked = sorted(
        grouped.items(),
        key=lambda pair: (
            sum(safe_int(item.get("digg_count")) for item in pair[1]) / max(len(pair[1]), 1),
            sum(safe_int(item.get("play_count")) for item in pair[1]) / max(len(pair[1]), 1),
        ),
        reverse=True,
    )
    slot, items = ranked[0]
    return f"{slot} 最强（样本 {len(items)} 条）"


def scene17_high_low_compare_rows(high_video: dict, low_video: dict) -> list[list[str]]:
    return [
        [
            "开头钩子",
            hook_text(high_video) or "高互动样本钩子待补",
            hook_text(low_video) or "低互动样本钩子待补",
            "高互动版本通常更快让人知道为什么值得继续看。",
        ],
        [
            "证明装置",
            proof_style_text(high_video),
            proof_style_text(low_video),
            "真正可迁移的是证明顺序，不是账号壳子本身。",
        ],
        [
            "内容类型",
            scene04_video_type(high_video),
            scene04_video_type(low_video),
            "要先知道赢的是哪种内容类型，再决定是否值得复用。",
        ],
        [
            "发布时间窗",
            scene17_publish_slot_label(high_video),
            scene17_publish_slot_label(low_video),
            "时间窗只能辅助判断，不能替代内容结构差异。",
        ],
    ]


def scene17_formula_library_rows(videos: list[dict]) -> list[list[str]]:
    from content_graph import shortlist_provenance_cell

    rows: list[list[str]] = []
    for index, video in enumerate(videos[:3], start=1):
        lane = teardown_lane_label(video)
        if "证明" in lane or "权威" in lane:
            template = "先给一个可识别人物 / 结果，再立刻补上自有证明物。"
        elif "情绪" in lane:
            template = "先给情绪或时刻感，再用一句证明把情绪落到具体对象。"
        elif "选题" in lane or "角度" in lane:
            template = "先抛出反常识角度，再快速证明为什么这件事值得信。"
        else:
            template = "先给一眼能懂的识别线索，再用最短路径把证明推到前面。"
        rows.append(
            [
                f"公式 {index}",
                hook_text(video) or display_cue_text(video, limit=80, fallback=video.get("desc")) or "原始钩子待补",
                template,
                scene17_publish_slot_label(video),
                f"{clean_text(video.get('video_url')) or f'creator-top-{index}'} | {shortlist_provenance_cell(video)}",
            ]
        )
    return rows


def scene19_dispatch_rows(compare: dict, high_video: dict, low_video: dict, comment_snapshot: dict) -> list[list[str]]:
    latest_week = clean_text(compare.get("latest_week")) or "本周"
    prior_week = clean_text(compare.get("prior_week")) or "上周"
    comment_theme = (
        clean_text((comment_snapshot.get("top_reply_pattern") or {}).get("theme"))
        or clean_text((comment_snapshot.get("top_complaint_cluster") or {}).get("theme"))
        or clean_text((comment_snapshot.get("top_purchase_cluster") or {}).get("theme"))
        or "评论样本不足"
    )
    high_mode = content_mode_text(high_video) or "高表现内容模式待补"
    low_mode = content_mode_text(low_video) or "低表现内容模式待补"
    high_cue = display_cue_text(high_video, limit=76, fallback=high_video.get("desc")) or "高表现关键信号缺失"
    low_cue = display_cue_text(low_video, limit=76, fallback=low_video.get("desc")) or "低表现关键信号缺失"
    if compare.get("mode") == "compare":
        latest_window = scene19_window_label(clean_text(high_video.get("publish_window")) or publish_week_label(high_video) or latest_week)
        weak_window = scene19_window_label(clean_text(low_video.get("publish_window")) or publish_week_label(low_video) or prior_week)
        return [
            ["本周多做", high_mode, f"{latest_week} / {latest_window} 里表现更强：{high_cue}", "把下轮排期向这类开头信号、镜头组织和轻解释包装倾斜。"],
            ["本周少做", low_mode, f"{prior_week} / {weak_window} 弱势线索：{low_cue}", "减少开头铺垫长、证明弱、识别慢的版本占比。"],
            ["本周停止", "借权威壳但无自有证明", comment_theme, "如果只是借账号体量撑起来，下一轮不要继续放大同类空心版本。"],
            ["下轮测试", "高模式 vs 低模式 对照", f"保持发布时间窗近似一致，优先复测 {latest_window}", "用同题材 A/B 测试看内容模式差异是否稳定复现，并补评论 / 下载证据。"],
        ]
    return [
        ["本周多做", high_mode, high_cue, "把下轮更多名额给识别快、轻解释、强社会线索的版本。"],
        ["本周少做", low_mode, low_cue, "缩减前奏过长、进入慢、证明弱的内容模式。"],
        ["本周停止", "把外部账号权威误当自家可复制能力", comment_theme, "没有自有证明物时，不要只抄外壳。"],
        ["下轮测试", "人物驱动 vs 证明物驱动", "同主题、同窗口发两版", "看哪条更能带来稳定互动质量或更接近 ROI 目标，并补足第二周对照。"],
    ]


def scene19_signal_label(value: object) -> str:
    text = clean_text(value).strip()
    if not text:
        return "未恢复"
    label_map = {
        "cart_question_very_high": "购物车追问很强",
        "cart_question_high": "购物车追问强",
        "comment_interest_medium": "评论兴趣中等",
        "weak_cart_signal": "购物车信号弱",
        "best_save_comment_mix": "收藏评论组合最佳",
        "strong_save_to_play_ratio": "收藏播放比强",
        "strong_comment_to_save_ratio": "评论收藏比强",
        "weaker_save_to_play_ratio": "收藏播放比偏弱",
        "low_save_to_play_ratio": "收藏播放比低",
        "polished_but_low_conversion_proxy": "成片完整但转化 proxy 偏弱",
    }
    return label_map.get(text, text.replace("_", " "))


def scene19_window_label(value: object) -> str:
    text = clean_text(value).strip()
    if not text:
        return "窗口未标记"
    replacements = {
        "lateweek evening": "周后段晚间",
        "midweek evening": "周中晚间",
        "earlyweek evening": "周前段晚间",
        "lateweek morning": "周后段上午",
        "midweek morning": "周中上午",
        "weekend evening": "周末晚间",
        "weekend afternoon": "周末下午",
    }
    normalized = text
    for source, target in replacements.items():
        normalized = normalized.replace(source, target)
    return normalized


def scene19_content_mode_label(value: object) -> str:
    text = clean_text(value).strip()
    if not text:
        return "未分类模式"
    label_map = {
        "founder-proof": "创始人出镜证明型",
        "proof-object-demo": "证明物直给演示型",
        "aesthetic-montage": "审美拼贴型",
        "slow-explainer": "慢解释型",
    }
    return label_map.get(text, text.replace("_", " "))


def scene19_window_signal_rows(videos: list[dict]) -> list[list[str]]:
    grouped: dict[str, list[dict]] = {}
    for video in videos:
        window = scene19_window_label(clean_text(video.get("publish_window")) or publish_week_label(video))
        grouped.setdefault(window or "窗口未标记", []).append(video)

    rows: list[list[str]] = []
    for window, items in grouped.items():
        ordered = sorted(
            items,
            key=lambda item: (safe_int(item.get("score")), safe_int(item.get("digg_count"))),
            reverse=True,
        )
        high = ordered[0] if ordered else {}
        low = ordered[-1] if ordered else {}
        mode_counter = Counter(scene19_content_mode_label(item.get("content_type")) or content_mode_text(item) or "未分类" for item in items)
        top_mode = mode_counter.most_common(1)[0][0] if mode_counter else "未分类"
        conversion_counter = Counter(clean_text(item.get("conversion_proxy")) for item in items if clean_text(item.get("conversion_proxy")))
        roi_counter = Counter(clean_text(item.get("roi_proxy")) for item in items if clean_text(item.get("roi_proxy")))
        top_conversion = scene19_signal_label(conversion_counter.most_common(1)[0][0]) if conversion_counter else "未恢复"
        top_roi = scene19_signal_label(roi_counter.most_common(1)[0][0]) if roi_counter else "未恢复"
        rows.append(
            [
                window,
                top_mode,
                f"最高分 {safe_int(high.get('score'))} / 最低分 {safe_int(low.get('score'))}",
                f"转化信号：{top_conversion}；ROI 信号：{top_roi}",
                (
                    f"头部样本：{display_cue_text(high, limit=72, fallback=high.get('desc')) or clean_text(high.get('video_url')) or '线索待补'}；"
                    f"低表现对照：{display_cue_text(low, limit=56, fallback=low.get('desc')) or clean_text(low.get('video_url')) or '线索待补'}"
                ),
            ]
        )
    return rows


def scene19_roi_cluster_rows(videos: list[dict]) -> list[list[str]]:
    rows: list[list[str]] = []
    grouped: dict[str, list[dict]] = {}
    for video in videos:
        key = scene19_content_mode_label(video.get("content_type")) or content_mode_text(video) or "未分类模式"
        grouped.setdefault(key, []).append(video)

    for key, items in sorted(
        grouped.items(),
        key=lambda pair: max(safe_int(video.get("score")) for video in pair[1]) if pair[1] else 0,
        reverse=True,
    ):
        ordered = sorted(
            items,
            key=lambda item: (safe_int(item.get("score")), safe_int(item.get("digg_count"))),
            reverse=True,
        )
        top = ordered[0]
        windows = sorted({scene19_window_label(clean_text(item.get("publish_window")) or publish_week_label(item)) for item in items if clean_text(item.get("publish_window")) or publish_week_label(item)})
        conversion = scene19_signal_label(top.get("conversion_proxy"))
        roi = scene19_signal_label(top.get("roi_proxy"))
        rows.append(
            [
                key,
                f"{len(items)} 条 | {compact_join(windows[:2]) or '窗口未标记'}",
                display_cue_text(top, limit=76, fallback=top.get("desc")) or clean_text(top.get("video_url")) or "代表帖子待补",
                f"转化信号：{conversion}；ROI 信号：{roi}",
                "更值得保留" if safe_int(top.get("score")) >= 80 else "继续观察",
            ]
        )
    return rows


def scene19_high_low_signal_rows(high_video: dict, low_video: dict, multi_week_rows: list[list[str]]) -> list[list[str]]:
    high_window = scene19_window_label(clean_text(high_video.get("publish_window")) or publish_week_label(high_video) or "窗口未标记")
    low_window = scene19_window_label(clean_text(low_video.get("publish_window")) or publish_week_label(low_video) or "窗口未标记")
    high_conversion = scene19_signal_label(high_video.get("conversion_proxy"))
    low_conversion = scene19_signal_label(low_video.get("conversion_proxy"))
    high_roi = scene19_signal_label(high_video.get("roi_proxy"))
    low_roi = scene19_signal_label(low_video.get("roi_proxy"))
    trend_note = multi_week_rows[0][5] if multi_week_rows else "当前更适合作为基线模板，不宜过度归因。"
    trend_window = multi_week_rows[0][4] if multi_week_rows else "仅基线周"
    return [
        [
            "高表现组",
            f"{scene19_content_mode_label(high_video.get('content_type')) or content_mode_text(high_video) or '识别优先内容模式'} | {high_window}",
            f"高分样本同时带出 {high_conversion} 与 {high_roi}，说明它不只是热度高，更接近可承接的增长 / 转化信号。",
            "优先把这类内容作为下轮排期主力，并保留同窗口对照。",
        ],
        [
            "低表现组",
            f"{scene19_content_mode_label(low_video.get('content_type')) or content_mode_text(low_video) or '解释优先内容模式'} | {low_window}",
            f"低分样本更像 {low_conversion} 与 {low_roi}，说明包装再完整，也可能没有把购买或保存动机拉起来。",
            "缩减这类前奏长、证明弱、转化 proxy 弱的内容占比。",
        ],
        [
            "多周 / 多窗口提示",
            trend_window,
            trend_note,
            "保持同发布时间窗复测，否则很难判断是模式升级，还是时间窗红利。",
        ],
    ]


def scene19_test_plan_rows(high_video: dict, low_video: dict) -> list[list[str]]:
    high_window = scene19_window_label(clean_text(high_video.get("publish_window")) or publish_week_label(high_video) or "高表现窗口")
    low_window = scene19_window_label(clean_text(low_video.get("publish_window")) or publish_week_label(low_video) or "低表现窗口")
    high_mode = scene19_content_mode_label(high_video.get("content_type")) or content_mode_text(high_video) or "高表现模式"
    low_mode = scene19_content_mode_label(low_video.get("content_type")) or content_mode_text(low_video) or "低表现模式"
    return [
        [
            f"{high_mode} vs {low_mode}",
            "如果高表现模式真的更接近转化，它在相近窗口下应该继续赢。",
            f"同主题各做一版，尽量分别落在 {high_window} 与相近晚间窗口。",
            "高表现模式继续拿到更强购物车追问、收藏或评论组合。",
        ],
        [
            "证明物 vs 美感包装",
            "即使不借大账号权威，只要证明物更早出现，也能压过纯审美蒙太奇。",
            "把一条低表现美感版改成更早给结果、人物或证明物的版本。",
            "评论里出现更多问价格、问购买、问效果的真实购买语言。",
        ],
        [
            "发布时间窗稳定复测",
            "窗口漂移会掩盖真实内容差异。",
            f"下一轮继续固定在 {high_window} 一带，不要把测试样本拆散到随机时间。",
            "同窗口下仍能复现高低差异，才值得升级成排期规则。",
        ],
    ]


def summarize_content_mode_clusters(videos: list[dict]) -> list[list[str]]:
    grouped: dict[str, list[dict]] = {}
    for video in videos:
        key = content_mode_text(video) or teardown_lane_label(video).replace(" teardown", "") or "Unclassified mode"
        grouped.setdefault(key, []).append(video)
    rows: list[list[str]] = []
    for key, items in sorted(
        grouped.items(),
        key=lambda pair: max(safe_int(video.get("score")) for video in pair[1]) if pair[1] else 0,
        reverse=True,
    ):
        top = sorted(
            items,
            key=lambda item: (safe_int(item.get("score")), safe_int(item.get("digg_count"))),
            reverse=True,
        )[0]
        rows.append(
            [
                teardown_lane_label(top).replace(" teardown", ""),
                key,
                f"{len(items)} 条帖子："
                + compact_join([clean_text(item.get("video_url") or item.get("video_id")) for item in items[:2]]),
                display_cue_text(top, limit=88, fallback=top.get("desc")) or clean_text(top.get("video_url")) or "线索缺失",
                f"最高分={safe_int(top.get('score'))} | 平均点赞={int(sum(safe_int(item.get('digg_count')) for item in items) / max(len(items), 1))}",
            ]
        )
    return rows


def infer_scene_from_capture_pack(ranked_videos: list[dict], qualified_videos: list[dict], comment_entries: list[dict]) -> tuple[str, dict]:
    reason = []
    if comment_entries:
        reason.append("Comment samples detected, so scene 08 is the strongest direct fit.")
        return "08", {"comment_count": len(comment_entries), "reasons": reason}
    if qualified_videos:
        reason.append("Qualified winners detected, so scene 03 is the strongest direct fit for shortlist + teardown.")
        return "03", {"qualified_count": len(qualified_videos), "reasons": reason}
    if ranked_videos:
        reason.append("Ranked videos detected without comment evidence, so scene 17 is the strongest direct fit for account/creator distillation.")
        return "17", {"ranked_count": len(ranked_videos), "reasons": reason}
    raise SystemExit("Could not infer a scene from the capture pack. No ranked videos or comment samples were found.")


from comment_pipeline import (
    build_comment_cluster_rows,
    build_scene08_price_band_rows,
    build_scene08_source_product_rows,
    clean_comment_entries,
    comment_signal_snapshot,
    ensure_comment_pack_artifacts,
    scene08_cluster_note,
    scene08_reply_chain_line,
    scene08_reply_chain_synthesis,
    summarize_comment_clusters,
    summarize_reply_patterns,
)


def load_comment_pack(capture_root: Path) -> dict:
    raw_entries = collect_comment_entries(capture_root)
    return ensure_comment_pack_artifacts(capture_root, raw_entries)


def week_sort_key(week_label: str) -> tuple[int, int]:
    match = re.match(r"(\d{4})-W(\d{1,2})$", clean_text(week_label))
    if match:
        return int(match.group(1)), int(match.group(2))
    return (0, 0)


def dominant_lane(videos: list[dict]) -> str:
    lanes = [teardown_lane_label(video) for video in videos if teardown_lane_label(video)]
    if not lanes:
        return "未恢复"
    return Counter(lanes).most_common(1)[0][0]


def weekly_top_video(videos: list[dict]) -> dict:
    ordered = sorted(
        videos,
        key=lambda item: (safe_int(item.get("score")), safe_int(item.get("digg_count"))),
        reverse=True,
    )
    return ordered[0] if ordered else {}


def multi_week_pattern_rows(videos: list[dict]) -> list[list[str]]:
    grouped = group_videos_by_publish_week(videos)
    rows: list[list[str]] = []
    ordered_weeks = sorted(grouped.keys(), key=week_sort_key, reverse=True)
    previous_lane = ""
    previous_likes = 0
    for week in ordered_weeks[:4]:
        week_videos = grouped.get(week, [])
        top_video = weekly_top_video(week_videos)
        lane = dominant_lane(week_videos)
        top_likes = safe_int(top_video.get("digg_count"))
        if not previous_lane:
            trend_tag = "当前基线周"
        elif lane == previous_lane and top_likes >= previous_likes:
            trend_tag = "连续复现"
        elif lane == previous_lane and top_likes < previous_likes:
            trend_tag = "同模式回落"
        elif top_likes >= previous_likes:
            trend_tag = "新冒头模式"
        else:
            trend_tag = "模式切换但量级未升"
        implication = {
            "连续复现": "优先继续追，同步拆它为什么能连周成立。",
            "同模式回落": "保留模式判断，但不要把本周回落样本继续放大投放。",
            "新冒头模式": "作为新策略变化重点核查，确认是不是本周真正切换。",
            "模式切换但量级未升": "先观察，不要急着把新包装当长期主线。",
            "当前基线周": "作为后续每周对比的起点。",
        }.get(trend_tag, "继续观察。")
        rows.append(
            [
                week,
                str(len(week_videos)),
                lane or "未恢复",
                display_cue_text(top_video, limit=72, fallback=top_video.get("desc")) or "头部线索缺失",
                trend_tag,
                implication,
            ]
        )
        previous_lane = lane
        previous_likes = top_likes
    return rows


def metric_value(video: dict, key: str) -> int:
    value = video.get(key, 0)
    if isinstance(value, bool):
        return int(value)
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def choose_reference_pool(ranked_videos: list[dict], qualified_videos: list[dict], limit: int = 4) -> list[dict]:
    pool = qualified_videos or ranked_videos
    return top_videos(pool, limit=limit)


def style_label(index: int, video: dict) -> str:
    desc = clean_text(video.get("desc")).lower()
    if "@" in desc:
        return f"Creator-led style {index}"
    if any(token in desc for token in ["reminder", "moment", "little", "story"]):
        return f"Emotion-led style {index}"
    if any(token in desc for token in ["proud", "blowing", "psa", "watching"]):
        return f"Community-led style {index}"
    return f"Editorial style {index}"


def classify_audience_lens(video: dict) -> str:
    desc = clean_text(video.get("desc")).lower()
    if "@" in desc:
        return "Fans of a recognizable creator or collaborator"
    if any(token in desc for token in ["reminder", "little moments", "proud"]):
        return "Viewers seeking emotional resonance and identity signal"
    if any(token in desc for token in ["stemtok", "creativity"]):
        return "Viewers attracted to achievement, creativity, or cultural momentum"
    return "General TikTok viewers who respond to fast recognition"


def build_scene_11_pipeline_rows(references: list[dict]) -> list[list[str]]:
    top_ref = references[0] if references else {}
    second_ref = references[1] if len(references) > 1 else top_ref
    third_ref = references[2] if len(references) > 2 else second_ref
    return [
        [
            "Discovery",
            f"{len(references)} ranked/qualified TikTok candidates from the real capture pack",
            "Only keep posts with clear recognition-first packaging and strong engagement shape",
            "Ranked links plus metric snapshot",
            "Operator / researcher",
            "Shortlist-ready intake board",
            "Daily or per collection cycle",
        ],
        [
            "Shortlist",
            display_cue_text(top_ref, limit=88, fallback=top_ref.get("desc")) or "Top candidate hook",
            "Prioritize the post with the clearest hook, proof cue, and soft continuation CTA",
            "1-3 replication-worthy references with teardown lane labels",
            "Strategist / lead operator",
            "Approved top-set board",
            "Same-day",
        ],
        [
            "Teardown",
            clean_text(second_ref.get("video_url")) or clean_text(top_ref.get("video_url")),
            "Separate transferable hook/pacing logic from official-account or celebrity lift",
            "Teardown worksheet or scene-03 style notes",
            "Strategist / analyst",
            "Hook-proof-CTA breakdown",
            "Same-day",
        ],
        [
            "Replication brief",
            display_cue_text(top_ref, limit=88, fallback=top_ref.get("desc")) or "Recognition-first replication control",
            "Preserve the first-frame promise but swap in owned proof, creator, or product angle",
            "2-3 adapted creative directions",
            "Creative strategist",
            "Brief-ready variants",
            "Within 24h",
        ],
        [
            "Production queue",
            clean_text(third_ref.get("video_url")) or clean_text(top_ref.get("video_url")),
            "Ship the clearest recognition-first variant first, then test one alternate proof device",
            "Approved brief plus owned assets",
            "Production / growth",
            "Prioritized weekly test queue",
            "Weekly",
        ],
    ]


def build_scene_11_invariant_rows(references: list[dict]) -> list[list[str]]:
    top_ref = references[0] if references else {}
    return [
        [
            "Entry threshold",
            "Only admit ranked references with a legible first-frame cue, one visible proof angle, and enough source text to rewrite.",
            "Without this gate the queue fills with account-lifted posts that cannot survive adaptation.",
        ],
        [
            "Teardown lens",
            f"Use {clean_text(top_ref.get('video_url')) or 'the top reference'} to separate hook, proof, and continuation CTA before anyone writes variants.",
            "The pipeline breaks if teardown stays impressionistic instead of being reduced to transferable building blocks.",
        ],
        [
            "Queue standard",
            "No brief enters production until the borrowed authority has been replaced by one owned proof object, creator, or use case.",
            "This keeps weekly tests comparable and prevents the team from shipping hollow clones of official-account winners.",
        ],
    ]


def build_scene_11_learning_rows(references: list[dict]) -> list[list[str]]:
    top_ref = references[0] if references else {}
    return [
        [
            "Which recognition-first hook is portable without official-account lift?",
            "This decides whether the format is usable outside the original TikTok account.",
            f"Compare first 3 seconds hold and engagement on the adaptation of {clean_text(top_ref.get('video_id')) or 'the top post'}.",
            "Whether this format deserves scale or stays a one-off reference.",
            "Promote the hook family into the standing queue.",
            "Drop it from the repeatable pipeline and keep only as inspiration.",
        ],
        [
            "How much proof is needed when platform authority is weaker?",
            "Smaller accounts need stronger owned proof to preserve trust.",
            "Track save/share/comment quality across proof-light versus proof-heavy variants.",
            "Whether proof-light edits can survive without borrowed trust.",
            "Standardize the proof block in future briefs.",
            "Move to proof-heavier packaging for this lane.",
        ],
        [
            "What weekly volume can one operator sustain?",
            "A replication pipeline only matters if it is actually repeatable.",
            "Count candidates sourced, teardowns finished, and briefs shipped per cycle.",
            "Whether the workflow is operationally light enough to keep.",
            "Lock the cadence and owner model.",
            "Reduce queue width or simplify the handoff requirements.",
        ],
    ]


def build_scene_11_handoff_rows(references: list[dict]) -> list[list[str]]:
    top_ref = references[0] if references else {}
    second_ref = references[1] if len(references) > 1 else top_ref
    third_ref = references[2] if len(references) > 2 else top_ref
    return [
        [
            "Discovery shortlist",
            "Research / operator",
            "Top candidates already carry ranked metrics, a visible hook cue, and a tentative teardown lane.",
            "Shortlist quality drops if captions or authority cues are missing from intake.",
        ],
        [
            "Teardown packet",
            "Strategist / analyst",
            f"{clean_text(second_ref.get('video_url')) or clean_text(top_ref.get('video_url')) or 'Top control'} has a hook-proof-CTA breakdown plus account-lift notes.",
            "If borrowed authority is not isolated here, the later brief will overfit the source account.",
        ],
        [
            "Replication brief bank",
            "Creative strategist",
            "Each winning reference has 2-3 owned-proof rewrite directions with one primary control and one contrast lane.",
            "The brief bank stalls when the owned proof asset is not named before scripting starts.",
        ],
        [
            "Production queue",
            "Growth / production lead",
            f"{clean_text(third_ref.get('video_url')) or clean_text(top_ref.get('video_url')) or 'First queued variant'} is prioritized with owner, launch order, and success metric.",
            "Queue velocity breaks if production receives ideas instead of ranked, asset-ready variants.",
        ],
    ]


def build_scene_12_invariant_rows(references: list[dict]) -> list[list[str]]:
    top_ref = references[0] if references else {}
    return [
        ["Core message", "Lead with a recognition-first editorial promise before explanation.", "All variants must test packaging, not change the core promise."],
        ["Product truth", "Replace official-account trust with one owned proof object, creator, or use case.", "Without a stable proof source, test results will not be comparable."],
        ["Target outcome", f"Turn the top reference format ({clean_text(top_ref.get('video_url')) or 'top ranked post'}) into 4 testable variants.", "All rows should compete for the same outcome, not different goals."],
    ]


def build_scene_12_expected_effect_rows(references: list[dict]) -> list[list[str]]:
    rows: list[list[str]] = []
    for index, video in enumerate(references[:4], start=1):
        style = style_label(index, video)
        lane = teardown_lane_label(video).replace(" teardown", "")
        if "Creator-led" in style:
            attention_shift = "Should improve thumb-stop by borrowing recognizable human context faster."
            conversion_shift = "Should lift follow/save if the owned creator or collaborator is credible."
            risk = "Falls apart if the borrowed recognition cue cannot be replaced with owned talent."
        elif "Emotion-led" in style:
            attention_shift = "Should improve first-second resonance through emotion or identity framing."
            conversion_shift = "Should lift comments/saves when the proof object feels personal, not corporate."
            risk = "Can become vague if the owned proof line is weaker than the emotional opener."
        elif "Community-led" in style:
            attention_shift = "Should attract niche or momentum-driven viewers by signaling shared culture fast."
            conversion_shift = "Should lift shares if the audience wants to pass along the moment or angle."
            risk = "May narrow reach if the cultural cue is too insider or detached from the product."
        else:
            attention_shift = "Should test whether neutral editorial packaging can hold attention without celebrity or platform lift."
            conversion_shift = "Should show whether the product can convert on proof structure alone."
            risk = "Low distinctiveness if the lane is not anchored to a sharper owned hook."
        rows.append([style, attention_shift, conversion_shift, f"Main lane: {lane}. Risk: {risk}"])
    while len(rows) < 4:
        index = len(rows) + 1
        rows.append(
            [
                f"Style {index}",
                "Needs owned hook before an attention-shift forecast is honest.",
                "Needs product truth and proof source before a conversion-shift forecast is honest.",
                "Do not launch until the owned asset and audience lens are named.",
            ]
        )
    return rows


def build_scene_12_handoff_rows(references: list[dict]) -> list[list[str]]:
    rows: list[list[str]] = []
    for index, video in enumerate(references[:4], start=1):
        style = style_label(index, video)
        if "Creator-led" in style:
            asset_need = "Owned creator, collaborator, or spokesperson frame plus one proof beat"
            owner = "Creative strategist + talent / creator owner"
            ready_when = "The replacement face and proof line are both approved."
        elif "Emotion-led" in style:
            asset_need = "Owned emotional cue, lifestyle/context visual, and one simple proof object"
            owner = "Strategist + production lead"
            ready_when = "The opening moment and the supporting proof visual are both storyboarded."
        elif "Community-led" in style:
            asset_need = "Owned culture/momentum cue, event angle, or social proof artifact"
            owner = "Growth lead + strategist"
            ready_when = "The community angle is real and one share-worthy proof cue is attached."
        else:
            asset_need = "Owned product hook, visual direction, and proof object"
            owner = "Product marketing + creative"
            ready_when = "A distinct fourth style exists beyond cosmetic wording changes."
        rows.append([style, asset_need, owner, ready_when])
    while len(rows) < 4:
        index = len(rows) + 1
        rows.append(
            [
                f"Style {index}",
                "Owned hook, product asset, and proof object still missing",
                "Creative + product owner",
                "Ready only after the missing owned inputs are attached to the row.",
            ]
        )
    return rows


def build_scene_12_priority_rows(references: list[dict]) -> list[list[str]]:
    style_rows = build_scene_12_style_rows(references)
    reasons = [
        "Best first control because it most closely matches the top-ranked recognition pattern while staying adaptable.",
        "Launch second to test whether emotion framing beats pure recognition once the proof source stays constant.",
        "Hold as the contrast lane to test whether culture/community framing earns better shares than the top two.",
        "Keep last until the team has a genuinely distinct fourth lane with owned assets instead of placeholder wording.",
    ]
    rows: list[list[str]] = []
    for index in range(4):
        style = style_rows[index][0] if index < len(style_rows) else f"Style {index + 1}"
        rows.append([str(index + 1), style, reasons[index]])
    return rows


def build_scene_12_style_rows(references: list[dict]) -> list[list[str]]:
    rows: list[list[str]] = []
    for index, video in enumerate(references[:4], start=1):
        desc = display_cue_text(video, limit=88, fallback=video.get("desc")) or f"Reference hook {index}"
        rows.append(
            [
                style_label(index, video),
                classify_audience_lens(video),
                desc,
                "Owned proof object or collaborator trust replacing official-account authority",
                "Short editorial framing with fast first-frame recognition",
                "Soft continuation CTA toward next watch, save, or profile action",
                f"Based on ranked TikTok reference {clean_text(video.get('video_id')) or index}",
                "Medium",
                "Recognition-first packaging should beat explanation-first structure for this audience lens.",
                "Confirms whether this audience lens deserves a permanent slot in the test matrix.",
            ]
        )
    while len(rows) < 4:
        index = len(rows) + 1
        rows.append(
            [
                f"Style {index}",
                "Needs product-specific audience lens",
                "Needs owned-product hook",
                "Needs owned proof device",
                "Needs concrete visual asset direction",
                "Needs CTA",
                "Fill after product assets are added",
                "Unknown",
                "Needs product-specific hypothesis",
                "Needs test rationale before launch",
            ]
        )
    return rows


def build_scene_12_learning_matrix(references: list[dict]) -> list[list[str]]:
    rows: list[list[str]] = []
    for index, video in enumerate(references[:4], start=1):
        rows.append(
            [
                style_label(index, video),
                "Recognition-first packaging will outperform explanation-first setup when paired with credible proof.",
                f"Measure thumb-stop, hold rate, and save/share quality against reference {clean_text(video.get('video_id')) or index}.",
                "Whether this packaging family deserves more volume next cycle.",
                "Promote this style into the first-wave test set.",
                "Demote or rewrite the style before more spend or production.",
            ]
        )
    while len(rows) < 4:
        index = len(rows) + 1
        rows.append([f"Style {index}", "Needs product-specific hypothesis", "Needs success signal", "Needs learning objective", "Needs promote rule", "Needs reject rule"])
    return rows


def asset_label(index: int, total: int) -> str:
    labels = [
        "Main image",
        "Scene image",
        "Benefit image",
        "Detail image",
        "Short video",
    ]
    if index < len(labels):
        return labels[index]
    return f"Support asset {index + 1}"


def reference_message(video: dict) -> str:
    desc = clean_text(video.get("desc"))
    return desc[:90] or clean_text(video.get("video_url")) or "Need owned hook"


def build_scene_14_asset_rows(references: list[dict]) -> list[list[str]]:
    purposes = [
        "Win the first click with one recognition-first hero promise",
        "Carry the same promise into a lifestyle or context frame",
        "Make one benefit concrete without losing the social-native feel",
        "Support credibility with one proof or detail layer",
        "Turn the same message into a short motion-first launch asset",
    ]
    formats = ["1:1 or 4:5", "4:5", "4:5", "1:1 or 4:5", "9:16"]
    priorities = ["P1", "P1", "P2", "P2", "P1"]
    rows: list[list[str]] = []
    total = max(5, len(references))
    for index in range(5):
        video = references[index] if index < len(references) else (references[-1] if references else {})
        rows.append(
            [
                asset_label(index, total),
                purposes[index],
                reference_message(video),
                formats[index],
                priorities[index],
            ]
        )
    return rows


def build_scene_14_learning_rows(references: list[dict]) -> list[list[str]]:
    first_ref = references[0] if references else {}
    second_ref = references[1] if len(references) > 1 else first_ref
    return [
        [
            "Does one shared hero promise improve launch coherence across static and motion assets?",
            "The family should feel coordinated instead of like unrelated deliverables.",
            f"Compare the hero promise adapted from {clean_text(first_ref.get('video_id')) or 'the top reference'} across image and short-video launch assets.",
        ],
        [
            "Which proof layer is required once official-account authority is removed?",
            "The reference pack carries built-in platform trust that may not transfer.",
            "Test one asset family with stronger owned proof and one with lighter editorial proof.",
        ],
        [
            "Which asset should ship first when production bandwidth is limited?",
            "A launch family only helps if the P1 asset order is explicit.",
            f"Use the creative direction anchored by {clean_text(second_ref.get('video_id')) or 'the second reference'} as the first production control.",
        ],
    ]


def visual_code_label(video: dict) -> str:
    desc = clean_text(video.get("desc")).lower()
    if "@" in desc:
        return "Creator/partner recognition"
    if any(token in desc for token in ["reminder", "little moments", "psa"]):
        return "Emotion-first editorial cover"
    if any(token in desc for token in ["creativity", "stemtok", "breakthrough"]):
        return "Achievement / culture cue"
    return "Recognition-first social cover"


def click_driver_label(video: dict) -> str:
    desc = clean_text(video.get("desc")).lower()
    if "@" in desc:
        return "Known person or collaborator curiosity"
    if any(token in desc for token in ["psa", "reminder"]):
        return "Fast emotional recognition"
    if any(token in desc for token in ["creativity", "stemtok"]):
        return "Proof of notable outcome or talent"
    return "Immediate pattern recognition"


def weakness_note(video: dict) -> str:
    desc = clean_text(video.get("desc")).lower()
    if "@" in desc:
        return "Depends partly on collaborator or account recognition."
    if any(token in desc for token in ["psa", "reminder", "little moments"]):
        return "Could become too vague without a stronger owned proof object."
    return "Needs clearer owned product or outcome translation."


def keep_or_avoid_note(video: dict) -> str:
    return "Keep the fast recognition cue; avoid borrowing official-account authority literally."


def build_scene_16_rows(references: list[dict]) -> list[list[str]]:
    rows: list[list[str]] = []
    for video in references[:3]:
        rows.append(
            [
                clean_text(video.get("video_id")) or clean_text(video.get("video_url")) or "Reference",
                visual_code_label(video),
                click_driver_label(video),
                weakness_note(video),
                keep_or_avoid_note(video),
            ]
        )
    while len(rows) < 3:
        rows.append(
            [
                "Needs owned image sample",
                "Owned product visual code missing",
                "Cannot benchmark click driver honestly yet",
                "No owned image or product sample to compare",
                "Add owned main image before final outperform brief",
            ]
        )
    return rows


def parse_target_markets(raw: str, fallback_market: str = "") -> list[str]:
    markets = [item.strip() for item in raw.split(",") if item.strip()]
    if not markets and fallback_market.strip():
        markets = [fallback_market.strip()]
    deduped: list[str] = []
    for item in markets:
        if item not in deduped:
            deduped.append(item)
    return deduped


def parse_target_languages(raw: str) -> list[str]:
    languages = [item.strip() for item in raw.split(",") if item.strip()]
    deduped: list[str] = []
    for item in languages:
        if item not in deduped:
            deduped.append(item)
    return deduped


def build_scene_13_market_rows(references: list[dict], markets: list[str]) -> list[list[str]]:
    rows: list[list[str]] = []
    source_refs = references or [{}]
    for index, market in enumerate(markets[:3]):
        video = source_refs[index % len(source_refs)]
        rows.append(
            [
                market,
                classify_audience_lens(video),
                reference_message(video),
                "Needs native copy adaptation after owned product and local-language evidence are added",
                "Do not reuse official-account tone or culture cue blindly",
            ]
        )
    while len(rows) < 3:
        rows.append(
            [
                "Add target market",
                "Audience cue pending",
                "Hook direction pending",
                "Language / tone pending",
                "Need market-specific avoid list",
            ]
        )
    return rows


def build_scene_15_message_rows(references: list[dict], languages: list[str]) -> list[list[str]]:
    rows: list[list[str]] = []
    source_refs = references or [{}]
    block_specs = [
        ("Primary image text block", "Headline"),
        ("Secondary support block", "Support line"),
        ("CTA or badge block", "CTA placeholder"),
    ]
    for language in languages[:3]:
        video = source_refs[len(rows) % len(source_refs)]
        reference_id = clean_text(video.get("video_id")) or clean_text(video.get("video_url")) or "top ranked TikTok reference"
        for source_block, function_name in block_specs:
            rows.append(
                [
                    f"{source_block} | {language} | source text missing, OCR required",
                    function_name,
                    "Requires native translation after OCR, product context, and layout review",
                    f"Infer hierarchy from {reference_id}; do not treat ranked captions as final translated image copy",
                ]
            )
    if not rows:
        rows.append(
            [
                "Primary image text block | source text missing, OCR required",
                "Headline",
                "Requires native translation after OCR, product context, and layout review",
                "Add explicit target languages before building the localization grid",
            ]
        )
    return rows


def build_scene_15_structure_rows() -> list[list[str]]:
    return [
        ["Headline", "P1", "Preserve the shortest, highest-contrast message area; expect length expansion in many languages."],
        ["Support line", "P2", "Keep supporting proof or qualifier text visually subordinate to the headline."],
        ["CTA / badge", "P3", "Leave room for shorter action language or localized trust cue without crowding the image."],
    ]


def fill_common(
    payload: dict,
    project: str,
    context: str,
    capture_root: Path,
    aggregate_summary: dict,
    profile_summary: dict,
    ranked_videos: list[dict],
    qualified_videos: list[dict],
    content_graph: dict | None = None,
) -> None:
    payload["metadata"]["project"] = project
    payload["metadata"]["title"] = f"Scene {payload['metadata']['scene']} Report - {project}"
    payload["metadata"]["generated_at"] = datetime.now().isoformat(timespec="seconds")
    payload["metadata"]["status"] = "imported"

    working = payload["working_context"]
    working["summary"] = context
    working["inputs"] = [
        f"Profile: {clean_text(profile_summary.get('profile_url') or profile_summary.get('profile_final_url'))}",
        f"Ranked video count: {profile_summary.get('ranked_video_count', 0)}",
        f"Qualified video count: {profile_summary.get('qualified_video_count', 0)}",
        f"Capture root: {display_path(capture_root)}",
    ]
    for line in scene01_config_summary(capture_root, aggregate_summary):
        if line not in working["inputs"]:
            working["inputs"].append(line)
    extra_constraints = [
        "Conclusions should stay tied to ranked metrics, captions, and capture-pack summaries only.",
    ]
    if not collect_comment_entries(capture_root):
        extra_constraints.insert(0, "Real TikTok anonymous-session capture. Comment sampling is missing in this pack.")
    working["constraints"] = list(dict.fromkeys(working.get("constraints", []) + extra_constraints))
    working["requested_outputs"] = list(dict.fromkeys(working.get("requested_outputs", []) + [
        "TikTok-native ranked-pattern conclusions",
        "Reusable adaptation rules grounded in the capture pack",
    ]))
    working["minimum_evidence"] = list(dict.fromkeys(working.get("minimum_evidence", []) + [
        "summary.json or aggregate_summary.json",
        "profile_summary.json or summary.json",
        "ranked_videos.json or aggregate_ranked_videos.json",
    ]))
    working["ideal_evidence"] = list(dict.fromkeys(working.get("ideal_evidence", []) + [
        "aggregate_qualified_videos.json or qualified_video_links.txt",
        "aggregate_report.md",
        "video_details.json",
    ]))
    working["ready_checklist"] = list(dict.fromkeys(working.get("ready_checklist", []) + [
        "Top-ranked videos are clearly identified",
        "Transferable pattern is separated from profile-specific brand power",
    ]))

    payload["evidence"] = build_evidence(capture_root, aggregate_summary, profile_summary, ranked_videos)
    payload["assets"] = build_assets(capture_root)
    if ranked_videos:
        top_video = ranked_videos[0]
        play_addr = clean_text(top_video.get("play_addr"))
        download_addr = clean_text(top_video.get("download_addr"))
        cover_url = clean_text(top_video.get("cover_url"))
        if play_addr or download_addr:
            payload["evidence"].append(
                {
                "label": "可下载视频源",
                "detail": "该 capture pack 保留了可播放或可下载的视频细节，可继续用于逐帧复核。",
                    "source": download_addr or play_addr,
                }
            )
        if cover_url:
            payload["assets"].append(
                {
                    "label": "Cover / key frame source",
                    "path": cover_url,
                    "note": "Recovered cover image URL that can support frame review or first-frame comparison.",
                }
            )
    payload["sources"] = list(dict.fromkeys(payload.get("sources", []) + [
        format_source_reference(capture_root / ("aggregate_summary.json" if (capture_root / "aggregate_summary.json").exists() else "summary.json"), anchor=capture_root),
        format_source_reference(capture_root / ("aggregate_ranked_videos.json" if (capture_root / "aggregate_ranked_videos.json").exists() else "ranked_videos.json"), anchor=capture_root),
        clean_text(profile_summary.get("profile_url") or profile_summary.get("profile_final_url")),
    ]))
    if content_graph:
        payload["content_graph"] = {
            "version": content_graph.get("version"),
            "cluster_summary": content_graph.get("cluster_summary", {}),
            "edge_count": content_graph.get("edge_count", 0),
            "node_count": content_graph.get("node_count", 0),
        }
        summary = content_graph.get("cluster_summary") or {}
        payload["evidence"].append(
            {
                "label": "Content graph clusters",
                "detail": (
                    f"creator={summary.get('creator_clusters', 0)}; "
                    f"sound={summary.get('sound_clusters', 0)}; "
                    f"hashtag={summary.get('hashtag_neighborhoods', 0)}; "
                    f"videos={summary.get('video_count', 0)}"
                ),
                "source": format_source_reference(capture_root / "content_graph.json", anchor=capture_root),
            }
        )
    execution_template = payload.get("execution_template", {}) or {}
    if contains_dirty_zh_markers(execution_template.get("recommended_request_zh")):
        execution_template["recommended_request_zh"] = ""
    prompt_scaffold_zh = execution_template.get("codex_prompt_scaffold_zh") or []
    if any(contains_dirty_zh_markers(item) for item in prompt_scaffold_zh):
        execution_template["codex_prompt_scaffold_zh"] = []


def fill_scene_03(payload: dict, ranked_videos: list[dict], qualified_videos: list[dict], aggregate_summary: dict, capture_root: Path | None = None) -> None:
    from content_graph import shortlist_provenance_cell

    sections = {section["heading"]: section for section in payload["sections"]}
    scene03_candidates = load_scene03_runtime_candidates(capture_root) if capture_root else []
    candidate_pool = scene03_candidates or qualified_videos or ranked_videos
    top_ranked = strongest_scene03_candidates(candidate_pool, limit=3)
    shortlist_rule = scene03_shortlist_rule_from_summary(aggregate_summary, candidate_pool)
    winner = top_ranked[0] if top_ranked else {}
    winner_hook = hook_text(winner)
    winner_topic = core_topic_text(winner)
    winner_author = author_signal_text(winner)

    payload["executive_summary"]["conclusion"] = (
        "The strongest TikTok posts in this pack win by pairing a clear first-line hook with recognizable authority, cultural framing, or a featured-person premise that viewers understand immediately."
    )
    payload["executive_summary"]["why_it_matters"] = (
        "This pack is useful for studying which short caption, topic cue, and authority signal are actually portable into a new teardown and adaptation workflow."
    )
    payload["executive_summary"]["next_action"] = (
        "Take the top-ranked shortlist into deeper teardown now, assign each winner to one teardown lane, and replace the original account authority with owned proof or owned talent."
    )
    payload["executive_summary"]["confidence"] = "medium"

    sections["Executive Conclusion"]["paragraphs"] = [
        "这批 TikTok 爆款深拆现在已经更接近 Clipcat 文档里的平台闭环：先搜候选，再按带货与点赞规则缩成短名单，最后直接进入逐条深拆。",
        f"候选池规模：{len(candidate_pool)} | 达标视频数：{aggregate_summary.get('aggregated_qualified_count', 0)}",
        f"短名单规则：{shortlist_rule}",
        f"头部样本主题：{winner_topic or '源包未恢复主题文本'}",
        f"头部样本钩子：{winner_hook or '源包未恢复钩子文本'}",
    ]
    sections["Executive Conclusion"]["bullets"] = [
        f"头部样本权威信号：{winner_author or '权威信号偏弱或未恢复'}",
        "头部样本应该拆它的钩子、证明链和权威替代逻辑，而不是照搬字面外壳。",
    ]
    if scene03_candidates:
        sections["Executive Conclusion"]["bullets"].append(
            f"已检测到 Scene 02 巡检交接：当前有 {len(scene03_candidates)} 条候选正按巡检优先级进入深拆。"
        )

    shortlist_rows = []
    for index, video in enumerate(top_ranked, start=1):
        shortlist_rows.append(
            [
                clean_text(video.get("shortlist_priority")) or f"P{index}",
                clean_text(video.get("video_url")),
                sentence_clip(hook_text(video), limit=100) or "钩子文本缺失",
                proof_style_text(video),
                f"{ranked_metric_summary(video)} | 商业置信度={safe_int(video.get('commerce_confidence'))} | 购物车信号={clean_text(video.get('tkshop_signal')) or '未检测到'}",
                shortlist_provenance_cell(video),
                clean_text(video.get("scene03_reason")) or f"{why_selected_text(video)}；交接方向：{teardown_lane_label(video)}",
                clean_text(video.get("shortlist_decision")) or "立即深拆",
            ]
        )
    sections["Structure Logic"]["table"]["rows"] = shortlist_rows
    if sections["Structure Logic"]["table"].get("headers"):
        headers = list(sections["Structure Logic"]["table"]["headers"])
        if len(headers) == 7:
            headers.insert(5, "入选溯源")
            sections["Structure Logic"]["table"]["headers"] = headers

    per_video_rows = []
    for video in top_ranked:
        script_full = sentence_clip(clean_text(video.get("caption_text") or video.get("desc") or video.get("core_topic")), limit=180) or "完整 caption / 脚本文本缺失"
        timeline_line = (
            f"00:00-00:03 {sentence_clip(hook_text(video), limit=52) or '开头钩子'} | "
            f"00:03-00:08 {sentence_clip(core_topic_text(video), limit=44) or '主题铺垫'} | "
            f"00:08-00:14 {proof_style_text(video)} | "
            f"00:14-00:20 软收口延续"
        )
        per_video_rows.append(
            [
                clean_text(video.get("video_url") or video.get("video_id")),
                sentence_clip(hook_text(video), limit=80) or "钩子文本缺失",
                script_full,
                timeline_line,
                author_signal_text(video) or "权威信号偏弱",
                hashtags_text(video) or "软收口 CTA 或当前未恢复明确 CTA",
                teardown_action_text(video),
            ]
        )
    sections["Core Mechanism"]["table"]["rows"] = per_video_rows
    sections["Core Mechanism"]["paragraphs"] = [
        "逐条深拆必须同时保留 4 块：脚本全文 / 关键句、时间轴节奏、证明装置、最终可执行创作建议。",
        "如果 caption 或脚本证据仍偏薄，这一行就该被标记为弱样本，而不是直接升格成共性规律。",
    ]
    sections["Core Mechanism"]["bullets"] = [
        "时间轴默认按 4 段展开：开头钩子 / 主题铺垫 / 证明段 / 软收口。",
        "脚本文本不够时，也要尽量保留当前能恢复出的完整 caption 或主题线索，别只剩一句抽象总结。",
        "后续创作建议必须对应到时间轴，而不是只给泛化结论。",
    ]

    sections["Reusable Formula"]["table"]["rows"] = scene03_reusable_formula_rows(top_ranked)
    sections["Reusable Formula"]["paragraphs"] = [
        "共性规律不是单条视频摘要，而是把多个 shortlisted 视频里反复出现的开头、证明和收口组织方式抽出来。",
        "最终写法要能直接指导新脚本，不是只适合做研究备忘录。",
    ]

    sections["Risks And Adaptation Notes"]["table"]["rows"] = scene03_risk_rows(top_ranked)
    sections["Risks And Adaptation Notes"]["bullets"] = [
        "认证账号或大号势能可能抬高表现，必须和可迁移的包装逻辑拆开看。",
        "这份采集包缺评论样本，所以人群语言相关结论只能弱持有。",
        "如果某条候选缺 caption 文本，这一行就应视为深拆证据更弱的样本。",
    ]
    sections["Next Action"]["table"]["rows"] = scene03_next_action_rows(top_ranked)
    sections["Next Action"]["numbered"] = [
        f"先把 {clean_text(top_ranked[0].get('video_url')) if top_ranked else '头部样本'} 做成主控深拆样本，完整补齐脚本、时间轴和证明链。",
        "第二条作为备选 hook / 主题对照线，避免团队只围着单一赢家过拟合。",
        "第三条保留为反例或低权威对照样本，验证这套包装离开账号势能后是否仍成立。",
    ]
    sections["Next Action"]["paragraphs"] = [
        "下一步不是重新搜更多视频，而是把当前 shortlist 的脚本全文、时间轴与证明段先拆完整，再进入改写与生产。",
    ]
    payload["notes"] = list(
        dict.fromkeys(
            payload.get("notes", [])
            + scene03_dispatch_memo(top_ranked, scene03_candidates)
        )
    )
    from scene_evidence_refs import attach_scene_03_evidence_refs

    attach_scene_03_evidence_refs(sections, top_ranked, winner)


def fill_scene_02(payload: dict, capture_root: Path, aggregate_summary: dict, ranked_videos: list[dict], qualified_videos: list[dict]) -> None:
    sections = {section["heading"]: section for section in payload["sections"]}
    snapshot, delta, alerts, scene03_candidates = load_scene02_runtime_files(capture_root)

    category = clean_text(snapshot.get("category") or aggregate_summary.get("category")) or "category pending"
    market = clean_text(snapshot.get("market") or aggregate_summary.get("market")) or "market pending"
    queries = snapshot.get("queries") or aggregate_summary.get("queries") or []
    topics = snapshot.get("topics") or aggregate_summary.get("topics") or []
    cadence = clean_text(snapshot.get("cadence") or aggregate_summary.get("cadence")) or "daily"
    tracked_videos = snapshot.get("tracked_videos") or []
    new_videos = delta.get("new_videos") or []
    breakout_videos = delta.get("breakout_videos") or []
    repeated_hooks = delta.get("repeated_hooks") or []
    missing_fields = snapshot.get("missing_fields") or []
    next_scene03 = scene03_candidates or qualified_videos[:3] or ranked_videos[:3]
    patrol_config = maybe_load(capture_root / "patrol_config.json")
    if not isinstance(patrol_config, dict):
        patrol_config = {}
    append_scope_key = clean_text(patrol_config.get("append_scope_key") or aggregate_summary.get("append_scope_key"))
    append_strategy = clean_text(patrol_config.get("append_strategy") or "append each run into the same board")
    rising_videos = delta.get("rising_videos") or []
    source_manifest = maybe_load(capture_root / "source_manifest.json")
    if not isinstance(source_manifest, list):
        source_manifest = []
    watchlist_rows = build_scene02_watchlist_rows(queries, topics, source_manifest)
    capture_date = clean_text(patrol_config.get("capture_date") or snapshot.get("snapshot_at") or aggregate_summary.get("started_at"))[:10]

    payload["executive_summary"]["conclusion"] = (
        "This Scene 02 pack now behaves like a real patrol loop: it tracks one TikTok category over time, compares the latest snapshot to the previous run, and flags which content changes deserve escalation."
    )
    payload["executive_summary"]["why_it_matters"] = (
        "The patrol is useful because it separates routine logging from actual operator triggers, so the next step is no longer vague monitoring but a ranked decision on what to deep-teardown next."
    )
    payload["executive_summary"]["next_action"] = (
        "Review the alert rows first, then send the strongest new or fast-rising videos into Scene 03 instead of re-tearing down the whole patrol pool."
    )
    payload["executive_summary"]["confidence"] = "medium"

    sections["Executive Conclusion"]["paragraphs"] = [
        "这份 Scene 02 已经不只是每天重搜一次关键词，而是更像同一张品类看板的持续追加与变化解释层。",
        f"Category: {category} | Market: {market} | Cadence: {cadence}",
        f"Append strategy: {append_strategy}",
        f"Tracked videos this cycle: {len(tracked_videos)} | New videos vs prior snapshot: {len(new_videos)} | Breakout videos: {len(breakout_videos)}",
    ]
    sections["Executive Conclusion"]["bullets"] = [
        f"Capture date: {capture_date or 'pending'}",
        f"Queries: {compact_join([clean_text(item) for item in queries]) or 'none'}",
        f"Topics: {compact_join([clean_text(item) for item in topics]) or 'none'}",
        f"Alert count this cycle: {len(alerts)} | Rising (sub-breakout): {len(rising_videos)}",
        f"Same-board key: {append_scope_key or 'not declared'}",
    ]

    object_rows: list[list[str]] = [
        ["Patrol date / snapshot time", "Pin each cycle to one comparable timepoint", "Prevents false trend reads caused by uneven sampling windows", "Daily"],
        ["Tracked query / topic", "Keep the keyword and hashtag entry points stable", "Makes repeated hook or creator changes comparable over time", "Daily"],
        ["Top video IDs / URLs", "Preserve the exact posts currently leading the category", "Needed for Scene 03 escalation and later rerank checks", "Daily"],
        ["Metric deltas", "Track likes, comments, shares, plays, and score movement", "Separates steady incumbents from breakout movers", "Daily"],
        ["Repeated hooks / packaging", "Record hook text or caption patterns repeated across accounts", "Signals category convergence and clone pressure", "Daily"],
        ["Creator / authority shift", "Track whether breakout posts depend on verified or niche authority", "Helps separate portable format from account advantage", "Weekly"],
    ]
    sections["Objects To Track"]["table"]["rows"] = object_rows
    if watchlist_rows:
        sections["Objects To Track"]["bullets"] = [
            "多关键词 / 多话题看板：同一 append_scope_key 下持续追加，不另起一张表。",
            *[f"{row[0]}={row[1]} ({row[2]})" for row in watchlist_rows[:6]],
        ]

    tracked_sample_rows: list[list[str]] = []
    for entry in tracked_videos[:5]:
        tracked_sample_rows.append(
            [
                patrol_entry_label(entry),
                patrol_entry_url(entry) or clean_text(entry.get("video_id")),
                sentence_clip(
                    normalize_caption_candidate(entry.get("hook_text") or entry.get("summary") or entry.get("core_topic")),
                    limit=88,
                )
                or "Hook/topic text missing",
                patrol_entry_metric_summary(entry) or "metrics unavailable",
            ]
        )
    change_digest_rows = scene02_change_digest_rows(
        alerts,
        new_videos,
        breakout_videos,
        repeated_hooks,
        next_scene03,
        rising_videos,
    )
    if tracked_sample_rows:
        sections["Why They Matter"]["paragraphs"] = [
            "先看今日新增 / 今日上升 / 今日异常，再用下表抽样确认这轮巡检到底监控到了什么。"
        ]
        sections["Why They Matter"]["table"]["title"] = "Change-First Patrol Digest"
        sections["Why They Matter"]["table"]["headers"] = ["今日信号", "发生了什么", "为什么值得看", "是否升级 Scene 03"]
        sections["Why They Matter"]["table"]["rows"] = change_digest_rows
        sections["Why They Matter"]["bullets"] = [
            "Tracked sample rows stay in notes / dispatch context; the main operator view should prioritize change over inventory.",
            "If no strong delta exists, keep the standing queue stable instead of widening search scope.",
        ]

    alert_rows = build_scene02_alert_rows(alerts, repeated_hooks, next_scene03, tracked_videos)

    capture_rows: list[list[str]] = []
    for field in missing_fields[:8]:
        capture_rows.append(
            [
                clean_text(field.get("field") or field),
                clean_text(field.get("why") or "This field improves later ranking or teardown quality"),
                clean_text(field.get("required") or "Yes"),
            ]
        )
    if not capture_rows:
        capture_rows = [
            ["Caption / hook text", "Preserve packaging language for later Scene 03 teardown quality", "Yes"],
            ["Author signal", "Separate account authority from portable content logic", "Yes"],
            ["Hashtags / topic tags", "Track repeated packaging and cluster emergence", "Yes"],
            ["First-seen timestamp", "Know whether a post is genuinely new in the category", "Yes"],
            ["Download metadata path", "Enable deeper enrichment on shortlisted videos", "Optional but recommended"],
        ]
    sections["Capture Gaps Next Round"]["paragraphs"] = [
        "Use the alert logic below to decide whether the patrol should escalate into teardown, stay in watch mode, or request better enrichment on the next cycle.",
        f"Current enrichment backlog: {compact_join([clean_text(row[0]) for row in capture_rows[:4]]) or 'none'}",
    ]
    sections["Capture Gaps Next Round"]["bullets"] = [
        "Keep alert thresholds stable across runs so comparisons stay meaningful.",
        "Treat missing enrichment as an operator backlog, not as a reason to skip the patrol handoff.",
        "同一类别 / 地区 / 频率必须持续追加到同一逻辑主表，而不是每次另起一张表。",
    ]
    sections["Capture Gaps Next Round"]["table"]["title"] = "Alert Logic"
    sections["Capture Gaps Next Round"]["table"]["headers"] = ["Priority", "Signal", "What It Might Mean", "Follow-up Action"]
    sections["Capture Gaps Next Round"]["table"]["rows"] = alert_rows

    next_action_numbered = [
        "Run the patrol on the same cadence and compare to the previous snapshot before drawing conclusions.",
        "Escalate only the rows that triggered a real alert or showed strong breakout movement.",
        "Send the top Scene 03 candidates below into the deep-teardown path instead of reprocessing the full patrol pool.",
    ]
    sections["Next Action"]["numbered"] = next_action_numbered

    summary_rows: list[list[str]] = [
        ["Which board to append", append_scope_key or f"{category}::{market}::{cadence}"],
        ["What changed", clean_text(delta.get("summary_change")) or f"{len(new_videos)} new videos and {len(breakout_videos)} breakout videos detected"],
        ["What broke out", clean_text(delta.get("summary_breakout")) or compact_join([clean_text(item.get("video_id") or item.get("video_url")) for item in breakout_videos[:3]]) or "No breakout video crossed threshold"],
        ["What needs deeper teardown", compact_join([clean_text(item.get('video_url') or item.get('video_id')) for item in next_scene03[:3]]) or "Choose the top-ranked new or breakout video"],
        ["What to watch tomorrow", clean_text(delta.get("watch_tomorrow")) or "Watch for repeated hooks, creator re-entries, and score acceleration"],
    ]
    sections["Next Action"]["table"]["rows"] = summary_rows
    sections["Next Action"]["paragraphs"] = [
        "Use the daily summary block below as the operator note, then hand the prioritized Scene 03 queue to teardown instead of reopening the whole patrol board."
    ]
    sections["Next Action"]["bullets"] = [
        "No breakout does not mean no action; it means operate from the standing queue and data-quality backlog.",
        "The handoff should always name one top Scene 03 control plus one or two contrast references."
    ]
    payload["notes"] = list(
        dict.fromkeys(
            payload.get("notes", [])
            + scene02_dispatch_memo(next_scene03, capture_rows)
            + [
                "The schema table defines what the patrol should watch every cycle; the tracked sample rows are only a sanity-check view of the current run.",
            ]
        )
    )

    working = payload["working_context"]
    working["constraints"] = list(
        dict.fromkeys(
            working.get("constraints", [])
            + [
                "This Scene 02 report is generated from a persisted patrol snapshot and delta, not from one isolated ranked list.",
                "If no previous snapshot exists, treat this run as the baseline and hold delta conclusions lightly.",
                "Rows from the same category / market / cadence should append into one continuing board with stable headers.",
            ]
        )
    )
    working["requested_outputs"] = list(
        dict.fromkeys(
            working.get("requested_outputs", [])
            + [
                "Snapshot delta interpretation",
                "Scene 03 escalation shortlist",
            ]
        )
    )
    if "Why They Matter" in sections:
        sections["Why They Matter"]["table"]["title"] = "Tracked Sample Rows"
    sections["Next Action"]["table"]["title"] = "Reusable Daily Summary Template"
    escalation_rows = build_scene02_escalation_rows(next_scene03)
    sections["Why They Matter"]["bullets"] = list(
        dict.fromkeys(
            (sections["Why They Matter"].get("bullets") or [])
            + [
                "Dispatch queue preview:",
                *[f"{row[0]} {row[1]} -> {row[2]} ({row[3]})" for row in escalation_rows],
                *(
                    [
                        "Tracked sample rows:",
                        *[
                            f"{row[0]} | {row[1]} | {row[2]} | {row[3]}"
                            for row in tracked_sample_rows[:3]
                        ],
                    ]
                    if tracked_sample_rows
                    else []
                ),
            ]
        )
    )


def fill_scene_17(payload: dict, ranked_videos: list[dict], profile_summary: dict) -> None:
    sections = {section["heading"]: section for section in payload["sections"]}
    top_ranked = top_videos(ranked_videos, limit=4)
    high_video = top_ranked[0] if top_ranked else {}
    low_video = top_ranked[-1] if len(top_ranked) > 1 else high_video
    average_views = int(sum(safe_int(video.get("play_count")) for video in top_ranked) / max(len(top_ranked), 1)) if top_ranked else 0
    average_likes = int(sum(safe_int(video.get("digg_count")) for video in top_ranked) / max(len(top_ranked), 1)) if top_ranked else 0
    average_comments = int(sum(safe_int(video.get("comment_count")) for video in top_ranked) / max(len(top_ranked), 1)) if top_ranked else 0
    average_shares = int(sum(safe_int(video.get("share_count")) for video in top_ranked) / max(len(top_ranked), 1)) if top_ranked else 0

    payload["executive_summary"]["conclusion"] = (
        "这组 TikTok 账号样本显示出一套可重复的编辑型公式：先把内容挂到可识别的创作者、故事或文化瞬间上，再用极少文案让亲和感自行发挥作用。"
    )
    payload["executive_summary"]["why_it_matters"] = (
        "这种模式适合需要更强社交原生包装、但又不想靠长解释开头的 TikTok 项目。"
    )
    payload["executive_summary"]["next_action"] = (
        "把这个账号最强的编辑型包装动作，翻译成可复用的创作者型或社群型内容制作简报。"
    )
    payload["executive_summary"]["confidence"] = "medium"

    sections["Executive Conclusion"]["paragraphs"] = [
        payload["executive_summary"]["conclusion"],
        f"账号会话质量：{clean_text(profile_summary.get('session_quality'))}",
    ]
    sections["Executive Conclusion"]["bullets"] = [
        f"头部钩子线索：{hook_text(high_video) or '缺失'}",
        f"低表现对照线索：{hook_text(low_video) or '缺失'}",
        f"主要创作者赛道：{creator_positioning_text(high_video)}",
        f"高互动 vs 低互动：{scene04_video_type(high_video)} 对比 {scene04_video_type(low_video)}",
    ]

    rows = [
        ["一句话定位", creator_positioning_text(high_video) or "创作者 / 编辑型账号正在用识别优先的社交包装取胜", clean_text(profile_summary.get("profile_url") or profile_summary.get("profile_final_url"))],
        ["平均播放", str(average_views), clean_text(high_video.get("video_url")) if high_video else ""],
        ["平均点赞", str(average_likes), clean_text(high_video.get("video_url")) if high_video else ""],
        ["平均评论", str(average_comments), clean_text(high_video.get("video_url")) if high_video else ""],
        ["平均分享", str(average_shares), clean_text(high_video.get("video_url")) if high_video else ""],
        ["爆款率", creator_breakout_rate_text(top_ranked, average_likes), "仅基于当前样本的估算"],
        ["更新频率", scene17_update_frequency_text(top_ranked), "基于当前样本时间点推断"],
        ["强势发布时间", scene17_best_publish_window_text(top_ranked), "样本窗口推断，不等于最终定论"],
    ]
    sections["Structure Logic"]["table"]["rows"] = rows
    sections["Structure Logic"]["table"]["headers"] = ["账号速览字段", "结论", "证据 / 说明"]

    sections["Core Mechanism"]["table"]["headers"] = ["比较维度", "高互动样本", "低互动样本", "操作解释"]
    sections["Core Mechanism"]["table"]["rows"] = scene17_high_low_compare_rows(high_video, low_video)
    sections["Core Mechanism"]["paragraphs"] = [
        "这份蒸馏报告必须把高互动和低互动样本拉成反例对照，而不是只总结爆款共性。",
        "先做账号速览，再做高低互动对比，最后才提炼公式，否则会把账号壳子误当成可迁移打法。",
    ]

    sections["Reusable Formula"]["table"]["title"] = "创作者公式库"
    sections["Reusable Formula"]["table"]["headers"] = ["公式", "原始钩子 / 证据", "可套用模板", "强势发布时间", "来源"]
    sections["Reusable Formula"]["table"]["rows"] = scene17_formula_library_rows(top_ranked)

    sections["Risks And Adaptation Notes"]["table"]["rows"] = [
        ["钩子公式", hook_text(high_video) if high_video else "识别优先钩子待补", "先给一个一眼可懂的人物、瞬间或文化线索", "更适合受众本就认识这条线索的场景"],
        ["钩子公式", hook_text(top_ranked[1]) if len(top_ranked) > 1 else "情绪优先 caption 包装待补", "先给情绪清晰度，再进入解释", "更适合证明能在情绪线索后快速到位的场景"],
        ["节奏模型", "快速铺垫 -> 一次证明节拍 -> 轻量延续", "压缩铺垫，避免长 exposition", "更适合短平快的社交原生帖子"],
        ["CTA 公式", "延续式 CTA 优先于硬卖", "把动作导向继续看、收藏或关注", "更适合以发现和扩散为主目标的内容"],
    ]
    sections["Visual And Distribution Signature"]["table"]["rows"] = [
        ["视觉风格", "偏编辑感、识别优先的社交原生包装", "让用户更快读懂内容前提，缩短刷到后做决定的时间", clean_text(high_video.get("video_url")) if high_video else ""],
        ["BGM / 音频", music_style_text(high_video), "音频更像包装 cue，而不是复杂叙事层", clean_text(high_video.get("video_url")) if high_video else ""],
        ["Hashtag 习惯", hashtags_text(high_video) or "样本里可见 hashtag 较轻", "这类账号更依赖 hook 包装，而不是 hashtag 堆砌", clean_text(high_video.get("video_url")) if high_video else ""],
        ["发布时间", "需要多周采样后再下结论", "样本薄时不要把偶发时间窗误判成稳定分发公式", clean_text(profile_summary.get("profile_url") or profile_summary.get("profile_final_url"))],
    ]
    sections["Next Action"]["table"]["rows"] = [
        ["新钩子草案", hook_text(high_video) or "识别优先的开头公式", "任何只适用于官方账号的 lift 或品牌权威外壳", "小账号需要更强的自有证明"],
        ["脚本节奏", "快速铺垫 -> 证明 -> 延续", "过度解释式开头", "核心前提必须在前几秒落地"],
        ["证明格式", proof_style_text(high_video), "无法证明的权威借用", "证明太弱会拉平整套公式"],
        ["发布实验", "测试创作者驱动版与证明物驱动版", "假设同一赛道适用于所有账号体量", "需要干净的 A/B 设置"],
    ]
    from scene_evidence_refs import attach_scene_17_evidence_refs

    attach_scene_17_evidence_refs(sections, top_ranked, high_video, low_video, profile_summary)


def fill_scene_08(payload: dict, capture_root: Path, ranked_videos: list[dict]) -> None:
    sections = {section["heading"]: section for section in payload["sections"]}
    comment_pack = load_comment_pack(capture_root)
    comment_entries = comment_pack["cleaned"]
    reply_chains = comment_pack["reply_chains"]
    comment_clusters = summarize_comment_clusters(comment_entries)
    reply_patterns = summarize_reply_patterns(comment_entries)
    snapshot = comment_pack["snapshot"]
    sampled_video_count = len({entry["video_id"] for entry in comment_entries if entry["video_id"]})
    top_texts = [clean_text(entry.get("quote_text") or entry.get("text")) for entry in comment_entries if clean_text(entry.get("quote_text") or entry.get("text"))][:6]
    price_sensitive = next((cluster for cluster in comment_clusters if "price" in clean_text(cluster.get("theme")).lower()), None)
    top_purchase = snapshot.get("top_purchase_cluster")
    top_complaint = snapshot.get("top_complaint_cluster")
    top_trust = snapshot.get("top_trust_cluster")
    top_reply = snapshot.get("top_reply_pattern")

    payload["executive_summary"]["conclusion"] = (
        "这份 TikTok 评论包里最强的重复用户语言，已经能更清楚地归到购买因素、信任信号和差评痛点三类，并且能用回复链压力把浅层热闹和真实异议处理区分开。"
    )
    payload["executive_summary"]["why_it_matters"] = (
        "这很重要，因为操作者拿到的不再是一堆平铺评论，而是更干净的买家语言聚类、来源商品标签、去重后的高频原话和回复链线索。"
    )
    payload["executive_summary"]["next_action"] = (
        "在下一轮测试前，先用这些已清洗的差评痛点和信任信号去写评论回复、FAQ 文案和定位话术。"
    )
    payload["executive_summary"]["confidence"] = "medium"

    sections["Executive Conclusion"]["paragraphs"] = [
        payload["executive_summary"]["conclusion"],
        f"这次共从 {sampled_video_count} 条 TikTok 视频中采到了评论样本。",
    ]

    sections["High-Level Judgment"]["paragraphs"] = [
        "核心教训是：一旦把低信号表情噪音、病毒式重复留言和浅层互动诱饵清理掉，真正重复出现的买家语言就会更可执行。"
    ]
    sections["High-Level Judgment"]["table"]["rows"] = build_scene08_source_product_rows(comment_entries)
    stats = comment_pack.get("stats") or {}
    sections["High-Level Judgment"]["bullets"] = [
        f"原始评论={stats.get('raw_count', len(comment_entries))} | 清洗后={snapshot.get('cleaned_count', len(comment_entries))} | 过滤噪音={stats.get('rejected_count', 0)}",
        f"最强购买因素：{clean_text((top_purchase or {}).get('theme')) or '未恢复出明确购买因素'}",
        f"最强差评痛点簇：{clean_text((top_complaint or {}).get('theme')) or '未恢复出明确差评痛点'}",
        f"最有价值的回复链簇：{scene08_reply_chain_line(snapshot.get('top_reply_chain') or top_reply)}",
        f"价格带信号：{clean_text(price_sensitive['theme']) if price_sensitive else '未恢复出强价格带分层'}",
        f"回复链合成条数：{stats.get('reply_chain_count', len(reply_chains))}",
    ]

    sections["Evidence Clusters"]["table"]["rows"] = build_comment_cluster_rows(comment_entries)
    sections["Evidence Clusters"]["paragraphs"] = [
        "主报告优先贴近四段式：购买因素、好评关键词、差评痛点、价位差异。",
        "每个聚类都尽量保留来源商品、重复原话、回复链压力和价格带线索，方便直接翻译成 FAQ、评论回复和卖点脚本。",
    ]
    sections["Evidence Clusters"]["bullets"] = [
        "回复链综合（顶层评论 + 追问回复已分开清洗）：",
        *[
            f"{row[0]} | 回复压力={row[1]} | 来源={row[2]} | {row[4]}"
            for row in scene08_reply_chain_synthesis(reply_chains or reply_patterns)
        ],
    ]

    sections["Recommended Action"]["table"]["rows"] = [
        [
            "购买因素",
            "先围绕最强购买触发点写卖点与证明，不要先写品牌自夸。",
            scene08_cluster_note(top_purchase, "当前仍需更强购买触发语料。"),
            "品类基础价值",
        ],
        [
            "好评关键词",
            "把重复出现的正向原话翻成标题、口播和评论区 FAQ 的基础词库。",
            scene08_cluster_note(top_trust or top_reply, "回复链已经说明：用户会先做质疑、确认或信任校验。"),
            "品类基础价值",
        ],
        [
            "差评痛点",
            "把物流、包装、真假、退货、尺寸或 before-after 证据不足单独前置，不要藏到后面。",
            scene08_cluster_note(top_complaint, "这批样本里还没有稳定成形的强差评痛点簇。"),
            "改进机会",
        ],
        [
            "价位差异",
            "不同价位段需要不同的价值证明和风险安抚，不要用一套脚本打全部价格带。",
            clean_text(price_sensitive["theme"]) if price_sensitive else "当前价格带分层仍偏弱，需要继续补样本。",
            "改进机会",
        ],
    ]

    sections["Open Questions"]["table"]["rows"] = build_scene08_price_band_rows(comment_entries)
    sections["Open Questions"]["bullets"] = [
        "当前采样评论只覆盖了部分来源视频，所以这些结论更适合作为方向判断，而不是完整品类定论。",
        "回复链结论目前主要来自导出的回复数量与摘要，不是完整的原始 threaded reply 全量抓取。",
        f"当前最值得追加全量抓取的回复链主题：{clean_text((top_reply or {}).get('theme')) or '未恢复'}。",
    ]

    payload["notes"] = list(
        dict.fromkeys(
            payload.get("notes", [])
            + top_texts
            + [scene08_reply_chain_line(top_reply)]
        )
    )
    from scene_evidence_refs import attach_scene_08_evidence_refs

    attach_scene_08_evidence_refs(
        sections,
        comment_entries,
        snapshot,
        top_purchase if isinstance(top_purchase, dict) else None,
        top_complaint if isinstance(top_complaint, dict) else None,
        top_reply if isinstance(top_reply, dict) else None,
        top_trust if isinstance(top_trust, dict) else None,
        snapshot.get("top_reply_chain") if isinstance(snapshot, dict) else None,
    )


def fill_scene_18(payload: dict, capture_root: Path, ranked_videos: list[dict], profile_summary: dict) -> None:
    from content_graph import shortlist_provenance_cell

    sections = {section["heading"]: section for section in payload["sections"]}
    top_ranked = top_videos(ranked_videos, limit=3)
    profile_url = clean_text(profile_summary.get("profile_url") or profile_summary.get("profile_final_url"))
    comment_pack = load_comment_pack(capture_root) if capture_root else {"cleaned": [], "reply_chains": [], "snapshot": {}}
    comment_snapshot = comment_pack["snapshot"]
    compare = compare_latest_two_weeks(ranked_videos)
    coverage = weekly_coverage_summary(ranked_videos, profile_summary, comment_snapshot)
    evidence_grade = weekly_evidence_grade(coverage)
    multi_week_rows = multi_week_pattern_rows(ranked_videos)
    matrix_mode = safe_int(coverage.get("account_count")) >= 2
    account_label = profile_url or "TikTok account"
    top_reply_chain = comment_snapshot.get("top_reply_chain")

    if matrix_mode and compare.get("mode") == "compare":
        payload["executive_summary"]["conclusion"] = (
            "这份竞品账号周报现在已经进入多账号、多周矩阵视角，所以不再只是看一个账号的单周榜单，而是能比较不同竞对这周到底谁在变、怎么变。"
        )
        payload["executive_summary"]["why_it_matters"] = (
            "这样可以把单账号偶发爆点和矩阵级策略变化分开，也更容易识别哪些包装线正在跨账号复现。"
        )
        payload["executive_summary"]["next_action"] = (
            "优先追那些在本周显著冒头、且不完全依赖账号权威壳的包装线；弱变化和事件型噪音先放到观察区。"
        )
    elif compare.get("mode") == "compare":
        payload["executive_summary"]["conclusion"] = (
            "这份竞品账号周报现在已经能对比最近两周，所以不再只是看单周榜单，而是能判断策略是否真的发生了变化。"
        )
        payload["executive_summary"]["why_it_matters"] = (
            "有了两周切片后，可以把稳定连胜的包装方式和短期噪音分开，也更容易识别竞对本周到底改了什么。"
        )
        payload["executive_summary"]["next_action"] = (
            "直接按下方周环比变化去做本周动作分发：哪些线继续追，哪些线可以借鉴，哪些异常峰值先忽略。"
        )
    else:
        payload["executive_summary"]["conclusion"] = (
            "这份 TikTok 采集包已经建立了可用的竞品账号周基线：当前胜出的主要是少量包装明显、情绪或文化识别很强的内容。"
        )
        payload["executive_summary"]["why_it_matters"] = (
            "即使只有一周基线，也足够先判断哪些包装线值得持续追踪，哪些只是账号噪音。"
        )
        payload["executive_summary"]["next_action"] = (
            "先把这批作为周基线保留，下周按同字段复采，就能快速识别包装或表现是否出现漂移。"
        )
    payload["executive_summary"]["confidence"] = "medium"

    sections["Executive Conclusion"]["paragraphs"] = [
        payload["executive_summary"]["conclusion"],
        f"{'竞品矩阵' if matrix_mode else '账号基线'}：{profile_url or (str(safe_int(coverage.get('account_count'))) + ' 个账号样本')}",
        f"证据等级：{evidence_grade}（{weekly_evidence_note(coverage)}）",
        (
            f"比较窗口：{clean_text(compare.get('latest_week'))} vs {clean_text(compare.get('prior_week'))}"
            if compare.get("mode") == "compare"
            else f"比较窗口：{clean_text(compare.get('latest_week')) or '仅当前周'}"
        ),
    ]
    sections["Executive Conclusion"]["bullets"] = [
        f"本周最强包装线：{teardown_lane_label(top_ranked[0]) if top_ranked else '未恢复'}",
        f"爆点帖子关键信号：{display_cue_text(top_ranked[0], limit=88, fallback=top_ranked[0].get('desc')) if top_ranked else '缺失'}",
        f"评论侧信任 / 质疑线索：{scene08_reply_chain_line(top_reply_chain or comment_snapshot.get('top_reply_pattern')) or '本包暂无评论采样'}",
        "如果还没有上周对照，就把本次视为基线周报；若账号数不足，也不要包装成完整矩阵级结论。",
    ]
    if top_ranked:
        sections["Executive Conclusion"]["bullets"].append(
            f"头部样本入选溯源：{shortlist_provenance_cell(top_ranked[0])}"
        )
    if top_reply_chain:
        sections["Executive Conclusion"]["bullets"].append(
            f"评论回复链信号：{scene08_reply_chain_line(top_reply_chain)}"
        )

    sections["Objects To Track"]["table"]["rows"] = (
        scene18_matrix_summary_rows(ranked_videos)[:5]
        if matrix_mode
        else weekly_account_summary_rows(ranked_videos, label=account_label)[:4]
    ) or [[account_label, "week unknown", str(len(ranked_videos)), "", "", "", ""]]
    sections["Objects To Track"]["bullets"] = [
        f"自然周覆盖：{safe_int(coverage.get('week_count'))} 周；帖子数：{safe_int(coverage.get('post_count'))}；账号数：{safe_int(coverage.get('account_count'))}。",
        "先看哪一周在重复赢、哪一周只是新冒头，再决定是否判定为策略变化；矩阵模式下还要看这种变化有没有跨账号扩散。",
    ]

    shift_rows = scene18_matrix_shift_rows(ranked_videos) if matrix_mode else weekly_shift_rows(ranked_videos)
    why_rows = shift_rows[:3]
    if not matrix_mode:
        why_rows.extend(scene18_multi_week_focus_rows(ranked_videos))
    sections["Why They Matter"]["table"]["rows"] = why_rows
    sections["Why They Matter"]["paragraphs"] = [
        "这一块不只是周报报数，而是要解释谁在发力、谁在回落、谁只是事件噪音。"
    ]
    sections["Why They Matter"]["bullets"] = [
        "优先解释策略变化，再解释单条爆点；不要把偶发爆点误写成全账号升级。",
        "横向对比要回答两个问题：是谁变了；这种变化有没有跨账号扩散。",
    ]
    if comment_snapshot:
        sections["Why They Matter"]["table"]["rows"].append(
            [
                "评论语言压力",
                clean_text((comment_snapshot.get("top_reply_pattern") or {}).get("theme")) or "未恢复出强 reply 聚类",
                "回复密集的评论簇能帮助区分：这是健康兴趣，还是争议 / 困惑驱动的放大。",
                clean_text((comment_snapshot.get("top_reply_pattern") or {}).get("top_entry", {}).get("reply_signal")) or "下轮需要继续补评论采样",
                "用它来判断本周高表现到底是在积累信任，还是只是在放大摩擦。",
            ]
        )

    sections["Fields To Capture Next Time"]["bullets"] = [
        "继续补同账号第二周、第三周切片；如果是竞品矩阵，还要保证每个账号都按同字段持续复采。",
        "每条帖子补评论采样可用性和出镜人 / 权威标签。",
        "如果账号改了封面、首帧或标题包装，要保留证据，不要只留 caption。",
    ]
    sections["Fields To Capture Next Time"]["table"]["title"] = "下轮补采升级"
    sections["Fields To Capture Next Time"]["table"]["headers"] = ["待补字段", "为什么重要", "优先级"]
    sections["Fields To Capture Next Time"]["table"]["rows"] = [
        ["第二周快照", "没有第二周，就无法把长期有效包装和单周噪音分开。", "P1"],
        ["多账号并排采样", "没有 3-5 个账号并排，就很难判断这是不是矩阵级变化。", "P1" if matrix_mode else "P2"],
        ["评论采样标记", "帮助判断高表现是在积累信任，还是在放大质疑 / 困惑。", "P1"],
        ["出镜人 / 权威标签", "把包装胜利和名人、官方身份加成拆开。", "P1"],
        ["封面 / 首帧证据", "让下一轮比较不只看 caption，还能看点击包装有没有变。", "P2"],
    ]

    sections["Next Action"]["table"]["rows"] = (
        scene18_matrix_dispatch_rows(ranked_videos, comment_snapshot)
        if matrix_mode
        else scene18_dispatch_rows(compare, top_ranked, comment_snapshot)
    )
    sections["Next Action"]["paragraphs"] = [
        "本周响应动作必须更像运营调度单：继续追谁、借鉴谁、忽略谁，都要回到策略变化而不是只回到热度高低。",
    ]
    from scene_evidence_refs import attach_scene_18_evidence_refs

    attach_scene_18_evidence_refs(sections, top_ranked, compare, profile_summary, comment_snapshot)


def fill_scene_19(payload: dict, capture_root: Path, ranked_videos: list[dict], profile_summary: dict) -> None:
    from content_graph import shortlist_provenance_cell

    sections = {section["heading"]: section for section in payload["sections"]}
    ordered_ranked = sorted(
        ranked_videos,
        key=lambda item: (safe_int(item.get("score")), safe_int(item.get("digg_count")), safe_int(item.get("comment_count"))),
        reverse=True,
    )
    top_ranked = top_videos(ordered_ranked, limit=4)
    high_video = ordered_ranked[0] if ordered_ranked else {}
    low_video = ordered_ranked[-1] if len(ordered_ranked) > 1 else high_video
    comment_pack = load_comment_pack(capture_root) if capture_root else {"cleaned": [], "reply_chains": [], "snapshot": {}}
    comment_snapshot = comment_pack["snapshot"]
    top_reply_chain = comment_snapshot.get("top_reply_chain")
    compare = compare_latest_two_weeks(ranked_videos)
    coverage = weekly_coverage_summary(ranked_videos, profile_summary, comment_snapshot)
    evidence_grade = weekly_evidence_grade(coverage)
    multi_week_rows = multi_week_pattern_rows(ranked_videos)
    window_signal_rows = scene19_window_signal_rows(ordered_ranked)
    roi_cluster_rows = scene19_roi_cluster_rows(top_ranked or ordered_ranked)
    high_low_rows = scene19_high_low_signal_rows(high_video, low_video, multi_week_rows)
    publish_window_rows = scene19_best_publish_window_rows(ordered_ranked)

    if compare.get("mode") == "compare":
        payload["executive_summary"]["conclusion"] = (
            "这份账号复盘现在已有至少两周切片，而且不同发布时间窗口下的 ROI 信号与转化信号 proxy 已能直接上屏，所以不再只是看单周排序。"
        )
        payload["executive_summary"]["why_it_matters"] = (
            "这样可以把一次性爆点、时间窗红利和真正可重复的内容模式胜利拆开，进而更明确地给出多做、少做、停止和下轮测试建议。"
        )
        payload["executive_summary"]["next_action"] = (
            "直接用下方周对比、时间窗差异和高低表现分组，决定下轮测试周期该把流量和排期给哪种内容模式。"
        )
    else:
        payload["executive_summary"]["conclusion"] = (
            "在这批 TikTok 账号样本里，当前更可能跑出的模式是短、包装清晰、能立刻挂到人物 / 证明物 / 时刻感上的内容，而不是先做长解释。"
        )
        payload["executive_summary"]["why_it_matters"] = (
            "它的价值不只是复盘，而是把原始排序数据连同发布时间窗、转化信号 proxy 和 ROI 信号 proxy 一起转成下一轮的多做、少做和测试计划。"
        )
        payload["executive_summary"]["next_action"] = (
            "下一轮先围绕人物驱动、时刻驱动和解释驱动三类内容聚类测试，确认哪个包装家族值得拿更多量。"
        )
    payload["executive_summary"]["confidence"] = "medium"

    sections["Executive Conclusion"]["paragraphs"] = [
        payload["executive_summary"]["conclusion"],
        f"当前采样包内排序帖子数：{profile_summary.get('ranked_video_count', len(ranked_videos))}",
        f"证据等级：{evidence_grade}（{weekly_evidence_note(coverage)}）",
        (
            f"周对比：{clean_text(compare.get('latest_week'))} vs {clean_text(compare.get('prior_week'))}"
            if compare.get("mode") == "compare"
            else f"周对比：{clean_text(compare.get('latest_week')) or '仅当前周'} 基线"
        ),
    ]
    sections["Executive Conclusion"]["bullets"] = [
        f"高表现对照：{display_cue_text(high_video, limit=88, fallback=high_video.get('desc')) if high_video else '缺失'}",
        f"低表现对照：{display_cue_text(low_video, limit=88, fallback=low_video.get('desc')) if low_video else '缺失'}",
        f"高表现窗口 / 信号：{scene19_window_label(clean_text(high_video.get('publish_window')) or publish_week_label(high_video) or '未标记')} / {scene19_signal_label(high_video.get('conversion_proxy'))} / {scene19_signal_label(high_video.get('roi_proxy'))}",
        f"低表现窗口 / 信号：{scene19_window_label(clean_text(low_video.get('publish_window')) or publish_week_label(low_video) or '未标记')} / {scene19_signal_label(low_video.get('conversion_proxy'))} / {scene19_signal_label(low_video.get('roi_proxy'))}",
        f"当前最佳发布时间窗：{publish_window_rows[0][0] if publish_window_rows else '尚不足以判断'}",
        f"最强评论侧阻力 / 信任线索：{scene08_reply_chain_line(top_reply_chain or comment_snapshot.get('top_reply_pattern') or comment_snapshot.get('top_complaint_cluster')) or '本包暂无评论采样'}",
        "把这份复盘当成下轮调度单，不要只当被动总结；若当前只是外部样本包，请把它当模板，不要直接当自家账号最终判决。",
    ]
    if high_video:
        sections["Executive Conclusion"]["bullets"].append(
            f"高表现样本入选溯源：{shortlist_provenance_cell(high_video)}"
        )
    if top_reply_chain:
        sections["Executive Conclusion"]["bullets"].append(
            f"评论回复链合成：{scene08_reply_chain_line(top_reply_chain)}"
        )

    sections["High-Level Judgment"]["table"]["rows"] = high_low_rows
    if publish_window_rows:
        sections["High-Level Judgment"]["table"]["rows"].append(
            [
                "最佳发布时间窗",
                publish_window_rows[0][0],
                f"{publish_window_rows[0][1]}；{publish_window_rows[0][3]}",
                "下轮优先在这个窗口复测，再判断它是模式胜利还是时间红利。",
            ]
        )
    sections["High-Level Judgment"]["paragraphs"] = [
        "这张主表现在必须把最佳发布时间窗直接推成一条主结论，而不是埋在明细里。",
    ]

    sections["Evidence Clusters"]["table"]["rows"] = roi_cluster_rows[:3]
    for row in window_signal_rows[:2]:
        sections["Evidence Clusters"]["table"]["rows"].append(
            [
                f"时间窗：{row[0]}",
                row[1],
                row[2],
                row[3],
                row[4],
            ]
        )
    for row in multi_week_rows[:2]:
        sections["Evidence Clusters"]["table"]["rows"].append(
            [
                f"周趋势：{row[0]}",
                row[2],
                row[1],
                row[3],
                f"{row[4]}；{row[5]}",
            ]
        )
    if comment_snapshot:
        sections["Evidence Clusters"]["table"]["rows"].append(
            [
                "评论侧模式",
                clean_text((comment_snapshot.get("top_reply_pattern") or {}).get("theme")) or clean_text((comment_snapshot.get("top_purchase_cluster") or {}).get("theme")) or "未恢复出强评论模式",
                clean_text((comment_snapshot.get("top_reply_pattern") or {}).get("top_entry", {}).get("source_product")) or "评论采样",
                clean_text((comment_snapshot.get("top_reply_pattern") or {}).get("top_entry", {}).get("quote_text")) or clean_text((comment_snapshot.get("top_purchase_cluster") or {}).get("top_entry", {}).get("quote_text")) or "下一轮需要更丰富的评论样本",
                clean_text((comment_snapshot.get("top_reply_pattern") or {}).get("top_entry", {}).get("reply_signal")) or "用评论侧摩擦来判断：下一轮放大的内容模式是在积累兴趣，还是在放大困惑。",
            ]
        )

    sections["Recommended Action"]["table"]["rows"] = scene19_dispatch_rows(compare, high_video, low_video, comment_snapshot)
    if sections["Recommended Action"]["table"]["rows"]:
        sections["Recommended Action"]["table"]["rows"][0][2] = (
            f"{sections['Recommended Action']['table']['rows'][0][2]}；"
            f"主窗口={scene19_window_label(clean_text(high_video.get('publish_window')) or publish_week_label(high_video) or '未标记')}；"
            f"转化信号/ROI 信号={scene19_signal_label(high_video.get('conversion_proxy'))} / {scene19_signal_label(high_video.get('roi_proxy'))}"
        )
        if len(sections["Recommended Action"]["table"]["rows"]) > 1:
            sections["Recommended Action"]["table"]["rows"][1][2] = (
                f"{sections['Recommended Action']['table']['rows'][1][2]}；"
                f"低表现窗口={scene19_window_label(clean_text(low_video.get('publish_window')) or publish_week_label(low_video) or '未标记')}；"
                f"转化信号/ROI 信号={scene19_signal_label(low_video.get('conversion_proxy'))} / {scene19_signal_label(low_video.get('roi_proxy'))}"
            )

    sections["Open Questions"]["bullets"] = [
        "真正的自家账号复盘，至少要有两周以上、同字段、同发布时间窗的内部样本对照。",
        "当前如果仍是外部导入包，这份更适合作为模式模板，而不是直接替代自家账号的最终策略判断。",
        "如果下一轮还拿不到真实订单、点击或加购数据，就继续把转化信号 proxy / ROI 信号 proxy 当过渡层，而不是最终归因真相。",
    ]
    sections["Open Questions"]["table"]["title"] = "下轮测试计划"
    sections["Open Questions"]["table"]["headers"] = ["下轮测试", "假设", "具体改什么", "成功信号"]
    sections["Open Questions"]["table"]["rows"] = scene19_test_plan_rows(high_video, low_video)
    from scene_evidence_refs import attach_scene_19_evidence_refs

    attach_scene_19_evidence_refs(
        sections,
        high_video,
        low_video,
        compare,
        comment_snapshot,
        top_ranked,
    )


def fill_scene_01(payload: dict, ranked_videos: list[dict], aggregate_summary: dict, capture_root: Path) -> None:
    from content_graph import shortlist_provenance_cell

    sections = {section["heading"]: section for section in payload["sections"]}
    top_ranked = top_videos(ranked_videos, limit=5)
    top_hook = hook_text(top_ranked[0]) if top_ranked else ""
    top_topic = core_topic_text(top_ranked[0]) if top_ranked else ""
    config_lines = scene01_config_summary(capture_root, aggregate_summary)
    config_rows = scene01_config_rows(capture_root, aggregate_summary)
    required_rows = scene01_required_input_rows(capture_root, aggregate_summary)
    handoff_gate = scene01_handoff_gate_text(required_rows)

    payload["executive_summary"]["conclusion"] = (
        "这份采集包已经具备可直接进入分析的 TikTok 爆款短名单，因为头部样本不仅有排序指标，还保留了可恢复的 caption、hook 和 core topic。"
    )
    payload["executive_summary"]["why_it_matters"] = (
        "它现在不只是按分数堆列表，而是真正可复用的爆款 intake 看板：会保留原始包装逻辑，并能直接交接到后续深拆。"
    )
    payload["executive_summary"]["next_action"] = (
        "先把前 3 条按明确研究方向送进深拆，再基于购物车信号、复用价值和内容线索决定谁优先复刻。"
    )
    payload["executive_summary"]["confidence"] = "medium"

    sections["Executive Conclusion"]["paragraphs"] = [
        "这份 Scene 01 候选板现在更像平台主表而不是一段说明文：先锁强约束输入，再把每条候选写成可直接进 Scene 03 的短名单。",
        f"头部候选主题：{top_topic or '源包缺少 topic 文本'}",
        f"头部候选 hook：{top_hook or '源包缺少 hook 文本'}",
    ]
    sections["Executive Conclusion"]["bullets"] = [
        "这不是简单高播放列表，而是带有复用价值判断和文本恢复线索的候选板。",
        "真正值得先拆的，不一定是播放最高，而是最适合复用到你当前品类或选题的样本。",
        handoff_gate,
    ]
    sections["Executive Conclusion"]["bullets"].extend(config_lines[:4])
    sections["Executive Conclusion"]["bullets"].extend(
        [f"{row[0]}：{row[1]}（{row[2]}）" for row in required_rows]
    )

    rows = []
    for index, video in enumerate(top_ranked, start=1):
        rows.append(
            [
                clean_text(video.get("shortlist_priority")) or f"P{index}",
                scene01_row_handoff_status(video, required_rows),
                shortlist_provenance_cell(video),
                clean_text(video.get("video_url")),
                scene01_study_value_text(video),
                scene01_reuse_fit_text(video),
                scene01_recommended_teardown_direction(video),
                scene01_best_next_scene(video),
                sentence_clip(core_topic_text(video), limit=72) or "主题文本缺失",
                sentence_clip(hook_text(video), limit=76) or "钩子文本缺失",
                ranked_metric_summary(video),
                clean_text(video.get("tkshop_signal")) or "未检测到",
                publish_window_text(video),
                str(video.get("commerce_confidence", "")),
            ]
        )
    sections["Objects To Track"]["table"]["rows"] = rows
    sections["Objects To Track"]["table"]["headers"] = [
        "优先级",
        "交接状态",
        "入选溯源",
        "视频 / 链接",
        "为什么值得研究",
        "适合复用在哪",
        "推荐深拆方向",
        "下一步最适合拆什么",
        "核心主题",
        "钩子强度",
        "表现信号",
        "TikTok Shop 信号",
        "发布时间窗口",
        "商业置信度",
    ]
    sections["Objects To Track"]["paragraphs"] = [
        "主表只放候选视频行，不再把采集配置行混进去。采集配置与强约束输入单独放在结论和说明区。"
    ]

    sections["Why They Matter"]["table"]["rows"] = [
        [
            clean_text(video.get("video_url") or video.get("video_id")),
            sentence_clip(hook_text(video), limit=84) or "钩子文本缺失",
            proof_style_text(video),
            f"reuse={video.get('reuse_value_score', 0)} / popularity={video.get('popularity_score', 0)} / caption={video.get('caption_quality', 'unknown')}",
            shortlist_provenance_cell(video),
            scene01_study_value_text(video),
            scene01_reuse_fit_text(video),
        ]
        for video in top_ranked[:3]
    ]
    sections["Why They Matter"]["table"]["headers"] = [
        "视频",
        "钩子强度",
        "证明风格",
        "转化信号",
        "入选溯源",
        "为什么值得研究",
        "适合复用在哪",
    ]
    sections["Why They Matter"]["bullets"] = [handoff_gate] + config_lines[4:] + [f"{row[0]}：{row[1]}（{row[3]}）" for row in required_rows]

    sections["Fields To Capture Next Time"]["table"]["rows"] = [
        *required_rows,
        ["视频链接", "保证后续深拆还能回溯到原视频", "是"],
        ["Caption / hook 文本", "保留原始包装语言，便于后续拆 hook", "是"],
        ["点赞 / 评论 / 分享", "比较的是表现结构，不只是播放量", "是"],
        ["出镜人或证明物", "把权威加成和包装能力拆开", "是"],
        ["评论样本可用性", "若存在评论，就能继续路由到 Scene 08", "是"],
        ["复用价值评分拆解", "解释为什么这条值得入 shortlist", "是"],
        ["商业置信度", "把研究价值和卖货价值拆开", "是"],
    ]
    sections["Fields To Capture Next Time"]["table"]["headers"] = [
        "字段",
        "为什么要补",
        "下次是否必须",
    ]

    sections["Next Action"]["table"]["rows"] = [
        [
            clean_text(video.get("shortlist_priority")) or str(index),
            scene01_row_handoff_status(video, required_rows),
            clean_text(video.get("video_url") or video.get("video_id")),
            scene01_study_value_text(video),
            scene01_best_next_scene(video),
            scene01_recommended_teardown_direction(video),
            clean_text(video.get("score_breakdown_text")) or "需要补评分拆解",
        ]
        for index, video in enumerate(top_ranked[:3], start=1)
    ]
    sections["Next Action"]["table"]["headers"] = [
        "优先级",
        "交接状态",
        "视频",
        "为什么现在就该推进",
        "Scene 03 交接角色",
        "推荐深拆方向",
        "当前证据缺口",
    ]
    sections["Next Action"]["numbered"] = [
        f"先把短名单第 1 条送进 {teardown_lane_label(top_ranked[0]) if top_ranked else 'Scene 03'}，补一份完整深拆记录。",
        f"把短名单第 2 条当成对照研究样本，重点看 {teardown_lane_label(top_ranked[1]) if len(top_ranked) > 1 else 'hook 或证明差异'} 是否同样成立。",
        "保留短名单第 3 条作为对照基线，并把整张候选板沉淀为下一轮采集的 intake 主表。",
    ]
    sections["Next Action"]["paragraphs"] = [handoff_gate]


def fill_scene_07(payload: dict, ranked_videos: list[dict], comment_entries: list[dict]) -> None:
    from content_graph import shortlist_provenance_cell

    sections = {section["heading"]: section for section in payload["sections"]}
    top_ranked = top_videos(ranked_videos, limit=4)

    payload["executive_summary"]["conclusion"] = (
        "The category signal in this capture pack points to durable interest in human-led, socially legible TikTok packaging rather than feature-heavy explanation."
    )
    payload["executive_summary"]["why_it_matters"] = (
        "This suggests the opportunity is not just in content volume but in simplifying the entry cue so viewers recognize the social or emotional premise immediately."
    )
    payload["executive_summary"]["next_action"] = (
        "Enter the category only if you can package your proof object with the same clarity and lower-friction recognition."
    )
    payload["executive_summary"]["confidence"] = "medium"

    sections["Executive Conclusion"]["paragraphs"] = [
        "这个场景要产出的不是泛洞察，而是类目是否值得进入的判断表。",
        payload["executive_summary"]["conclusion"],
    ]
    sections["High-Level Judgment"]["table"]["rows"] = [
        ["内容热度", "People- and moment-led posts still rank strongly", "Multiple top rows still win on immediate recognition", "中"],
        ["商品表现", "可承接，但需要更强 owned proof", "The current winners still lean on trust transfer and clear proof", "中"],
        ["竞争程度", "Official-account advantage is significant", "Copying the shell alone will not be enough", "中"],
        ["进入吸引力", "优先做，但要走证明物更强的切法", "Opportunity exists but requires sharper proof packaging", "中"],
    ]

    sections["Evidence Clusters"]["table"]["rows"] = [
        [
            sentence_clip(core_topic_text(video), limit=56) or "未恢复关键词",
            "内容热度强",
            f"score={video.get('score', 0)} / likes={safe_int(video.get('digg_count'))}",
            "优先做" if index == 0 else "做",
            display_cue_text(video, limit=80, fallback=video.get("desc")) or "Cue text missing",
            shortlist_provenance_cell(video),
        ]
        for index, video in enumerate(top_ranked[:3])
    ]
    if sections["Evidence Clusters"]["table"].get("headers"):
        headers = list(sections["Evidence Clusters"]["table"]["headers"])
        if len(headers) == 5:
            headers.append("入选溯源")
            sections["Evidence Clusters"]["table"]["headers"] = headers

    sections["Recommended Action"]["table"]["rows"] = [
        ["Hot angles", "人物 / 时刻感优先", "说明内容池还奖励一眼能懂的社会识别信号"],
        ["Overused angles", "解释先行、证明偏慢", "这类打法更容易被挤进普通教程或普通口播区"],
        ["Underserved need", "证明物更强、但不借官方账号外壳", "这是更值得切进去的差异点"],
        ["Audience cue", "用户先认前提，再认功能", "先把前提看懂比补更多卖点更重要"],
    ]
    sections["Recommended Action"]["table"]["title"] = "Category Dispatch"
    sections["Recommended Action"]["table"]["headers"] = ["Cluster", "What Repeats", "Implication"]

    sections["Open Questions"]["table"]["rows"] = [
        ["做", "可以做", "内容热度还在，且证明物路线仍有切入空间"],
        ["不做", "不要做解释先行版本", "容易掉进泛内容，不像强进入点"],
        ["优先做", "优先做强 proof、强识别的进入版本", "更像能在同类里打出差异的路线"],
    ]
    sections["Open Questions"]["bullets"] = [
        "A fuller market-insight call would need more than one account and more than one capture window.",
        f"Comment-sample count available in this pack: {len(comment_entries)}.",
    ]


def fill_scene_09(payload: dict, ranked_videos: list[dict], qualified_videos: list[dict]) -> None:
    sections = {section["heading"]: section for section in payload["sections"]}
    source = qualified_videos[0] if qualified_videos else (top_videos(ranked_videos, limit=1)[0] if ranked_videos else {})
    source_url = clean_text(source.get("video_url"))
    source_desc = normalize_caption_candidate(source.get("desc"))
    source_hook = hook_text(source)
    source_topic = core_topic_text(source)

    payload["executive_summary"]["conclusion"] = (
        "The cleanest replication target in this pack is a recognition-first editorial post that opens from a human or emotional cue, then lets trust and continuation do the rest."
    )
    payload["executive_summary"]["why_it_matters"] = (
        "This is a strong reference format for accounts that need simpler packaging and faster first-frame clarity."
    )
    payload["executive_summary"]["next_action"] = (
        "Adapt the reference by swapping in the user's own proof object or featured person while keeping the same first-frame promise and soft continuation CTA."
    )
    payload["executive_summary"]["confidence"] = "medium"

    sections["Executive Conclusion"]["paragraphs"] = [
        payload["executive_summary"]["conclusion"],
        f"Reference asset: {source_url}",
    ]

    sections["Target"]["table"]["rows"] = [
        ["Target audience", "Viewers who respond to immediate recognition or emotionally clear social packaging"],
        ["Conversion goal", "Drive the next watch, save, follow, or soft interest action"],
        ["Reference asset", source_url],
        ["User product", "Replace with the user's own creator, proof object, or community moment"],
    ]

    sections["Audience"]["paragraphs"] = [
        "The audience does not need a long explanation first. They need an instant reason to care and a clear social or emotional cue that feels native to TikTok.",
    ]

    sections["Message"]["table"]["rows"] = [
        [
            "Hook",
            display_cue_text(source, limit=90, fallback=source_desc) or "Needs clearer owned hook",
            "Swap in your own recognizable cue or outcome in the first frame",
            "Owned hero cue, creator, product outcome, or community moment",
        ],
        [
            "Problem framing",
            "Low-friction, premise-first",
            "Keep the explanation compressed so the cue lands before context",
            "Clear one-line promise or emotional angle",
        ],
        [
            "Proof device",
            "Account authority / featured person / context",
            "Replace platform authority with owned proof or collaborator trust",
            "Receipt, testimonial, feature proof, or known face",
        ],
        [
            "CTA",
            "Soft continuation toward more content",
            "Ask for the next watch or save, not a hard sales jump",
            "Profile follow, save, or low-friction curiosity move",
        ],
    ]

    sections["Structure"]["table"]["rows"] = [
        [
            "Hook frame",
            "Open on the clearest recognizable person, object, or emotional cue.",
            "Make the post legible before explanation starts.",
            "Owned hero shot, creator frame, or emotionally clear visual cue",
            source_hook or "Rewrite the reference cue into owned hook language",
            "Fails if the first frame is decorative instead of legible",
        ],
        [
            "Context beat",
            "Compress the explanation so the post stays premise-led.",
            "Prevent drop-off before the viewer understands why the post matters.",
            "Support visual, caption card, or one short setup shot",
            source_topic or "One short line clarifying the premise",
            "Do not add a dense explainer or too many product details",
        ],
        [
            "Proof beat",
            "Add one trust anchor or proof object before the close.",
            "Replace source-account authority with owned trust.",
            "Receipt, collaborator, result, demo, or testimonial asset",
            "One proof line that reduces skepticism fast",
            "Weak proof will make the adaptation feel copied but not credible",
        ],
        [
            "Close / CTA",
            "End with a continuation move rather than a heavy conversion push.",
            "Keep the post TikTok-native and socially legible.",
            "Return to hero shot, product, or creator frame",
            "Follow for part 2, save this, or watch the next clip",
            "Hard-sell CTA will break the reference logic",
        ],
    ]

    sections["Creative Constraints"]["table"]["rows"] = [
        [
            "Visual identity",
            "Keep recognition-first clarity; change official-account or platform-specific polish",
            "The winning logic is clarity, not borrowed brand authority",
            "Creative lead checks first frame before production",
        ],
        [
            "Claim language",
            "Keep the premise simple; change any unsupported promise",
            "The adaptation should not inherit claims it cannot prove",
            "Strategist or operator validates owned proof line",
        ],
        [
            "Proof style",
            "Keep one fast trust anchor; change who or what carries trust",
            "Smaller accounts need owned proof instead of platform lift",
            "Product or creator owner confirms available proof asset",
        ],
        [
            "CTA wording",
            "Keep a soft continuation CTA; change any hard conversion jump",
            "The reference wins through social-native continuation, not catalog selling",
            "Growth owner approves final follow/save/watch CTA",
        ],
    ]

    sections["Production Handoff"]["table"]["rows"] = [
        [
            "Hook direction",
            source_hook or "Recognition-first owned hook still needs rewrite",
            "Strategist / creative",
            "Owned hero cue or first-frame visual may still be missing",
        ],
        [
            "Proof asset",
            "One owned proof object must replace source-account authority",
            "Operator / product",
            "No adaptation should ship before the proof source is named",
        ],
        [
            "On-screen line / overlay",
            source_topic or "One short premise-support line is required",
            "Copy / strategist",
            "Overlay can bloat if it tries to explain too much",
        ],
        [
            "CTA execution",
            "Close with a follow, save, or next-watch move",
            "Growth / operator",
            "Final CTA destination and wording still need market fit",
        ],
    ]

    sections["Next Action"]["paragraphs"] = [
        "现在就写两版改编稿：一版走人物驱动钩子，一版走证明物驱动钩子，但都保留相同的证明顺序与轻量延续式收口。",
    ]


def fill_scene_04(payload: dict, ranked_videos: list[dict], qualified_videos: list[dict], profile_summary: dict) -> None:
    sections = {section["heading"]: section for section in payload["sections"]}
    source = qualified_videos[0] if qualified_videos else (top_videos(ranked_videos, limit=1)[0] if ranked_videos else {})
    source_url = clean_text(source.get("video_url"))
    source_desc = normalize_caption_candidate(source.get("desc"))
    source_hook = hook_text(source)
    source_topic = core_topic_text(source)
    authority = author_signal_text(source)
    music_style = music_style_text(source)
    video_type = scene04_video_type(source)
    profile_url = clean_text(profile_summary.get("profile_url") or profile_summary.get("profile_final_url"))
    has_downloadable_source = bool(clean_text(source.get("download_addr")) or clean_text(source.get("play_addr")))

    payload["executive_summary"]["conclusion"] = (
        "这条真实单视频拆解目标之所以能跑出来，核心不是表面风格，而是首屏先让人秒懂，再用权威、人物或结果线索做压缩证明。"
    )
    payload["executive_summary"]["why_it_matters"] = (
        "真正可复用的资产不是装饰层，而是从识别到证明再到轻收口的顺序；只要顺序对，换产品或换人设时仍可成立。"
    )
    payload["executive_summary"]["next_action"] = (
        "先按顺序把参考视频重建出来，再把证明层改写成你自己的产品、创作者或证据物也能承接同样决策逻辑。"
    )
    payload["executive_summary"]["confidence"] = "medium"

    sections["Executive Conclusion"]["paragraphs"] = [
        payload["executive_summary"]["conclusion"],
        f"参考视频：{source_url or '参考链接缺失'}",
        f"来源账号基线：{profile_url or '账号链接缺失'}",
    ]
    sections["Executive Conclusion"]["bullets"] = [
        f"已恢复 hook：{source_hook or '源包缺少 hook 文本'}",
        f"已恢复主题线索：{source_topic or '源包缺少主题文本'}",
        f"权威 / 人物信号：{authority or '权威信号较弱或缺失'}",
        f"视频类型归类：{video_type}",
        ("可复核下载源：已存在 play/download 明细，可继续做更细镜头重看。"
         if has_downloadable_source else "可复核下载源：当前只有页面级证据，若要更细镜头拆解需补下载明细。"),
    ]

    sections["Structure Logic"]["table"]["rows"] = scene04_structure_rows(
        source,
        source_url,
        source_desc,
        source_hook,
        source_topic,
        authority,
    )
    sections["Structure Logic"]["paragraphs"] = [
        "主表必须稳定贴近《口红爆款视频拆解报告》的成品视图：时间段 | 场景类型 | 画面内容 | 口播脚本，再补这一段在转化中的作用与素材需求。",
        "如果源视频口播很薄，就优先从字幕、动作、切镜和证明物去重建，不要因为没有完整口播就放弃结构化拆解。",
    ]

    sections["Core Mechanism"]["paragraphs"] = [
        "真正的机制是识别优先的压缩表达：观众先知道谁或什么值得看，然后再接受最短路径的证明，而不是先听长解释。",
        "证明层之所以成立，是因为源视频借到了账号语境、人物熟悉度、结果感或文化线索，把信任转移压缩到了前半段。",
    ]
    sections["Core Mechanism"]["bullets"] = [
        f"视频类型归类：{video_type}。",
        scene04_no_voiceover_judgment(source),
        "可迁移逻辑：首屏清晰 + 压缩证明。",
        "不可直接照抄的 lift：官方账号权威、名人识别度或账号分发优势。",
        ("这条已有可下载视频源，适合继续做逐镜头复核。"
         if has_downloadable_source else "若要继续做逐镜头复核，下一步需要补下载视频或关键帧。"),
    ]
    sections["Core Mechanism"]["table"]["rows"] = scene04_mechanism_rows(source, video_type, authority, source_url)

    sections["可复用公式"]["table"]["rows"] = [
        ["钩子逻辑", source_hook or "先给一个短而可识别的首屏线索", "是", "保留一眼能懂的识别感，但把原视频里的人物 / 对象 / 话题换成自有资产。", "medium"],
        ["画面风格", "偏 editorial / social-native 的原生包装", "部分可复用", "只保留有助于证明顺序的视觉组织，不要抄纯装饰层。", "medium"],
        ["证明逻辑", authority or "借来的权威 / 语境 / 结果感", "是，但要替换", "改成自有 proof、凭证、产品证据或合作方信任，而不是继续借原账号外壳。", "medium"],
        ["CTA 风格", "轻量 continuation close", "是", "更适合继续看、保存、轻量关注，而不是硬切强卖点。", "medium"],
    ]

    sections["Risks And Adaptation Notes"]["table"]["rows"] = [
        ["开头钩子", source_hook or "识别优先的首屏开头", "第一个可见线索要在解释前先告诉观众为什么值得看。", "不要把只有源账号扛得住的铺垫，照搬到自家版本里。", source_url or "primary-video"],
        ["转化节奏", "钩子 -> 铺垫 -> 证明 -> 轻收口", "结构把注意力压缩在前半段，并让证明紧贴开头线索出现。", "如果新产品需要更多说明，优先补证明，不要补长解释。", source_url or "primary-video"],
        ["视觉风格", f"偏 editorial framing，搭配 {music_style.lower()}", "感官层是在辅助识别，不是在跟主信息抢注意力。", "保留节奏和清晰度，不要做装饰性模仿。", source_url or "primary-video"],
    ]

    sections["BGM And Sensory Layer"]["table"]["rows"] = [
        ["BGM / audio mood", music_style, "在原生感和连续观看上提供底层支撑。", "只有在自有音频也能保留同样 editorial 能量时才替换。", source_url or "primary-video-audio"],
        ["Subtitle style", "短句式 premise-led 字幕 / caption 支撑", "即使口播很薄，也能让逻辑继续成立。", "优先保留可读性，别把字幕写成长解释。", source_url or "subtitle-pass"],
        ["Transition rhythm", "快 setup、少空拍、早 proof", "避免视频过早变成长讲解。", "用紧凑切镜或 motion crop，不要做装饰性转场。", source_url or "primary-video"],
        ["留白 / 停顿使用", "极少停顿，注意力持续压在关键信号和证明上", "让整条内容保持原生、压缩、可刷。", "如果改写里要停顿，必须是在给证明加重，不是在拖节奏。", source_url or "primary-video"],
    ]
    sections["BGM And Sensory Layer"]["paragraphs"] = [
        "BGM 不只是陪衬，它直接决定这条内容更像测评、教程、审美拼贴还是情绪推动；因此这一块必须比普通拆解更醒目。",
        "无口播视频尤其依赖音频、字幕密度和动作节奏来补足逻辑，这时感官层就不是装饰，而是结构本身。",
    ]
    sections["Production-Spec Handoff"]["table"]["rows"] = scene04_production_spec_rows(
        source,
        source_url,
        source_hook,
        source_topic,
        authority,
    )
    sections["Production-Spec Handoff"]["table"]["title"] = "制作交接 / 分镜执行表"
    sections["Production-Spec Handoff"]["table"]["headers"] = ["镜头", "这一拍要做什么", "阶段", "建议字幕 / 口播", "执行提醒", "素材需求", "置信度"]
    sections["Production-Spec Handoff"]["paragraphs"] = [
        "这张表直接服务导演 / 剪辑 / 生成器，不是泛分析备注。",
        "如果还要更细化镜头，应继续把 shot_01 到 shot_04 和上面的时间段主表对齐。",
    ]

    sections["Next Action"]["table"]["title"] = "下一步动作 / shot 交接"
    sections["Next Action"]["table"]["headers"] = ["shot_id", "时间", "阶段", "画面 / 动作", "字幕 / 口播", "generator 字段", "素材 / 执行需求"]
    sections["Next Action"]["table"]["rows"] = scene04_storyboard_handoff_rows(
        source,
        source_url,
        source_hook,
        source_topic,
        authority,
    )
    from scene_evidence_refs import attach_scene_04_evidence_refs

    attach_scene_04_evidence_refs(sections, source, profile_summary)


def fill_scene_05(payload: dict, ranked_videos: list[dict], qualified_videos: list[dict], profile_summary: dict) -> None:
    sections = {section["heading"]: section for section in payload["sections"]}
    source = qualified_videos[0] if qualified_videos else (top_videos(ranked_videos, limit=1)[0] if ranked_videos else {})
    source_url = clean_text(source.get("video_url"))
    source_desc = normalize_caption_candidate(source.get("desc"))
    source_hook = hook_text(source)
    source_topic = core_topic_text(source)
    music_style = music_style_text(source)
    proof_style = proof_style_text(source)
    lane = teardown_lane_label(source)
    profile_url = clean_text(profile_summary.get("profile_url") or profile_summary.get("profile_final_url"))

    payload["executive_summary"]["conclusion"] = (
        "这条真实 TikTok 参考视频反推出的是一份以快速识别、少解释、单个信任支点为核心的提示词 / 制作简报，而不是重叙事、重世界观的复杂脚本。"
    )
    payload["executive_summary"]["why_it_matters"] = (
        "这让反推出来的制作简报具备复用价值：保留视觉节奏和前提顺序后，只要替换证明物或主线线索，就能迁移到别的产品或账号。"
    )
    payload["executive_summary"]["next_action"] = (
        "把这份反推制作简报当成结构化创作蓝图使用，并明确区分哪些部分依赖源账号权威，哪些部分属于可迁移的镜头与文案逻辑。"
    )
    payload["executive_summary"]["confidence"] = "medium"

    sections["Executive Conclusion"]["paragraphs"] = [
        payload["executive_summary"]["conclusion"],
        f"参考视频：{source_url or '参考链接缺失'}",
        f"来源账号基线：{profile_url or '账号链接缺失'}",
    ]
    sections["Executive Conclusion"]["bullets"] = [
        f"已恢复钩子：{source_hook or '源包缺少钩子文本'}",
        f"已恢复证明路径：{proof_style}",
        f"主要改写赛道：{lane}",
        "输出必须显式拆成两层：infer 原视频制作简报 + adapt 到用户产品卖点的制作简报。",
    ]
    sections["Structure Logic"]["table"]["rows"] = [
        ["风格", source_topic or "识别优先的编辑型包装", "让内容在细节出现前先具备社交可读性", "style", "medium"],
        ["环境", "社交原生的编辑语境，带一个主导性的识别线索", "避免背景杂乱而遮住核心前提", "environment", "low"],
        ["语气与节奏", "压缩铺垫、尽早给证明、轻量收口", "避免长解释拖慢核心承诺出现", "tone_pacing", "medium"],
        ["镜头", "短节拍、前提先行、快速建立识别", "先给出让观众立刻在意的首屏线索", "camera", "low"],
        ["灯光", "优先清楚可信，而不是过度电影感", "保证证明层清晰可信", "lighting", "low"],
        ["角色", author_signal_text(source) or "识别线索、创作者或承载信任的对象", "尽快承接信任", "character", "medium"],
        ["背景声音", music_style, "支撑整体 editorial 气质，但不要压过主线线索", "background_sound", "low"],
        ["转场 / 剪辑", "快切或紧凑节拍变化", "保护清晰度和推进感", "transition", "medium"],
    ]
    sections["Structure Logic"]["paragraphs"] = [
        "这一块要直接对齐 generator-ready schema：Style / Environment / Tone & Pacing / Camera / Lighting / Character / Shots / Background Sound / Transition。",
        "上表是 infer 层，作用是从原视频反推出制作意图；下游 adapt 层则要把这些字段重新翻译成用户产品可执行版本。",
    ]

    sections["Core Mechanism"]["table"]["rows"] = [
        ["钩子设计", "第一个线索一眼可懂，且具备情绪或社交识别度。", source_hook or source_url or "primary-video", "首屏可见主镜头 / 钩子叠字", "medium"],
        ["证明设计", f"证明层更依赖 {proof_style.lower()}，而不是靠长篇论证。", source_url or "primary-video", "证明物、口碑、结果或人物信任线索", "medium"],
        ["节奏设计", "压缩比电影感复杂度更重要。", source_desc or source_url or "primary-video", "快 setup、早 proof、少解释", "medium"],
        ["转化设计", "收口是在推动继续观看，而不是硬塞强 CTA。", source_url or "primary-video", "延续式 CTA / 继续看 / 保存 / 了解更多", "medium"],
    ]
    sections["Core Mechanism"]["paragraphs"] = [
        "infer 版本回答的是：原视频为什么成立；adapt 版本回答的是：换成你的产品后，这套成立条件要由什么素材来接住。",
    ]

    sections["Reusable Formula"]["table"]["title"] = "Generator-Ready Schema"
    sections["Reusable Formula"]["table"]["headers"] = ["字段", "infer 原视频", "adapt 到你的产品", "generator key", "证据 / 素材", "置信度"]
    sections["Reusable Formula"]["table"]["rows"] = scene05_generator_schema_rows(
        source,
        source_url,
        source_hook,
        source_topic,
        proof_style,
        music_style,
    )
    sections["Reusable Formula"]["paragraphs"] = [
        "这一层输出的是可直接交给视频生成模型或剪辑执行的模块化制作简报，而不是普通分析笔记。",
    ]

    sections["Risks And Adaptation Notes"]["table"]["rows"] = [
        ["1", "0-3s", "开头识别线索", "让前提在一瞬间可读", source_hook or "把可见钩子改写成自有表达", "识别", "首屏主镜头 / 钩子画面", "shot_01", "medium"],
        ["2", "3-8s", "铺垫 / 语境节拍", "压缩交代场景或话题", source_topic or "补一行澄清性叠字", "语境", "辅助画面或字幕", "shot_02", "medium"],
        ["3", "8-14s", "证明节拍", f"用一条信任线索承接 {proof_style.lower()}", "用证明支撑承诺，而不是靠解释", "信任", "自有证明物", "shot_03", "medium"],
        ["4", "14-20s", "延续式收口", "回到主线索并引导下一次点击或继续观看", "延续 CTA", "轻转化", "收口画面 / 片尾卡", "shot_04", "medium"],
    ]
    sections["Risks And Adaptation Notes"]["paragraphs"] = [
        "这里输出的是分镜逐条表，既服务于 reverse-engineer 原视频，也服务于把原视频改写成用户产品版本。",
    ]

    sections["Next Action"]["table"]["title"] = "产品适配 / 改写字段"
    sections["Next Action"]["table"]["headers"] = ["字段", "原视频成立方式", "改成你的产品", "需要补什么", "主要风险"]
    sections["Next Action"]["table"]["rows"] = scene05_product_adapt_rows(
        source,
        source_hook,
        source_topic,
        proof_style,
    )
    sections["Next Action"]["paragraphs"] = [
        "这一层是 adapt 版本：在已有用户产品时，直接把参考视频翻译成可执行制作简报，而不是停留在原视频 prompt 反推。",
    ]
    sections["Production-Spec Handoff"]["table"]["rows"] = [
        ["原始制作简报结构", "infer 层 schema 与证据字段", "策略 / 生成器", "如果字段仍空，需要补截图、字幕或下载明细", "内容策略"],
        ["分镜逐条表", "shot_01 到 shot_04 的分镜与字幕 / 动作节拍", "剪辑 / 生成器", "镜头级证据不足会导致误生成", "导演 / 剪辑"],
        ["产品适配简报", "hook / proof / scene_character / cta_close 改写版", "创意 / 生成器", "没有产品卖点与素材就无法真正 adapt", "运营 / 创意"],
        ["素材 / 人员清单", "人物、产品、证明物、字幕与音频需求", "制片 / 执行", "缺实物素材时必须标红，不要假设资产存在", "制片"],
    ]
    from scene_evidence_refs import attach_scene_05_evidence_refs

    attach_scene_05_evidence_refs(sections, source, profile_summary)


def fill_scene_10(payload: dict, ranked_videos: list[dict], qualified_videos: list[dict], profile_summary: dict) -> None:
    sections = {section["heading"]: section for section in payload["sections"]}
    source = qualified_videos[0] if qualified_videos else (top_videos(ranked_videos, limit=1)[0] if ranked_videos else {})
    source_url = clean_text(source.get("video_url"))
    source_desc = normalize_caption_candidate(source.get("desc"))
    source_hook = hook_text(source)
    source_topic = core_topic_text(source)
    profile_url = clean_text(profile_summary.get("profile_url") or profile_summary.get("profile_final_url"))

    payload["executive_summary"]["conclusion"] = (
        "This real TikTok reference can seed a product-image-to-video brief when the operator preserves the same recognition-first promise but rebuilds the proof beats from still assets that actually exist."
    )
    payload["executive_summary"]["why_it_matters"] = (
        "The value is not a fake final render. It is a production-safe brief that keeps hook, proof order, and CTA visible while labeling the asset gaps that still block execution."
    )
    payload["executive_summary"]["next_action"] = (
        "Use the top reference as the packaging control, then rebuild it into an image-compatible shot flow before handing it to production or a render model."
    )
    payload["executive_summary"]["confidence"] = "medium"

    sections["Executive Conclusion"]["paragraphs"] = [
        payload["executive_summary"]["conclusion"],
        f"Reference video: {source_url or 'missing reference URL'}",
        f"来源账号基线：{profile_url or 'missing profile URL'}",
    ]

    sections["Target"]["table"]["rows"] = [
        ["Audience", "Viewers who need the promise to be obvious in the first frame", "Still-image inputs have less room for slow setup"],
        ["Market", "Use the target market passed by the operator", "Overlay and CTA phrasing should fit the market"],
        ["Conversion goal", "Drive the next click, save, or product curiosity move", "Avoid a generic beauty montage with no action goal"],
        ["Video type", "Recognition-first image-led short video", "Chosen because the reference wins on packaging clarity, not on impossible footage"],
    ]

    sections["Audience"]["paragraphs"] = [
        "The viewer must understand the promise immediately even if the brief only has product stills, text overlays, and simple motion treatment available."
    ]
    sections["Audience"]["bullets"] = [
        f"Top reference hook: {source_hook or 'hook text missing in source pack'}",
        f"Top reference topic cue: {source_topic or 'topic cue missing in source pack'}",
    ]

    sections["Message"]["table"]["rows"] = [
        ["Core promise", display_cue_text(source, limit=80, fallback=source_desc) or "Needs owned-product promise", "Hero product image plus first overlay line", "Yes if no owned product image is attached"],
        ["Primary proof", "One owned proof object replacing account authority", "Close-up product detail, before/after, ingredient, or testimonial card", "Likely"],
        ["Secondary proof", "A second support cue that reduces skepticism", "Packaging, review snippet, feature callout, or demo frame", "Likely"],
        ["CTA", "Soft continuation or next-step curiosity CTA", "Final overlay frame", "No if overlay can be authored now"],
    ]

    sections["Structure"]["table"]["rows"] = [
        ["Hook", "Fast hero image with motion crop or zoom", source_hook or "Rewrite the hook from the reference into image-safe language", "Immediate recognition", "Owned hero image", "Yes if hero image missing"],
        ["Proof 1", "Primary proof image or close-up", "State the clearest proof claim", "Replace source authority with owned proof", "Owned proof asset", "Likely"],
        ["Proof 2", "Secondary support image or testimonial-style card", "Reduce doubt without over-explaining", "Strengthen trust", "Support image or review card", "Likely"],
        ["Close", "Return to product plus CTA overlay", "Ask for the next click, save, or learn-more move", "Soft conversion", "Hero or CTA card", "No if overlay can be authored"],
    ]

    sections["Creative Constraints"]["table"]["rows"] = [
        ["Visual style", "Recognition-first, editorial, socially legible", "The video becomes decorative and loses clarity", "Keep overlays short and motion simple"],
        ["Tone", "Premise-first rather than feature-dump", "The viewer does not know why to care quickly enough", "Compress copy into hook plus proof line"],
        ["Must show", "One owned proof object or trust cue", "The adaptation relies only on borrowed authority from the source reference", "Add proof asset before production"],
        ["Must avoid", "Invented lifestyle footage or talent scenes", "The brief becomes impossible to execute from images only", "Label unsupported scenes as pending instead of implying they exist"],
    ]

    sections["Production Handoff"]["table"]["rows"] = [
        [
            "Hook frame",
            source_hook or "Needs owned-product hook",
            "Need hero image and first overlay line",
            "Creative / design",
        ],
        [
            "Primary proof beat",
            "One owned proof object should replace source-account authority in beat two",
            "Need proof asset selection and proof claim",
            "Operator / product",
        ],
        [
            "VO / overlay draft",
            f"{source_hook or 'Hook line'} -> one proof line -> soft CTA",
            "Need final market phrasing and supported product language",
            "Copy / strategist",
        ],
        [
            "CTA treatment",
            "Use a save, learn-more, or follow-style continuation CTA tied to the actual destination",
            "Need final conversion destination and CTA card",
            "Growth / operator",
        ],
    ]

    sections["Next Action"]["table"]["rows"] = [
        ["Hook framing", "The top reference proves the packaging style works", "Need one owned hero image and first overlay rewrite"],
        ["Proof order", "Still-image formats often fail because proof appears too late", "Need proof asset prioritization"],
        ["CTA treatment", "The adaptation needs a social-native close, not a catalog close", "Need final CTA wording by market"],
    ]


def fill_scene_11(payload: dict, ranked_videos: list[dict], qualified_videos: list[dict], profile_summary: dict) -> None:
    sections = {section["heading"]: section for section in payload["sections"]}
    references = choose_reference_pool(ranked_videos, qualified_videos, limit=4)
    top_ref = references[0] if references else {}

    payload["executive_summary"]["conclusion"] = (
        "This real TikTok capture pack is strong enough to seed a hot-video replication pipeline built around recognition-first editorial posts, not around blind copying."
    )
    payload["executive_summary"]["why_it_matters"] = (
        "The pipeline is useful because it turns ranked TikTok evidence into a repeatable weekly sourcing, teardown, adaptation, and queueing cadence."
    )
    payload["executive_summary"]["next_action"] = (
        "Use the top-ranked reference as the first weekly control, then generate 2-3 owned-proof adaptations instead of cloning the official-account shell."
    )
    payload["executive_summary"]["confidence"] = "medium"

    sections["Executive Conclusion"]["paragraphs"] = [
        payload["executive_summary"]["conclusion"],
        f"Reference account: {clean_text(profile_summary.get('profile_url') or profile_summary.get('profile_final_url'))}",
    ]
    sections["Executive Conclusion"]["bullets"] = [
        "The capture pack already gives a usable discovery pool, shortlist, and first replication target.",
        "The reusable asset is the operating cadence and decision gate, not the original account authority.",
    ]

    sections["Core Invariant"]["paragraphs"] = [
        "Every candidate entering the pipeline should have a clear first-frame recognition cue plus enough visible proof to survive adaptation onto a smaller or different account."
    ]
    sections["Core Invariant"]["bullets"] = [
        "Do not queue videos whose main advantage is only official-account distribution.",
        "Treat hook, proof, and continuation CTA as the minimum reusable unit.",
    ]
    sections["Core Invariant"]["table"]["rows"] = build_scene_11_invariant_rows(references)

    sections["Variable Matrix"]["table"]["rows"] = build_scene_11_pipeline_rows(references)

    sections["Expected Effect"]["paragraphs"] = [
        "This pipeline should reduce time spent re-deciding what to copy and force a clearer handoff from discovery into adaptation and test queueing."
    ]
    sections["Expected Effect"]["bullets"] = [
        "Higher-quality weekly shortlist because the replication gate is explicit.",
        "Faster creative generation because teardown outputs directly into owned-proof variations.",
        "Less wasted production on references that cannot transfer cleanly.",
    ]

    sections["What To Learn"]["table"]["rows"] = build_scene_11_learning_rows(references)
    sections["Execution Handoff"]["table"]["rows"] = build_scene_11_handoff_rows(references)

    sections["Next Action"]["numbered"] = [
        f"Promote {clean_text(top_ref.get('video_url')) or 'the top-ranked post'} to the first replication control.",
        "Write one creator-led and one proof-object-led adaptation from the same reference.",
        "Run one weekly cycle and record which candidates failed the transferability gate.",
    ]


def fill_scene_12(payload: dict, ranked_videos: list[dict], qualified_videos: list[dict], profile_summary: dict) -> None:
    sections = {section["heading"]: section for section in payload["sections"]}
    references = choose_reference_pool(ranked_videos, qualified_videos, limit=4)
    profile_url = clean_text(profile_summary.get("profile_url") or profile_summary.get("profile_final_url"))

    payload["executive_summary"]["conclusion"] = (
        "This TikTok capture pack can seed a one-product multi-style testing matrix by turning real ranked references into four distinct recognition-first creative directions."
    )
    payload["executive_summary"]["why_it_matters"] = (
        "The matrix is useful because it preserves one invariant message while varying hook framing, proof device emphasis, and audience lens across styles."
    )
    payload["executive_summary"]["next_action"] = (
        "Lock the product truth and owned proof asset first, then map it onto the four ranked-reference style families below."
    )
    payload["executive_summary"]["confidence"] = "medium"

    sections["Executive Conclusion"]["paragraphs"] = [
        payload["executive_summary"]["conclusion"],
        f"来源账号基线：{profile_url}",
    ]
    sections["Executive Conclusion"]["bullets"] = [
        "This is a real TikTok reference matrix, not a fabricated product brief.",
        "Rows that need product assets are marked so the operator knows what must be added before production.",
    ]

    sections["Core Invariant"]["paragraphs"] = [
        "Keep the same product truth and target outcome across all variants; only the packaging family should change."
    ]
    sections["Core Invariant"]["table"]["rows"] = build_scene_12_invariant_rows(references)

    sections["Variable Matrix"]["table"]["rows"] = build_scene_12_style_rows(references)

    sections["Expected Effect"]["paragraphs"] = [
        "The matrix should reveal whether the product performs better with creator-led, emotion-led, community-led, or more neutral editorial packaging."
    ]
    sections["Expected Effect"]["bullets"] = [
        "Recognition-first styles should improve early hold rate.",
        "Proof-device differences should clarify how much authority replacement the product needs.",
        "Audience-lens variation should show which social framing is most portable.",
    ]
    sections["Expected Effect"]["table"]["rows"] = build_scene_12_expected_effect_rows(references)

    sections["What To Learn"]["table"]["rows"] = build_scene_12_learning_matrix(references)
    sections["Execution Handoff"]["table"]["rows"] = build_scene_12_handoff_rows(references)

    sections["Next Action"]["numbered"] = [
        "Choose one owned product and one owned proof asset before shooting.",
        "Launch the top two style families first, then keep the other two as contrast tests.",
        "Record which variant wins on hold, saves, and comment quality before expanding volume.",
    ]
    sections["Next Action"]["table"]["rows"] = build_scene_12_priority_rows(references)


def fill_scene_13(
    payload: dict,
    ranked_videos: list[dict],
    qualified_videos: list[dict],
    profile_summary: dict,
    target_markets: list[str],
) -> None:
    sections = {section["heading"]: section for section in payload["sections"]}
    references = choose_reference_pool(ranked_videos, qualified_videos, limit=3)
    profile_url = clean_text(profile_summary.get("profile_url") or profile_summary.get("profile_final_url"))
    markets = target_markets or ["Need target market"]

    payload["executive_summary"]["conclusion"] = (
        "This TikTok capture pack can support a multi-market localization blueprint by preserving one recognition-first invariant while mapping where hook wording, talent cue, and tone would need market-specific adaptation."
    )
    payload["executive_summary"]["why_it_matters"] = (
        "The safe output here is a localization planning grid, not fabricated translated scripts or market-native copy that lacks owned product evidence."
    )
    payload["executive_summary"]["next_action"] = (
        "Choose the target markets now, then add owned product truth and native-language evidence before writing final market scripts."
    )
    payload["executive_summary"]["confidence"] = "low-to-medium"

    sections["Executive Conclusion"]["paragraphs"] = [
        payload["executive_summary"]["conclusion"],
        f"Reference account baseline: {profile_url}",
    ]
    sections["Executive Conclusion"]["bullets"] = [
        "This import stays at localization blueprint level.",
        "The ranked TikTok references show portable recognition logic, but not final translated conversion copy.",
    ]

    sections["Target"]["table"]["rows"] = [
        ["Core product promise", "Recognition-first social promise anchored to one owned proof object", "No"],
        ["Hook wording", "Derived from ranked references but must be rewritten per market", "Yes"],
        ["Talent / scene cue", "Keep only if the cue exists in the local market context", "Yes"],
        ["CTA tone", "Soft continuation or next-step action adapted by market norm", "Yes"],
    ]

    sections["Audience"]["paragraphs"] = [
        "Audience expectation should be treated as market-specific even when the invariant creative logic stays constant. The same ranked TikTok cue may need a different emotional framing, trust device, or talent cue outside the source context."
    ]
    sections["Audience"]["bullets"] = [f"Target markets requested: {', '.join(markets)}"]

    sections["Message"]["table"]["rows"] = build_scene_13_market_rows(references, markets)

    sections["Structure"]["paragraphs"] = [
        "Keep the first-frame recognition logic fixed, then localize wording, cultural cue, and tone only after owned product proof and native-language review are available."
    ]
    sections["Structure"]["numbered"] = [
        "Lock one invariant message and one owned proof object first.",
        "Write one localization note per market before any script drafting.",
        "Delay final script translation until native-language quality control is available.",
    ]

    sections["Creative Constraints"]["bullets"] = [
        "Do not fabricate translated ad copy from ranked captions alone.",
        "Do not assume the same person, scene, or cultural cue works in every market.",
        "Do not let localization drift away from the invariant promise.",
    ]

    sections["Next Action"]["numbered"] = [
        "Confirm the 2-3 target markets explicitly.",
        "Add owned product, proof, and local-language review input for each market.",
        "Only then turn this blueprint into final per-market hook and script directions.",
    ]


def fill_scene_14(payload: dict, ranked_videos: list[dict], qualified_videos: list[dict], profile_summary: dict) -> None:
    sections = {section["heading"]: section for section in payload["sections"]}
    references = choose_reference_pool(ranked_videos, qualified_videos, limit=4)
    profile_url = clean_text(profile_summary.get("profile_url") or profile_summary.get("profile_final_url"))
    top_ref = references[0] if references else {}

    payload["executive_summary"]["conclusion"] = (
        "This TikTok capture pack can support a launch asset family blueprint by reusing one ranked recognition-first promise across hero, support, and short-video launch assets."
    )
    payload["executive_summary"]["why_it_matters"] = (
        "The useful output here is a coordinated blueprint and production order, not a fake claim that owned product images already exist."
    )
    payload["executive_summary"]["next_action"] = (
        "Lock one owned hero product or proof object, then translate the ranked references below into a P1 launch asset family."
    )
    payload["executive_summary"]["confidence"] = "medium"

    sections["Executive Conclusion"]["paragraphs"] = [
        payload["executive_summary"]["conclusion"],
        f"Reference account baseline: {profile_url}",
    ]
    sections["Executive Conclusion"]["bullets"] = [
        "This import stays at blueprint level where owned launch assets are missing.",
        "The ranked TikTok pack is being used to define shared message logic and asset priority, not to fabricate finished design files.",
    ]

    sections["Core Invariant"]["paragraphs"] = [
        "Every launch asset should carry the same first-frame promise, then vary only by asset job: click, context, benefit, proof, or motion."
    ]
    sections["Core Invariant"]["bullets"] = [
        "Do not let each asset invent a different message.",
        "Replace official-account trust with one owned proof device before production.",
        "Keep P1 assets limited to the few pieces that can realistically launch together.",
    ]

    sections["Variable Matrix"]["table"]["rows"] = build_scene_14_asset_rows(references)

    sections["Expected Effect"]["paragraphs"] = [
        "A shared asset-family blueprint should reduce launch drift between images and short video while keeping the creative direction grounded in real TikTok recognition patterns."
    ]
    sections["Expected Effect"]["bullets"] = [
        "Faster creative handoff because asset jobs and priority order are explicit.",
        "Less message drift between hero image, support images, and motion launch asset.",
        "Cleaner launch sequencing when only P1 assets can be produced immediately.",
    ]

    sections["What To Learn"]["table"]["rows"] = build_scene_14_learning_rows(references)

    sections["Next Action"]["numbered"] = [
        f"Use {clean_text(top_ref.get('video_url')) or 'the top-ranked reference'} as the message anchor for the P1 family.",
        "Add one owned product image, proof object, or collaborator asset before turning this blueprint into production files.",
        "Ship main image plus short video first, then fill support images only after the shared promise is locked.",
    ]


def fill_scene_15(
    payload: dict,
    ranked_videos: list[dict],
    qualified_videos: list[dict],
    profile_summary: dict,
    target_languages: list[str],
) -> None:
    sections = {section["heading"]: section for section in payload["sections"]}
    references = choose_reference_pool(ranked_videos, qualified_videos, limit=3)
    profile_url = clean_text(profile_summary.get("profile_url") or profile_summary.get("profile_final_url"))
    languages = target_languages

    payload["executive_summary"]["conclusion"] = (
        "This TikTok capture pack can support an image-translation blueprint by mapping text hierarchy and localization risk, but it cannot produce final translated image copy because the pack does not include OCR-ready source blocks."
    )
    payload["executive_summary"]["why_it_matters"] = (
        "The safe output here is a localization planning grid for image copy layers, not fabricated OCR text or ready-to-render translated creative."
    )
    payload["executive_summary"]["next_action"] = (
        "Confirm the target languages now, then add OCR output, product context, and native-language review before any final image-copy translation."
    )
    payload["executive_summary"]["confidence"] = "low"

    sections["Executive Conclusion"]["paragraphs"] = [
        payload["executive_summary"]["conclusion"],
        f"Reference account baseline: {profile_url}",
    ]
    sections["Executive Conclusion"]["bullets"] = [
        "This import stays at image-localization blueprint level.",
        "Ranked TikTok references can suggest hierarchy and packaging pressure, but not recover missing image text faithfully.",
    ]

    sections["Target"]["table"]["rows"] = [
        ["Platform", "TikTok"],
        ["Requested target languages", ", ".join(languages)],
        ["Source image text status", "Missing from current capture pack; OCR required before final translation"],
        ["Safe output", "Blueprint for hierarchy, fit risk, and review steps"],
    ]

    sections["Audience"]["paragraphs"] = [
        "Treat the target viewer need as a conversion-language problem, not a literal translation problem. The ranked TikTok pack only helps infer how compressed and legible the image message likely needs to be."
    ]
    sections["Audience"]["bullets"] = [f"Target languages requested: {', '.join(languages)}"]

    sections["Message"]["table"]["rows"] = build_scene_15_message_rows(references, languages)

    sections["Structure"]["paragraphs"] = [
        "Recover the source text blocks first, then localize headline, support, and CTA layers in that order so fit risk is managed before rendering."
    ]
    sections["Structure"]["table"]["rows"] = build_scene_15_structure_rows()

    sections["Creative Constraints"]["bullets"] = [
        "Do not pretend OCR-extracted source copy already exists in this capture pack.",
        "Do not fabricate final localized image copy from ranked captions or post descriptions alone.",
        "Do not force translated strings into the original layout without checking expansion, hierarchy, and readability.",
    ]

    sections["Next Action"]["numbered"] = [
        "Run OCR or manually recover the source image text blocks in reading order.",
        "Add product context and one native-language reviewer for each requested language.",
        "Only then convert this blueprint into a real localized image-copy brief or render-ready file.",
    ]


def fill_scene_16(payload: dict, ranked_videos: list[dict], qualified_videos: list[dict], profile_summary: dict) -> None:
    sections = {section["heading"]: section for section in payload["sections"]}
    references = choose_reference_pool(ranked_videos, qualified_videos, limit=3)
    profile_url = clean_text(profile_summary.get("profile_url") or profile_summary.get("profile_final_url"))

    payload["executive_summary"]["conclusion"] = (
        "This TikTok capture pack can support a competitor main-image benchmark blueprint by comparing recognition-first cover patterns, but it cannot finalize an outperform brief until an owned image or product sample is added."
    )
    payload["executive_summary"]["why_it_matters"] = (
        "The safe reusable asset is the benchmark lens: what visual code earns the click, what likely depends on account authority, and what should be translated into an owned-image direction."
    )
    payload["executive_summary"]["next_action"] = (
        "Use the ranked covers below as benchmark references, then add one owned main image or product asset before locking the revised design direction."
    )
    payload["executive_summary"]["confidence"] = "low-to-medium"

    sections["Executive Conclusion"]["paragraphs"] = [
        payload["executive_summary"]["conclusion"],
        f"Reference account baseline: {profile_url}",
    ]
    sections["Executive Conclusion"]["bullets"] = [
        "This output is a benchmark blueprint, not a final redesign of a missing owned image.",
        "The capture pack provides competitor-side cover cues but not a trustworthy owned-image comparison set.",
    ]

    sections["Target"]["table"]["rows"] = [
        ["Platform", "TikTok"],
        ["Category", "Recognition-first editorial/social cover benchmarking"],
        ["User asset", "Missing in current capture pack; add owned main image or product sample"],
        ["Competitor count", str(len(references))],
    ]

    sections["Audience"]["paragraphs"] = [
        "The likely click context here is a fast social-feed decision, where the cover or first visible frame must compress recognition, emotional cue, or proof cue before any explanation is read."
    ]

    sections["Message"]["table"]["rows"] = build_scene_16_rows(references)

    sections["Structure"]["paragraphs"] = [
        "Treat the strongest ranked cover as the benchmark for click logic, then rewrite that logic into an owned-image direction that uses the user's own product, proof object, or talent instead of platform authority."
    ]
    sections["Structure"]["numbered"] = [
        "Choose one ranked reference whose click logic is portable without celebrity or official-account lift.",
        "Define the owned proof device that will replace TikTok account authority.",
        "Sketch one safer control image and one sharper outperform concept after the owned asset is available.",
    ]

    sections["Creative Constraints"]["bullets"] = [
        "Do not benchmark on aesthetics alone; benchmark on probable click trigger.",
        "Do not claim the user's image is weaker or stronger until an owned main image is provided.",
        "Avoid copying official-account branding or celebrity recognition that the user does not own.",
    ]

    sections["Next Action"]["numbered"] = [
        "Add one owned main image or product sample to complete the benchmark loop.",
        "Use the top-ranked reference to define the first outperform hypothesis, not the final design.",
        "Only after the owned asset is attached should the benchmark become a true revised main-image brief.",
    ]


def main() -> None:
    args = parse_args()
    capture_root = Path(args.capture_root).resolve()

    aggregate_summary, profile_summary, ranked_videos, qualified_videos = load_pack_files(capture_root)

    skill_root = Path(__file__).resolve().parents[1]
    catalog = load_catalog(skill_root)
    comment_entries = collect_comment_entries(capture_root)
    scene_ref = args.scene.strip().lower()
    if scene_ref == "auto":
        inferred_scene, _ = infer_scene_from_capture_pack(ranked_videos, qualified_videos, comment_entries)
        scene = resolve_scene(catalog, inferred_scene)
    else:
        scene = resolve_scene(catalog, args.scene)

    default_project = f"TikTok Capture Pack - {clean_text(profile_summary.get('profile_url'))}".strip(" -")
    project = clean_text(args.project) or default_project or "tiktok-capture-pack"
    context = make_context(capture_root, aggregate_summary, profile_summary, ranked_videos, qualified_videos)
    payload = build_report_payload(scene, project, context)
    content_graph = read_json_file(capture_root / "content_graph.json") if (capture_root / "content_graph.json").exists() else {}
    fill_common(
        payload,
        project,
        context,
        capture_root,
        aggregate_summary,
        profile_summary,
        ranked_videos,
        qualified_videos,
        content_graph=content_graph if isinstance(content_graph, dict) else None,
    )
    target_markets = parse_target_markets(args.target_markets)
    target_languages = parse_target_languages(args.target_languages)
    if scene["id"] == "15" and not target_languages:
        raise SystemExit("Scene 15 capture-pack import requires --target-languages with one or more explicit target languages.")

    if scene["id"] == "01":
        fill_scene_01(payload, ranked_videos, aggregate_summary, capture_root)
    elif scene["id"] == "02":
        fill_scene_02(payload, capture_root, aggregate_summary, ranked_videos, qualified_videos)
    elif scene["id"] == "03":
        fill_scene_03(payload, ranked_videos, qualified_videos, aggregate_summary, capture_root)
    elif scene["id"] == "04":
        fill_scene_04(payload, ranked_videos, qualified_videos, profile_summary)
    elif scene["id"] == "05":
        fill_scene_05(payload, ranked_videos, qualified_videos, profile_summary)
    elif scene["id"] == "07":
        fill_scene_07(payload, ranked_videos, comment_entries)
    elif scene["id"] == "08":
        fill_scene_08(payload, capture_root, ranked_videos)
    elif scene["id"] == "09":
        fill_scene_09(payload, ranked_videos, qualified_videos)
    elif scene["id"] == "10":
        fill_scene_10(payload, ranked_videos, qualified_videos, profile_summary)
    elif scene["id"] == "11":
        fill_scene_11(payload, ranked_videos, qualified_videos, profile_summary)
    elif scene["id"] == "12":
        fill_scene_12(payload, ranked_videos, qualified_videos, profile_summary)
    elif scene["id"] == "13":
        fill_scene_13(payload, ranked_videos, qualified_videos, profile_summary, target_markets)
    elif scene["id"] == "14":
        fill_scene_14(payload, ranked_videos, qualified_videos, profile_summary)
    elif scene["id"] == "15":
        fill_scene_15(payload, ranked_videos, qualified_videos, profile_summary, target_languages)
    elif scene["id"] == "16":
        fill_scene_16(payload, ranked_videos, qualified_videos, profile_summary)
    elif scene["id"] == "18":
        fill_scene_18(payload, capture_root, ranked_videos, profile_summary)
    elif scene["id"] == "19":
        fill_scene_19(payload, capture_root, ranked_videos, profile_summary)
    elif scene["id"] == "17":
        fill_scene_17(payload, ranked_videos, profile_summary)
    else:
        raise SystemExit("This importer currently supports scene auto, 01, 02, 03, 04, 05, 07, 08, 09, 10, 11, 12, 13, 14, 15, 16, 17, 18, and 19.")

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output = output.with_name(f"scene-{scene['id']}-{output.name.split('scene-', 1)[-1]}" if output.name.startswith("scene-auto-") else output.name)
    write_json_file(output, payload)
    print(output)


if __name__ == "__main__":
    main()

