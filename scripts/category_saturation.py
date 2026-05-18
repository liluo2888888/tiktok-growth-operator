from __future__ import annotations

from collections import Counter
from typing import Any

from text_normalization import normalize_text


def clean_text(value: object) -> str:
    return normalize_text(value)


def safe_int(value: object) -> int:
    if isinstance(value, bool):
        return int(value)
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def hook_key(video: dict) -> str:
    return clean_text(video.get("hook_text") or video.get("desc"))[:96].lower()


def creator_key(video: dict) -> str:
    return clean_text(video.get("unique_id") or video.get("author_unique_id") or video.get("nickname")).lower()


def estimate_category_saturation(videos: list[dict], comment_entries: list[dict] | None = None) -> dict[str, Any]:
    rows = [item for item in videos if isinstance(item, dict)]
    comment_entries = comment_entries or []
    total = len(rows)
    hooks = [hook_key(video) for video in rows if hook_key(video)]
    creators = [creator_key(video) for video in rows if creator_key(video)]
    hook_counts = Counter(hooks)
    creator_counts = Counter(creators)
    repeated_hook_share = (
        sum(count for count in hook_counts.values() if count >= 2) / len(hooks) if hooks else 0.0
    )
    top_creator_share = (creator_counts.most_common(1)[0][1] / total) if total and creator_counts else 0.0
    avg_score = sum(safe_int(item.get("score")) for item in rows) / total if total else 0.0
    avg_likes = sum(safe_int(item.get("digg_count")) for item in rows) / total if total else 0.0

    comment_themes = [
        clean_text(entry.get("theme"))
        for entry in comment_entries
        if clean_text(entry.get("theme")) and clean_text(entry.get("theme")) != "一般反应"
    ]
    theme_homogeneity = 0.0
    if comment_themes:
        top_theme_count = Counter(comment_themes).most_common(1)[0][1]
        theme_homogeneity = top_theme_count / len(comment_themes)

    demand_heat = "高" if avg_likes >= 1500 or avg_score >= 70 else "中" if avg_likes >= 400 or avg_score >= 40 else "低"
    supply_pressure = "高" if repeated_hook_share >= 0.35 or top_creator_share >= 0.45 else "中" if repeated_hook_share >= 0.2 else "低"

    if demand_heat in {"高", "中"} and supply_pressure == "高":
        verdict = "热但拥挤"
        verdict_en = "hot_but_crowded"
        action = "谨慎进入：需求还在，但包装与 hook 已明显收敛，需要更强差异化证明。"
    elif demand_heat in {"高", "中"} and supply_pressure != "高":
        verdict = "有空间"
        verdict_en = "promising_underserved"
        action = "值得进入：热度成立且供给尚未完全同质化，优先切证明物更强的进入版本。"
    elif demand_heat == "低":
        verdict = "暂不建议"
        verdict_en = "weak_not_worth_entering"
        action = "暂不建议重投入：当前样本热度偏弱，先补更多关键词与评论样本再判断。"
    else:
        verdict = "观察"
        verdict_en = "watch"
        action = "先小流量验证：需求中等、供给压力未完全释放，不要一次性铺开。"

    return {
        "demand_heat": demand_heat,
        "supply_pressure": supply_pressure,
        "verdict": verdict,
        "verdict_code": verdict_en,
        "recommended_action": action,
        "signals": {
            "sample_count": total,
            "avg_score": round(avg_score, 1),
            "avg_likes": round(avg_likes, 1),
            "repeated_hook_share": round(repeated_hook_share, 2),
            "top_creator_share": round(top_creator_share, 2),
            "comment_theme_homogeneity": round(theme_homogeneity, 2),
            "comment_sample_count": len(comment_entries),
        },
    }


def category_saturation_rows(assessment: dict) -> list[list[str]]:
    signals = assessment.get("signals") or {}
    return [
        ["需求热度", assessment.get("demand_heat", "中"), f"均赞={signals.get('avg_likes')} / 均分={signals.get('avg_score')}", "中"],
        ["供给拥挤度", assessment.get("supply_pressure", "中"), f"重复 hook 占比={signals.get('repeated_hook_share')} / 头部账号占比={signals.get('top_creator_share')}", "中"],
        ["评论同质化", "高" if float(signals.get("comment_theme_homogeneity") or 0) >= 0.45 else "低", f"主题集中度={signals.get('comment_theme_homogeneity')}", "中"],
        ["进入判断", assessment.get("verdict", "观察"), assessment.get("recommended_action", ""), "高"],
    ]


def category_entry_decision_rows(assessment: dict) -> list[list[str]]:
    verdict = clean_text(assessment.get("verdict"))
    mapping = {
        "热但拥挤": ["做", "谨慎做", "需要更强差异化 proof，不要复制壳"],
        "有空间": ["优先做", "可以做", "先切证明物更强的进入版本"],
        "暂不建议": ["不做", "暂不做", "先补采样与评论证据"],
        "观察": ["观察", "小流量试", "先验证再决定是否加码"],
    }
    do, tone, note = mapping.get(verdict, ["观察", "小流量试", "先验证再决定"])
    return [
        [do, tone, assessment.get("recommended_action", ""), note],
    ]
