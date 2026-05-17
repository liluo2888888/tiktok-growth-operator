from __future__ import annotations

import re
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any

from text_normalization import normalize_text, write_json_file


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


def sentence_clip(text: str, limit: int = 120) -> str:
    value = clean_text(text)
    if len(value) <= limit:
        return value
    return value[: max(0, limit - 1)].rstrip() + "…"


def short_list_text(values: list[object], limit: int = 3) -> str:
    items = [clean_text(item) for item in values if clean_text(item)]
    return ", ".join(items[:limit])


def strip_display_noise(text: str) -> str:
    compact = clean_text(text)
    compact = re.sub(r"[\u200b-\u200f\u202a-\u202e\ufeff]", "", compact)
    return compact.strip()


COMMENT_NOISE_PATTERNS = [
    re.compile(r"^[\W_]+$"),
    re.compile(r"^(ha)+$", re.IGNORECASE),
    re.compile(r"^(lol)+$", re.IGNORECASE),
]


def detect_theme(text: str) -> str:
    lowered = text.lower()
    if any(
        token in lowered
        for token in [
            "shipping",
            "arrived",
            "delivery",
            "package",
            "packaging",
            "damaged box",
            "mailer",
            "arrived crushed",
            "slow shipping",
            "broken seal",
            "sealed",
            "leaking",
            "leaked",
            "pilling",
        ]
    ):
        return "物流 / 包装顾虑"
    if any(token in lowered for token in ["fake", "authentic", "real or fake", "counterfeit", "dupe?", "real product", "original or fake"]):
        return "真假 / 正品顾虑"
    if any(
        token in lowered
        for token in ["shade", "undertone", "tone match", "my skin tone", "which color", "which shade", "olive-friendly", "oxidiz", "pull too peach"]
    ):
        return "shade / 色号适配"
    if any(token in lowered for token in ["return", "refund", "send it back", "returned", "exchange", "money back"]):
        return "退货 / 退款顾虑"
    if any(
        token in lowered
        for token in ["before and after", "before/after", "results after", "did this work", "worked for me", "daylight proof", "texture closeups", "morning clip"]
    ):
        return "前后对比证明"
    if "ai remix" in lowered or "ai " in lowered:
        return "AI 控制 / 隐私顾虑"
    if "verified" in lowered or "verification" in lowered:
        return "认证 / 可信度"
    if "support" in lowered:
        return "售后 / 求助需求"
    if "watching tiktok on tiktok" in lowered or "tiktok posting on tiktok" in lowered:
        return "平台自反应"
    if "turn off" in lowered or "opt out" in lowered or "remove" in lowered:
        return "关闭功能 / 用户控制"
    if "price" in lowered or "expensive" in lowered or "cheap" in lowered or "worth" in lowered:
        return "价格 / 性价比顾虑"
    if "buy" in lowered or "need" in lowered or "want" in lowered or "where" in lowered:
        return "购买意向"
    if any(token in lowered for token in ["watched it twice", "watch it twice", "can't stop", "so beautiful", "hermosos", "laughed", "smiled"]):
        return "反复观看 / 愉悦感"
    if any(token in lowered for token in ["cartoons used to be", "how old are we", "childhood", "used to be", "remember this"]):
        return "怀旧反应"
    return "一般反应"


def normalize_comment_text(text: str) -> str:
    compact = unicodedata.normalize("NFKC", clean_text(text))
    compact = " ".join(compact.split())
    compact = strip_display_noise(compact)
    for token in ["棣冦亙", "馃槀", "馃ぃ", "馃槶", "鉂わ笍", "鈾"]:
        compact = compact.replace(token, "")
    compact = re.sub(r"([!?.,])\1{2,}", r"\1", compact)
    compact = re.sub(r"\b(\w{2,})(?:\s+\1\b)+", r"\1", compact, flags=re.IGNORECASE)
    compact = compact.replace("  ", " ")
    return compact.strip(" ,;:-")


def low_signal_reason(text: str) -> str:
    normalized = normalize_comment_text(text)
    if not normalized:
        return "empty"
    if len(normalized) < 4:
        return "too_short"
    lowered = normalized.lower()
    if lowered in {"lol", "haha", "omg", "wow", "same", "nice", "cool", "first"}:
        return "generic_reaction"
    if any(token in lowered for token in ["follow me", "let be friends", "sub back", "friend me"]):
        return "spam_invite"
    if any(pattern.fullmatch(lowered) for pattern in COMMENT_NOISE_PATTERNS):
        return "emoji_or_noise"
    return ""


def is_low_signal_comment(text: str) -> bool:
    return bool(low_signal_reason(text))


def comment_cluster_type(theme: str) -> str:
    if theme in {"购买意向", "价格 / 性价比顾虑", "shade / 色号适配", "前后对比证明"}:
        return "购买因素"
    if theme in {"AI 控制 / 隐私顾虑", "关闭功能 / 用户控制", "售后 / 求助需求", "物流 / 包装顾虑", "真假 / 正品顾虑", "退货 / 退款顾虑"}:
        return "差评痛点"
    if theme in {"认证 / 可信度"}:
        return "信任信号"
    return "好评关键词"


def estimate_price_band(text: str) -> str:
    lowered = text.lower()
    if any(token in lowered for token in ["cheap", "affordable", "budget", "$", "price"]):
        return "价格敏感"
    if any(token in lowered for token in ["premium", "worth it", "expensive", "luxury", "high end", "splurge"]):
        return "偏高端"
    return "不明确"


def signal_tier_for_entry(entry: dict) -> str:
    if clean_text(entry.get("high_purchase_intent")) or entry.get("is_high_purchase_intent"):
        return "high"
    if safe_int(entry.get("reply_comment_total")) >= 8 or safe_int(entry.get("digg_count")) >= 100:
        return "high"
    if safe_int(entry.get("reply_comment_total")) >= 3 or safe_int(entry.get("digg_count")) >= 20:
        return "medium"
    return "low"


def synthesize_reply_signal(entry: dict) -> str:
    reply_total = safe_int(entry.get("reply_comment_total"))
    summary = clean_text(entry.get("reply_summary"))
    if summary:
        return summary
    theme = clean_text(entry.get("theme"))
    sample_kind = clean_text(entry.get("sample_kind"))
    if sample_kind == "reply" and reply_total >= 1:
        return f"这是直接回复样本，显示评论区已经在围绕“{theme or '该议题'}”做追问或经验补充。"
    if reply_total >= 25 and theme in {"认证 / 可信度", "售后 / 求助需求", "关闭功能 / 用户控制", "价格 / 性价比顾虑", "购买意向", "物流 / 包装顾虑", "退货 / 退款顾虑"}:
        return f"回复链压力较重（{reply_total} 条回复），大概率集中在质疑、追问、售后或下单前确认。"
    if reply_total >= 8:
        return f"回复链活跃（{reply_total} 条回复），已经足够视为真实的购买前确认或异议处理信号。"
    if reply_total >= 3:
        return f"有一定回复链活动（{reply_total} 条回复），值得继续检查追问、补充证据和售后语言。"
    return "未恢复出有意义的回复链信号。"


def canonical_comment_key(text: str, *, is_reply: bool = False) -> str:
    normalized = normalize_comment_text(text).lower()
    normalized = re.sub(r"[^\w\s]", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    prefix = "reply:" if is_reply else "top:"
    return f"{prefix}{normalized}" if normalized else ""


def partition_comment_entries(comment_entries: list[dict]) -> tuple[list[dict], list[dict]]:
    cleaned: list[dict] = []
    rejected: list[dict] = []
    aggregated: dict[str, dict] = {}
    for entry in comment_entries:
        if not isinstance(entry, dict):
            continue
        raw_text = clean_text(entry.get("raw_text") or entry.get("text"))
        normalized_text = normalize_comment_text(raw_text)
        reason = low_signal_reason(normalized_text)
        if reason:
            rejected.append({**entry, "text": normalized_text, "low_signal_reason": reason})
            continue
        is_reply = bool(entry.get("is_reply")) or clean_text(entry.get("sample_kind")).lower() == "reply"
        dedupe_key = canonical_comment_key(normalized_text, is_reply=is_reply)
        if not dedupe_key:
            rejected.append({**entry, "text": normalized_text, "low_signal_reason": "empty"})
            continue
        merged = aggregated.get(dedupe_key)
        if merged is None:
            merged = dict(entry)
            merged["text"] = normalized_text
            merged["quote_text"] = raw_text or normalized_text
            merged["canonical_text"] = dedupe_key
            merged["duplicate_count"] = 0
            merged["source_products"] = []
            merged["comment_languages"] = []
            merged["sample_kinds"] = []
            merged["is_reply"] = is_reply
            aggregated[dedupe_key] = merged
        merged["duplicate_count"] += 1
        if len(raw_text) > len(clean_text(merged.get("quote_text"))):
            merged["quote_text"] = raw_text
        merged["digg_count"] = max(safe_int(merged.get("digg_count")), safe_int(entry.get("digg_count")))
        merged["reply_comment_total"] = max(safe_int(merged.get("reply_comment_total")), safe_int(entry.get("reply_comment_total")))
        merged["author_verified"] = bool(merged.get("author_verified")) or bool(entry.get("author_verified"))
        merged["high_purchase_intent"] = bool(merged.get("high_purchase_intent")) or bool(entry.get("high_purchase_intent"))
        for key_name, field_name in [
            ("source_products", "source_product"),
            ("comment_languages", "comment_language"),
            ("sample_kinds", "sample_kind"),
        ]:
            value = clean_text(entry.get(field_name))
            if value and value not in merged[key_name]:
                merged[key_name].append(value)
        if not clean_text(merged.get("source_product")):
            merged["source_product"] = clean_text(entry.get("source_product"))
    cleaned = list(aggregated.values())
    for merged in cleaned:
        merged["theme"] = detect_theme(clean_text(merged.get("text")))
        merged["cluster_type"] = comment_cluster_type(merged["theme"])
        merged["price_band"] = estimate_price_band(" ".join([clean_text(merged.get("text")), clean_text(merged.get("reply_summary"))]))
        merged["reply_signal"] = synthesize_reply_signal(merged)
        merged["signal_tier"] = signal_tier_for_entry(merged)
        merged["source_product"] = short_list_text(merged.get("source_products", []), limit=3) or clean_text(merged.get("source_product"))
    cleaned.sort(
        key=lambda item: (
            {"high": 3, "medium": 2, "low": 1}.get(clean_text(item.get("signal_tier")), 0),
            safe_int(item.get("duplicate_count")),
            safe_int(item.get("digg_count")),
            safe_int(item.get("reply_comment_total")),
        ),
        reverse=True,
    )
    return cleaned, rejected


def clean_comment_entries(comment_entries: list[dict]) -> list[dict]:
    cleaned, _ = partition_comment_entries(comment_entries)
    return cleaned


def build_reply_chain_synthesis(cleaned: list[dict], limit: int = 6) -> list[dict]:
    grouped: dict[tuple[str, str], dict[str, Any]] = {}
    for entry in cleaned:
        video_id = clean_text(entry.get("video_id")) or "video-unknown"
        theme = clean_text(entry.get("theme")) or "一般反应"
        key = (video_id, theme)
        bucket = grouped.setdefault(
            key,
            {
                "video_id": video_id,
                "video_url": clean_text(entry.get("video_url")),
                "theme": theme,
                "cluster_type": clean_text(entry.get("cluster_type")),
                "source_product": clean_text(entry.get("source_product")),
                "reply_pressure": 0,
                "top_level_quotes": [],
                "reply_quotes": [],
                "member_count": 0,
            },
        )
        bucket["member_count"] += max(1, safe_int(entry.get("duplicate_count")))
        bucket["reply_pressure"] += safe_int(entry.get("reply_comment_total"))
        quote = clean_text(entry.get("quote_text") or entry.get("text"))
        if entry.get("is_reply"):
            bucket["reply_quotes"].append(quote)
        else:
            bucket["top_level_quotes"].append(quote)
        if safe_int(entry.get("reply_comment_total")) >= safe_int((bucket.get("anchor_entry") or {}).get("reply_comment_total")):
            bucket["anchor_entry"] = entry
    chains = list(grouped.values())
    chains = [chain for chain in chains if chain["reply_pressure"] >= 3 or chain["reply_quotes"]]
    chains.sort(key=lambda item: (safe_int(item.get("reply_pressure")), safe_int(item.get("member_count"))), reverse=True)
    for chain in chains:
        anchor = chain.get("anchor_entry") or {}
        chain["top_level_excerpt"] = sentence_clip((chain.get("top_level_quotes") or [""])[0], limit=96)
        chain["reply_excerpt"] = sentence_clip((chain.get("reply_quotes") or chain.get("top_level_quotes") or [""])[0], limit=96)
        chain["synthesis"] = synthesize_reply_signal(anchor if isinstance(anchor, dict) else {})
        chain["signal_role"] = clean_text(anchor.get("cluster_type")) if isinstance(anchor, dict) else clean_text(chain.get("cluster_type"))
    return chains[:limit]


def process_comment_pack(raw_entries: list[dict]) -> dict[str, Any]:
    cleaned, rejected = partition_comment_entries(raw_entries)
    chains = build_reply_chain_synthesis(cleaned)
    clusters = summarize_comment_clusters(cleaned)
    return {
        "cleaned": cleaned,
        "rejected": rejected,
        "reply_chains": chains,
        "stats": {
            "raw_count": len(raw_entries),
            "cleaned_count": len(cleaned),
            "rejected_count": len(rejected),
            "reply_chain_count": len(chains),
            "high_signal_count": sum(1 for item in cleaned if clean_text(item.get("signal_tier")) == "high"),
        },
        "snapshot": comment_signal_snapshot_from_cleaned(cleaned, chains),
    }


def comment_signal_snapshot_from_cleaned(cleaned: list[dict], chains: list[dict]) -> dict:
    clusters = summarize_comment_clusters(cleaned)
    reply_patterns = summarize_reply_patterns(cleaned)
    return {
        "cleaned_count": len(cleaned),
        "top_cluster": clusters[0] if clusters else None,
        "top_trust_cluster": strongest_cluster_by_type(clusters, "信任信号"),
        "top_complaint_cluster": strongest_cluster_by_type(clusters, "差评痛点"),
        "top_purchase_cluster": strongest_cluster_by_type(clusters, "购买因素"),
        "top_reply_pattern": reply_patterns[0] if reply_patterns else None,
        "top_reply_chain": chains[0] if chains else None,
    }


def comment_signal_snapshot(comment_entries: list[dict]) -> dict:
    pack = process_comment_pack(comment_entries)
    return pack["snapshot"]


def ensure_comment_pack_artifacts(capture_root: Path, raw_entries: list[dict]) -> dict[str, Any]:
    pack = process_comment_pack(raw_entries)
    if capture_root.exists():
        write_json_file(capture_root / "comments_cleaned.json", pack["cleaned"])
        write_json_file(capture_root / "comments_rejected.json", pack["rejected"])
        write_json_file(capture_root / "comment_reply_chains.json", pack["reply_chains"])
        write_json_file(capture_root / "comment_cleaning_stats.json", pack["stats"])
    return pack


def summarize_comment_clusters(comment_entries: list[dict]) -> list[dict]:
    grouped: dict[tuple[str, str], dict] = {}
    for entry in comment_entries:
        cluster_type = clean_text(entry.get("cluster_type")) or "一般"
        theme = clean_text(entry.get("theme")) or "一般反应"
        key = (cluster_type, theme)
        bucket = grouped.setdefault(
            key,
            {
                "cluster_type": cluster_type,
                "theme": theme,
                "count": 0,
                "top_entry": entry,
                "source_products": [],
                "price_bands": [],
                "reply_signals": [],
                "reply_pressure": 0,
                "duplicate_count": 0,
            },
        )
        bucket["count"] += max(1, safe_int(entry.get("duplicate_count")))
        bucket["duplicate_count"] += max(1, safe_int(entry.get("duplicate_count")))
        bucket["reply_pressure"] += safe_int(entry.get("reply_comment_total"))
        if safe_int(entry.get("digg_count")) > safe_int(bucket["top_entry"].get("digg_count")):
            bucket["top_entry"] = entry
        source_product = clean_text(entry.get("source_product"))
        if source_product and source_product not in bucket["source_products"]:
            bucket["source_products"].append(source_product)
        price_band = clean_text(entry.get("price_band"))
        if price_band and price_band not in bucket["price_bands"]:
            bucket["price_bands"].append(price_band)
        reply_signal = clean_text(entry.get("reply_signal"))
        if reply_signal and reply_signal not in bucket["reply_signals"]:
            bucket["reply_signals"].append(reply_signal)
    return sorted(
        grouped.values(),
        key=lambda item: (
            safe_int(item.get("count")),
            safe_int(item.get("reply_pressure")),
            safe_int(item["top_entry"].get("digg_count")),
        ),
        reverse=True,
    )


def strongest_cluster_by_type(comment_clusters: list[dict], cluster_type: str) -> dict | None:
    return next((cluster for cluster in comment_clusters if clean_text(cluster.get("cluster_type")) == cluster_type), None)


def build_comment_cluster_rows(comment_entries: list[dict]) -> list[list[str]]:
    rows: list[list[str]] = []
    for cluster in summarize_comment_clusters(clean_comment_entries(comment_entries))[:6]:
        entry = cluster["top_entry"]
        reply_pressure = safe_int(cluster.get("reply_pressure"))
        price_band = short_list_text(cluster.get("price_bands", []), limit=2) or "价格带待补"
        implication = {
            "AI 控制 / 隐私顾虑": "脚本里应直接回应用户控制权、退出阻力和信任问题。",
            "认证 / 可信度": "用户会快速公开地读取账号或创作者的可信度线索。",
            "售后 / 求助需求": "客服或评论区需要有快速响应这类问题的路径。",
            "平台自反应": "这类平台自指反应能带来互动，但不等于购买意图。",
            "关闭功能 / 用户控制": "用户需要更简单、直白的解决方式和指引。",
            "价格 / 性价比顾虑": "需要更强的价格框架、价值证明或预期管理。",
            "购买意向": "适合反哺 offer、FAQ 和转化角度设计。",
            "反复观看 / 愉悦感": "这类愉悦表述可以反哺开头钩子和留存语言。",
            "怀旧反应": "真正驱动反应的是识别感与记忆线索，而不只是功能解释。",
            "一般反应": "除非它持续重复出现且更具体，否则先视为弱信号。",
        }.get(cluster["theme"], "把这句重复出现的话翻译成可执行的运营或信息规则。")
        rows.append(
            [
                cluster["cluster_type"],
                sentence_clip(clean_text(entry.get("quote_text") or entry.get("text")), limit=120),
                short_list_text(cluster.get("source_products", []), limit=3) or clean_text(entry.get("source_product")) or "来源待补",
                (
                    f"{cluster['theme']} | 重复提及={cluster.get('count', 0)}"
                    f" | 回复压力={reply_pressure} | 价位={price_band}"
                    f" | 信号={clean_text(entry.get('signal_tier')) or 'medium'}"
                ),
                f"{implication} 回复链：{clean_text(entry.get('reply_signal')) or '未恢复出有意义的回复链信号'}",
            ]
        )
    return rows


def build_scene08_source_product_rows(comment_entries: list[dict]) -> list[list[str]]:
    rows: list[list[str]] = []
    grouped: dict[str, list[dict]] = {}
    for entry in comment_entries:
        product = clean_text(entry.get("source_product")) or "来源待补"
        grouped.setdefault(product, []).append(entry)
    for product, entries in sorted(grouped.items(), key=lambda item: len(item[1]), reverse=True)[:4]:
        product_clusters = summarize_comment_clusters(entries)
        purchase_cluster = strongest_cluster_by_type(product_clusters, "购买因素")
        complaint_cluster = strongest_cluster_by_type(product_clusters, "差评痛点")
        bands = [clean_text(entry.get("price_band")) for entry in entries if clean_text(entry.get("price_band")) and clean_text(entry.get("price_band")) != "不明确"]
        band = Counter(bands).most_common(1)[0][0] if bands else "不明确"
        purchase_text = (
            f"{clean_text(purchase_cluster.get('theme'))} | {sentence_clip(clean_text((purchase_cluster.get('top_entry') or {}).get('quote_text')), limit=72)}"
            if purchase_cluster
            else "未恢复出强购买触发点"
        )
        complaint_text = (
            f"{clean_text(complaint_cluster.get('theme'))} | {sentence_clip(clean_text((complaint_cluster.get('top_entry') or {}).get('quote_text')), limit=72)}"
            if complaint_cluster
            else "未恢复出强差评痛点簇"
        )
        rows.append([product, band, str(sum(max(1, safe_int(entry.get("duplicate_count"))) for entry in entries)), purchase_text, complaint_text])
    return rows


def build_scene08_price_band_rows(comment_entries: list[dict]) -> list[list[str]]:
    rows: list[list[str]] = []
    clusters = summarize_comment_clusters(comment_entries)
    for band in ["价格敏感", "偏高端", "不明确"]:
        band_entries = [entry for entry in comment_entries if clean_text(entry.get("price_band")) == band]
        if not band_entries and band != "不明确":
            rows.append([band, "未恢复出强重复驱动", "未恢复出强重复抱怨", "这个价格带还需要更多来源商品"])
            continue
        band_clusters = summarize_comment_clusters(band_entries) if band_entries else []
        purchase_cluster = strongest_cluster_by_type(band_clusters, "购买因素")
        complaint_cluster = strongest_cluster_by_type(band_clusters, "差评痛点")
        fallback_cluster = clusters[0] if clusters else None
        driver = clean_text((purchase_cluster or fallback_cluster or {}).get("theme")) or "未恢复出明确的重复驱动"
        complaint = clean_text((complaint_cluster or {}).get("theme")) or "未恢复出明确的重复抱怨"
        implication = {
            "价格敏感": "需要更轻的承诺语言、更强的价值证明或更简单的预期管理。",
            "偏高端": "需要更强的信任转移、差异化收益或高端证明语言。",
            "不明确": "当前样本更偏一般反应，价格分层还不够清晰。",
        }.get(band, "还需要更多按价格分层的商品样本。")
        rows.append([band, driver, complaint, implication])
    return rows


def scene08_reply_chain_line(pattern: dict | None) -> str:
    if not pattern:
        return "未恢复出强回复链压力。"
    theme = clean_text(pattern.get("theme")) or "一般反应"
    top_entry = pattern.get("top_entry") or pattern
    quote = sentence_clip(clean_text(top_entry.get("quote_text") or top_entry.get("text") or pattern.get("reply_excerpt")), limit=92)
    reply_pressure = safe_int(pattern.get("reply_pressure"))
    parts = [f"{theme} | 回复压力={reply_pressure}"]
    if quote:
        parts.append(quote)
    return " | ".join(parts)


def scene08_reply_chain_synthesis(chains_or_patterns: list[dict]) -> list[list[str]]:
    rows: list[list[str]] = []
    for item in chains_or_patterns[:4]:
        if clean_text(item.get("synthesis")):
            rows.append(
                [
                    clean_text(item.get("theme")) or "一般反应",
                    str(safe_int(item.get("reply_pressure"))),
                    clean_text(item.get("source_product")) or "来源待补",
                    sentence_clip(clean_text(item.get("reply_excerpt") or item.get("top_level_excerpt")), limit=96) or "回复链代表原话待补",
                    clean_text(item.get("synthesis")) or "未恢复出有意义的回复链信号",
                ]
            )
            continue
        top_entry = item.get("top_entry") or {}
        rows.append(
            [
                clean_text(item.get("theme")) or "一般反应",
                str(safe_int(item.get("reply_pressure"))),
                clean_text(top_entry.get("source_product")) or "来源待补",
                sentence_clip(clean_text(top_entry.get("quote_text") or top_entry.get("text")), limit=96) or "回复链代表原话待补",
                clean_text(top_entry.get("reply_signal")) or synthesize_reply_signal(top_entry),
            ]
        )
    return rows


def scene08_cluster_note(cluster: dict | None, fallback: str) -> str:
    if not cluster:
        return fallback
    theme = clean_text(cluster.get("theme"))
    quote = clean_text((cluster.get("top_entry") or {}).get("quote_text"))
    if theme and quote:
        return f"{theme}: {sentence_clip(quote, limit=88)}"
    if theme:
        return theme
    return fallback


def summarize_reply_patterns(comment_entries: list[dict]) -> list[dict]:
    patterns: dict[str, dict] = {}
    for entry in comment_entries:
        reply_total = safe_int(entry.get("reply_comment_total"))
        if reply_total < 3 and not clean_text(entry.get("reply_summary")):
            continue
        theme = clean_text(entry.get("theme")) or "一般反应"
        bucket = patterns.setdefault(
            theme,
            {"theme": theme, "count": 0, "reply_pressure": 0, "top_entry": entry},
        )
        bucket["count"] += max(1, safe_int(entry.get("duplicate_count")))
        bucket["reply_pressure"] += reply_total
        if reply_total > safe_int(bucket["top_entry"].get("reply_comment_total")):
            bucket["top_entry"] = entry
    return sorted(patterns.values(), key=lambda item: (safe_int(item.get("reply_pressure")), safe_int(item.get("count"))), reverse=True)
