from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

from generate_scene_report import build_report_payload, load_catalog, resolve_scene


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
    return json.loads(path.read_text(encoding="utf-8-sig"))


def clean_text(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        parts = [clean_text(item) for item in value]
        return "\n".join(item for item in parts if item)
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False)
    return str(value).replace("\r\n", "\n").strip()


def maybe_load(path: Path) -> dict | list | None:
    return load_json(path) if path.exists() else None


def maybe_read_text(path: Path) -> str | None:
    return path.read_text(encoding="utf-8-sig") if path.exists() else None


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

    return (
        aggregate_summary if isinstance(aggregate_summary, dict) else {},
        profile_summary if isinstance(profile_summary, dict) else {},
        ranked_videos if isinstance(ranked_videos, list) else [],
        qualified_videos if isinstance(qualified_videos, list) else [],
    )


def top_videos(videos: list[dict], limit: int = 5) -> list[dict]:
    return videos[:limit]


def video_line(video: dict) -> str:
    return (
        f"{clean_text(video.get('video_url'))} | likes={video.get('digg_count', 0)} "
        f"comments={video.get('comment_count', 0)} shares={video.get('share_count', 0)} "
        f"plays={video.get('play_count', 0)}"
    )


def make_context(
    capture_root: Path,
    aggregate_summary: dict,
    profile_summary: dict,
    ranked_videos: list[dict],
    qualified_videos: list[dict],
) -> str:
    lines = [
        f"Real TikTok capture-pack import from {capture_root}.",
        f"Profile URL: {clean_text(profile_summary.get('profile_url'))}",
        f"Platform: TikTok",
        f"Session quality: {clean_text(profile_summary.get('session_quality'))}",
        f"Ranked count: {aggregate_summary.get('aggregated_ranked_count', aggregate_summary.get('ranked_video_count', 0))}",
        f"Qualified count: {aggregate_summary.get('aggregated_qualified_count', aggregate_summary.get('qualified_video_count', 0))}",
        f"Min likes threshold: {aggregate_summary.get('min_likes', aggregate_summary.get('min_likes_threshold', ''))}",
    ]
    if ranked_videos:
        top = ranked_videos[0]
        lines.append(f"Top ranked video: {video_line(top)}")
        lines.append(f"Top ranked hook/caption: {clean_text(top.get('desc'))}")
    if qualified_videos:
        lines.append(f"Qualified winner: {video_line(qualified_videos[0])}")
    return "\n".join(line for line in lines if line)


def build_evidence(capture_root: Path, aggregate_summary: dict, profile_summary: dict, ranked_videos: list[dict]) -> list[dict]:
    summary_source = capture_root / ("aggregate_summary.json" if (capture_root / "aggregate_summary.json").exists() else "summary.json")
    profile_source = capture_root / ("profile_summary.json" if (capture_root / "profile_summary.json").exists() else "summary.json")
    evidence = [
        {
            "label": "Summary",
            "detail": (
                f"ranked={aggregate_summary.get('aggregated_ranked_count', aggregate_summary.get('ranked_video_count', 0))}; "
                f"qualified={aggregate_summary.get('aggregated_qualified_count', aggregate_summary.get('qualified_video_count', 0))}; "
                f"min_likes={aggregate_summary.get('min_likes', aggregate_summary.get('min_likes_threshold', ''))}"
            ),
            "source": str(summary_source),
        },
        {
            "label": "Profile summary",
            "detail": (
                f"profile={clean_text(profile_summary.get('profile_url') or profile_summary.get('profile_final_url'))}; "
                f"session={clean_text(profile_summary.get('session_quality'))}; "
                f"ranked={profile_summary.get('ranked_video_count', 0)}"
            ),
            "source": str(profile_source),
        },
    ]
    for video in top_videos(ranked_videos, limit=3):
        evidence.append(
            {
                "label": f"Ranked video {video.get('video_id', '')}",
                "detail": clean_text(video.get("desc")) or video_line(video),
                "source": clean_text(video.get("video_url")),
            }
        )
    return evidence


def build_assets(capture_root: Path) -> list[dict]:
    assets: list[dict] = []
    for name, note in [
        ("aggregate_report.md", "Aggregate markdown report from the real TikTok capture pack."),
        ("aggregate_analysis.xlsx", "Aggregate workbook from the real TikTok capture pack."),
        ("aggregate_ranked_videos.xlsx", "Ranked-video workbook."),
        ("aggregate_qualified_videos.xlsx", "Qualified-video workbook."),
        ("ranked_videos.xlsx", "Ranked-video workbook from the single TikTok capture pack."),
        ("comments_flat.csv", "Flattened comment export from the single TikTok capture pack."),
    ]:
        path = first_existing_path(capture_root, [name])
        if path:
            assets.append({"label": name, "path": str(path), "note": note})
    return assets


def collect_comment_entries(capture_root: Path) -> list[dict]:
    entries: list[dict] = []
    comments_sampled = maybe_load(capture_root / "comments_sampled.json") or []
    if isinstance(comments_sampled, list):
        for video in comments_sampled:
            samples = video.get("samples", []) or []
            for sample in samples:
                entries.append(
                    {
                        "video_id": clean_text(video.get("video_id")),
                        "video_url": clean_text(video.get("video_url")),
                        "text": clean_text(sample.get("text")),
                        "digg_count": sample.get("digg_count", 0),
                        "nickname": clean_text(sample.get("nickname")),
                        "unique_id": clean_text(sample.get("unique_id")),
                    }
                )
    return entries


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


def detect_theme(text: str) -> str:
    lowered = text.lower()
    if "ai remix" in lowered or "ai " in lowered:
        return "AI control / privacy concern"
    if "verified" in lowered or "verification" in lowered:
        return "verification / credibility"
    if "support" in lowered:
        return "support / help request"
    if "watching tiktok on tiktok" in lowered or "tiktok posting on tiktok" in lowered:
        return "meta platform reaction"
    if "turn off" in lowered or "opt out" in lowered or "remove" in lowered:
        return "feature removal / user control"
    return "general reaction"


def build_comment_cluster_rows(comment_entries: list[dict]) -> list[list[str]]:
    rows: list[list[str]] = []
    added: set[str] = set()
    for entry in comment_entries:
        text = entry["text"]
        if not text:
            continue
        theme = detect_theme(text)
        if theme in added:
            continue
        added.add(theme)
        implication = {
            "AI control / privacy concern": "Live scripts should address user control, opt-out friction, and trust directly.",
            "verification / credibility": "Viewers are reading account or creator credibility cues quickly and publicly.",
            "support / help request": "Moderation needs a fast path for support-seeking questions.",
            "meta platform reaction": "Meta/self-referential reactions can drive engagement but do not equal buyer intent.",
            "feature removal / user control": "Users want a simple fix and plain-language instructions.",
            "general reaction": "Treat as weak signal unless repeated with stronger specificity.",
        }.get(theme, "Translate the repeated phrase into a moderation or messaging rule.")
        rows.append(
            [
                "Complaint" if "concern" in theme.lower() or "removal" in theme.lower() else "Trust signal",
                text[:120],
                theme,
                implication,
            ]
        )
        if len(rows) >= 5:
            break
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
            clean_text(top_ref.get("video_url")) or "Top candidate list",
        ],
        [
            "Shortlist",
            clean_text(top_ref.get("desc"))[:90],
            "Prioritize the post with the clearest hook, proof cue, and soft continuation CTA",
            "1-3 replication-worthy references",
        ],
        [
            "Teardown",
            clean_text(second_ref.get("video_url")) or clean_text(top_ref.get("video_url")),
            "Separate transferable hook/pacing logic from official-account or celebrity lift",
            "Reference notes by hook, proof, and CTA",
        ],
        [
            "Replication brief",
            clean_text(top_ref.get("desc"))[:90],
            "Preserve the first-frame promise but swap in owned proof, creator, or product angle",
            "2-3 adapted creative directions",
        ],
        [
            "Production queue",
            clean_text(third_ref.get("video_url")) or clean_text(top_ref.get("video_url")),
            "Ship the clearest recognition-first variant first, then test one alternate proof device",
            "Prioritized weekly test queue",
        ],
    ]


def build_scene_11_learning_rows(references: list[dict]) -> list[list[str]]:
    top_ref = references[0] if references else {}
    return [
        [
            "Which recognition-first hook is portable without official-account lift?",
            "This decides whether the format is usable outside the original TikTok account.",
            f"Compare first 3 seconds hold and engagement on the adaptation of {clean_text(top_ref.get('video_id')) or 'the top post'}.",
        ],
        [
            "How much proof is needed when platform authority is weaker?",
            "Smaller accounts need stronger owned proof to preserve trust.",
            "Track save/share/comment quality across proof-light versus proof-heavy variants.",
        ],
        [
            "What weekly volume can one operator sustain?",
            "A replication pipeline only matters if it is actually repeatable.",
            "Count candidates sourced, teardowns finished, and briefs shipped per cycle.",
        ],
    ]


def build_scene_12_invariant_rows(references: list[dict]) -> list[list[str]]:
    top_ref = references[0] if references else {}
    return [
        ["Core message", "Lead with a recognition-first editorial promise before explanation."],
        ["Product truth", "Replace official-account trust with one owned proof object, creator, or use case."],
        ["Target outcome", f"Turn the top reference format ({clean_text(top_ref.get('video_url')) or 'top ranked post'}) into 4 testable variants."],
    ]


def build_scene_12_style_rows(references: list[dict]) -> list[list[str]]:
    rows: list[list[str]] = []
    for index, video in enumerate(references[:4], start=1):
        desc = clean_text(video.get("desc"))
        rows.append(
            [
                style_label(index, video),
                classify_audience_lens(video),
                desc[:90] or f"Reference hook {index}",
                "Owned proof object or collaborator trust replacing official-account authority",
                "Short editorial framing with fast first-frame recognition",
                "Soft continuation CTA toward next watch, save, or profile action",
                f"Based on ranked TikTok reference {clean_text(video.get('video_id')) or index}",
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
            ]
        )
    while len(rows) < 4:
        index = len(rows) + 1
        rows.append([f"Style {index}", "Needs product-specific hypothesis", "Needs success signal"])
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


def fill_common(payload: dict, project: str, context: str, capture_root: Path, aggregate_summary: dict, profile_summary: dict, ranked_videos: list[dict], qualified_videos: list[dict]) -> None:
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
        f"Capture root: {capture_root}",
    ]
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
    payload["sources"] = list(dict.fromkeys(payload.get("sources", []) + [
        str(capture_root / ("aggregate_summary.json" if (capture_root / "aggregate_summary.json").exists() else "summary.json")),
        str(capture_root / ("aggregate_ranked_videos.json" if (capture_root / "aggregate_ranked_videos.json").exists() else "ranked_videos.json")),
        clean_text(profile_summary.get("profile_url") or profile_summary.get("profile_final_url")),
    ]))


def fill_scene_03(payload: dict, ranked_videos: list[dict], qualified_videos: list[dict], aggregate_summary: dict) -> None:
    sections = {section["heading"]: section for section in payload["sections"]}
    top_ranked = top_videos(ranked_videos, limit=3)
    winner = qualified_videos[0] if qualified_videos else (top_ranked[0] if top_ranked else {})

    payload["executive_summary"]["conclusion"] = (
        "The strongest TikTok posts in this pack win by pairing emotionally legible captions with platform-native cultural context and proven account authority."
    )
    payload["executive_summary"]["why_it_matters"] = (
        "This pack is useful for studying how TikTok account-level editorial packaging and creator-feature framing drive strong ranking signals."
    )
    payload["executive_summary"]["next_action"] = (
        "Adapt the top-ranked format into 2-3 new variants that preserve the emotional promise but swap in the user's own proof object or featured creator."
    )
    payload["executive_summary"]["confidence"] = "medium"

    sections["Executive Conclusion"]["paragraphs"] = [
        payload["executive_summary"]["conclusion"],
        f"Qualified winners in pack: {aggregate_summary.get('aggregated_qualified_count', 0)}",
    ]
    sections["Executive Conclusion"]["bullets"] = [
        "High-performing posts are not generic account updates; they frame a recognizable person, feeling, or cultural moment.",
        "The top post also shows that account trust plus simple, emotionally clear copy can scale strongly without long explanation.",
    ]

    shortlist_rows = []
    for index, video in enumerate(top_ranked, start=1):
        shortlist_rows.append(
            [
                str(index),
                clean_text(video.get("video_url")),
                clean_text(video.get("desc"))[:100],
                f"likes={video.get('digg_count', 0)} / comments={video.get('comment_count', 0)} / shares={video.get('share_count', 0)}",
                "Editorial/cultural framing",
                "Top score in the capture pack",
            ]
        )
    sections["Structure Logic"]["table"]["rows"] = shortlist_rows

    per_video_rows = []
    for video in top_ranked:
        per_video_rows.append(
            [
                clean_text(video.get("video_id")),
                clean_text(video.get("desc"))[:80],
                "Short caption-led emotional or cultural cue",
                "Account trust / featured talent / cultural relevance",
                "Drive watch, affinity, and follow-on interest",
                "Use emotion-first packaging with visible proof object",
            ]
        )
    sections["Core Mechanism"]["table"]["rows"] = per_video_rows

    sections["Reusable Formula"]["table"]["rows"] = [
        ["Hook", "Lead with a human or emotional cue the viewer instantly recognizes", "Keep the emotional premise but change the featured object or person", "Do not open with generic brand setup"],
        ["Proof", "Use profile authority or featured talent as built-in proof", "Replace account authority with a concrete proof asset the user owns", "Weak proof will collapse the same format"],
        ["Packaging", "Keep copy short and culturally legible", "Reduce explanation and let the premise do more work", "Over-explaining makes the format flatter"],
        ["CTA", "Soft continuation CTA or tease of full episode / more content", "Ask for the next click or next watch, not a hard sell", "Hard conversion CTA may break fit"],
    ]

    sections["Risks And Adaptation Notes"]["bullets"] = [
        "A large official TikTok account has built-in trust and distribution that do not transfer cleanly.",
        "This pack lacks sampled comments, so audience-language conclusions should stay weakly held.",
    ]
    sections["Next Action"]["numbered"] = [
        "Choose the top-ranked post as the main reference format.",
        "Write two adaptations: one creator-featured and one proof-object-featured.",
        "Test whether short emotional packaging still works when account authority is lower.",
    ]


def fill_scene_17(payload: dict, ranked_videos: list[dict], profile_summary: dict) -> None:
    sections = {section["heading"]: section for section in payload["sections"]}
    top_ranked = top_videos(ranked_videos, limit=4)

    payload["executive_summary"]["conclusion"] = (
        "This TikTok account sample suggests a repeatable editorial formula: attach the post to a recognizable creator, story, or cultural moment, then use minimal copy to let affinity do the work."
    )
    payload["executive_summary"]["why_it_matters"] = (
        "The pattern is useful for TikTok projects that need stronger social-native packaging without long explanation-heavy intros."
    )
    payload["executive_summary"]["next_action"] = (
        "Translate the account's strongest editorial packaging moves into a reusable creator- or community-led content brief."
    )
    payload["executive_summary"]["confidence"] = "medium"

    sections["Executive Conclusion"]["paragraphs"] = [
        payload["executive_summary"]["conclusion"],
        f"Profile session quality: {clean_text(profile_summary.get('session_quality'))}",
    ]

    rows = [
        ["Hook formula", "Human-first, emotion-first, or culture-first caption packaging", clean_text(top_ranked[0].get("desc")) if top_ranked else ""],
        ["Visual rhythm", "Likely dependent on featured creator/performance clip rather than explanation-led structure", clean_text(top_ranked[1].get("desc")) if len(top_ranked) > 1 else ""],
        ["Proof style", "Trust rides on official account authority, featured people, and recognizable context", clean_text(top_ranked[2].get("desc")) if len(top_ranked) > 2 else ""],
        ["CTA style", "Soft teaser or continuation toward more content", clean_text(top_ranked[3].get("desc")) if len(top_ranked) > 3 else ""],
    ]
    sections["Structure Logic"]["table"]["rows"] = rows

    sections["Core Mechanism"]["paragraphs"] = [
        "The account does not need to over-explain. It packages a familiar person or cultural cue and relies on fast recognition plus account trust.",
        "The transferable lesson is not 'be TikTok'. It is to reduce friction between first-frame recognition and the emotional reason to keep watching.",
    ]

    sections["Reusable Formula"]["table"]["rows"] = [
        ["Hook", "Open with immediate recognition or emotional clarity", "Recognition compresses decision time on TikTok", "Swap in a figure, object, or cue your audience already cares about"],
        ["Pacing", "Stay short and premise-led", "The format works because it does not over-teach", "Strip excess setup before the main cue lands"],
        ["Trust-building", "Borrow trust from the account, featured talent, or event context", "Trust can be transferred via stronger proof objects", "Use receipts, social proof, or known collaborators if account authority is weaker"],
        ["Conversion move", "Use continuation energy instead of hard closing", "Soft progression fits social-native viewing better", "Route toward next watch, next profile action, or soft save/share"],
    ]

    sections["Risks And Adaptation Notes"]["table"]["rows"] = [
        ["Official-account authority", "A large platform account has built-in distribution and credibility most projects do not have."],
        ["Featured-talent lift", "Recognition from known creators or cultural moments may be doing part of the ranking work."],
        ["Missing comments", "Without sampled comments, true audience-language resonance is under-evidenced in this import."],
    ]
    sections["Next Action"]["numbered"] = [
        "Pick one top-ranked post and rewrite it for a smaller account with a stronger proof object.",
        "Test one version led by a person and one version led by a moment or outcome.",
        "Measure whether lighter copy plus faster recognition improves early engagement.",
    ]


def fill_scene_08(payload: dict, capture_root: Path, ranked_videos: list[dict]) -> None:
    sections = {section["heading"]: section for section in payload["sections"]}
    comment_entries = collect_comment_entries(capture_root)
    sampled_video_count = len({entry["video_id"] for entry in comment_entries if entry["video_id"]})
    top_texts = [entry["text"] for entry in comment_entries if entry["text"]][:6]

    payload["executive_summary"]["conclusion"] = (
        "The strongest repeated user language in this TikTok comment pack is not purchase desire but control, trust, and feature-friction concern, especially around AI remix settings."
    )
    payload["executive_summary"]["why_it_matters"] = (
        "This matters because live moderation and content framing need to answer user-control anxiety directly instead of only promoting the post theme."
    )
    payload["executive_summary"]["next_action"] = (
        "Use the repeated complaint language to build moderator replies, host clarification prompts, and a cleaner user-control explanation path."
    )
    payload["executive_summary"]["confidence"] = "medium"

    sections["Executive Conclusion"]["paragraphs"] = [
        payload["executive_summary"]["conclusion"],
        f"Comment samples were captured from {sampled_video_count} TikTok videos in this pack.",
    ]

    sections["High-Level Judgment"]["paragraphs"] = [
        "The dominant live-ops lesson is that users surface platform-control complaints in public comment threads even when the post itself is not primarily about that feature."
    ]
    sections["High-Level Judgment"]["bullets"] = [
        "Most repeated pain: inability to easily disable or opt out of AI remix behavior.",
        "Most repeated trigger: visible mismatch between what users think they consented to and what the platform enabled by default.",
    ]

    sections["Evidence Clusters"]["table"]["rows"] = build_comment_cluster_rows(comment_entries)

    sections["Recommended Action"]["table"]["rows"] = [
        ["Product direction", "Explain feature control in plainer language and reduce opt-out friction in user-facing guidance.", "Repeated comments ask how to disable or remove AI remix."],
        ["Offer / positioning", "Lead with control and transparency before reassurance.", "Trust is weakened when users feel settings changed without consent."],
        ["Script language", "Reuse user phrases like 'turn off', 'opt out', and 'remove AI remix'.", "Direct language will match what users are already typing."],
        ["Proof content", "Show exact steps or visible UI proof when answering control questions.", "Trust objections need concrete resolution, not only tone."],
    ]

    sections["Open Questions"]["bullets"] = [
        "Sampled comments exist for only part of the ranked set, so these findings are provisional rather than category-complete.",
        "The pack is centered on TikTok's own account, so some complaints may reflect platform-policy sentiment more than content-category demand.",
    ]

    payload["notes"] = list(dict.fromkeys(payload.get("notes", []) + top_texts))


def fill_scene_18(payload: dict, ranked_videos: list[dict], profile_summary: dict) -> None:
    sections = {section["heading"]: section for section in payload["sections"]}
    top_ranked = top_videos(ranked_videos, limit=3)
    profile_url = clean_text(profile_summary.get("profile_url") or profile_summary.get("profile_final_url"))

    payload["executive_summary"]["conclusion"] = (
        "This TikTok capture pack establishes a usable weekly competitor-account baseline: the account is winning with a small number of editorially packaged, emotion-first or culture-first posts."
    )
    payload["executive_summary"]["why_it_matters"] = (
        "Even one weekly baseline is enough to decide what kind of post packaging deserves continued tracking versus what is just account noise."
    )
    payload["executive_summary"]["next_action"] = (
        "Use this pack as the baseline week, then compare the next capture against the same account fields to spot packaging or performance shifts."
    )
    payload["executive_summary"]["confidence"] = "medium"

    sections["Executive Conclusion"]["paragraphs"] = [
        payload["executive_summary"]["conclusion"],
        f"Account baseline: {profile_url}",
    ]

    summary_row = [
        profile_url or "TikTok account",
        str(profile_summary.get("ranked_video_count", len(ranked_videos))),
        clean_text(top_ranked[0].get("video_url")) if top_ranked else "",
        clean_text(top_ranked[0].get("desc"))[:80] if top_ranked else "",
        f"Top score={top_ranked[0].get('score', 0)}" if top_ranked else "",
        "Baseline week only",
    ]
    sections["Objects To Track"]["table"]["rows"] = [summary_row]

    shift_rows = []
    for video in top_ranked:
        shift_rows.append(
            [
                "Emotion-first / culture-first editorial packaging",
                clean_text(video.get("video_id")),
                f"likes={video.get('digg_count', 0)} comments={video.get('comment_count', 0)} shares={video.get('share_count', 0)}",
                "Worth monitoring again next week for repetition or drift",
            ]
        )
    sections["Why They Matter"]["table"]["rows"] = shift_rows[:3]

    sections["Fields To Capture Next Time"]["bullets"] = [
        "Capture a second week from the same account so shifts can be compared against a real baseline.",
        "Add comment-sample availability and featured-person tags per post.",
        "Preserve cover/headline evidence if the account changes packaging style.",
    ]

    sections["Next Action"]["table"]["rows"] = [
        ["Watch", "Track whether the same account keeps using person-led or culture-led packaging", "High"],
        ["Test", "Try one smaller-account version with the same editorial framing but stronger owned proof", "High"],
        ["Ignore", "Do not overlearn official-account distribution effects as if they were universal", "Medium"],
    ]


def fill_scene_19(payload: dict, ranked_videos: list[dict], profile_summary: dict) -> None:
    sections = {section["heading"]: section for section in payload["sections"]}
    top_ranked = top_videos(ranked_videos, limit=4)

    payload["executive_summary"]["conclusion"] = (
        "Within this TikTok account sample, the likely winning pattern is short, editorially framed posts that attach to a recognizable person, story, or moment instead of leading with heavy explanation."
    )
    payload["executive_summary"]["why_it_matters"] = (
        "This is useful as a retro template because it converts raw ranked-post data into do-more, do-less, and next-test rules for the next cycle."
    )
    payload["executive_summary"]["next_action"] = (
        "Cluster the next account batch around people-led, moment-led, and explanation-led posts to confirm which packaging family deserves more volume."
    )
    payload["executive_summary"]["confidence"] = "medium"

    sections["Executive Conclusion"]["paragraphs"] = [
        payload["executive_summary"]["conclusion"],
        f"Current ranked post count in pack: {profile_summary.get('ranked_video_count', len(ranked_videos))}",
    ]

    sections["High-Level Judgment"]["table"]["rows"] = [
        ["Winning pattern", "Short editorial packaging around a person or moment", "Higher-ranked posts lean on immediate recognition and lighter copy"],
        ["Losing pattern", "Over-explanation or weak proof object", "Not directly visible here, but implied by what the top set is not doing"],
        ["Unclear pattern", "Whether comment-heavy posts outperform because of controversy or because of account trust", "Needs more weeks and more comment-linked evidence"],
    ]

    cluster_rows = []
    for video in top_ranked:
        cluster_rows.append(
            [
                "People / moment-led",
                clean_text(video.get("video_url")),
                clean_text(video.get("desc"))[:90],
                f"score={video.get('score', 0)}",
            ]
        )
    sections["Evidence Clusters"]["table"]["rows"] = cluster_rows[:4]

    sections["Recommended Action"]["table"]["rows"] = [
        ["Do more", "Lead with quicker recognition and lighter caption packaging", "Top posts show recognition-first framing"],
        ["Do less", "Reduce explanation-heavy intros that delay the emotional or social cue", "The winning set moves faster into the premise"],
        ["Stop", "Stop assuming platform-account authority will transfer unchanged to smaller accounts", "Official-account lift is not portable"],
        ["Test next", "Run a controlled comparison between person-led and proof-object-led versions", "This will separate authority effects from packaging effects"],
    ]

    sections["Open Questions"]["bullets"] = [
        "A true retro on the user's own account would need multiple internal batches, not only competitor data.",
        "This imported retro is best treated as a pattern template, not as a final verdict on a different account's strategy.",
    ]


def fill_scene_01(payload: dict, ranked_videos: list[dict]) -> None:
    sections = {section["heading"]: section for section in payload["sections"]}
    top_ranked = top_videos(ranked_videos, limit=5)

    payload["executive_summary"]["conclusion"] = (
        "This capture pack already contains a usable shortlist of TikTok posts worth deeper study because they combine strong ranking signals with clearly identifiable editorial packaging."
    )
    payload["executive_summary"]["why_it_matters"] = (
        "The board can be used as a repeatable intake layer before deeper teardown or adaptation work."
    )
    payload["executive_summary"]["next_action"] = (
        "Take the top three into deeper teardown and tag each by hook, proof, or creator-pattern reuse value."
    )
    payload["executive_summary"]["confidence"] = "medium"

    sections["Executive Conclusion"]["paragraphs"] = [
        payload["executive_summary"]["conclusion"],
    ]
    sections["Executive Conclusion"]["bullets"] = [
        "These are not just top-view posts; they are ranked candidates with reusable packaging traits.",
        "The best shortlist items should be routed by reuse value, not only raw numbers.",
    ]

    rows = []
    for index, video in enumerate(top_ranked, start=1):
        rows.append(
            [
                str(index),
                clean_text(video.get("video_url")),
                clean_text(video.get("desc"))[:60],
                f"likes={video.get('digg_count', 0)} comments={video.get('comment_count', 0)} shares={video.get('share_count', 0)}",
                "Hook / packaging study",
                "Strong score and clean editorial premise",
            ]
        )
    sections["Objects To Track"]["table"]["rows"] = rows

    sections["Why They Matter"]["table"]["rows"] = [
        [
            clean_text(video.get("video_id")),
            "Strong first-frame recognition or emotional cue",
            "Official account trust or recognizable cultural/person-led premise",
            "Use for next teardown stage",
        ]
        for video in top_ranked[:3]
    ]

    sections["Fields To Capture Next Time"]["table"]["rows"] = [
        ["Video link", "Traceability into later teardown", "Yes"],
        ["Caption / hook text", "Preserve the exact framing language", "Yes"],
        ["Likes/comments/shares", "Compare performance shape, not just views", "Yes"],
        ["Featured person or object", "Separate authority from packaging", "Yes"],
        ["Comment sample availability", "Route into scene 08 if present", "Yes"],
    ]

    sections["Next Action"]["numbered"] = [
        "Tag each shortlisted post by whether it is strongest for hook, proof, or creator-pattern study.",
        "Move the top 1-3 items into scene 03 or scene 17.",
        "Preserve this shortlist as the evidence board for later comparisons.",
    ]


def fill_scene_07(payload: dict, ranked_videos: list[dict], comment_entries: list[dict]) -> None:
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
        payload["executive_summary"]["conclusion"],
    ]
    sections["High-Level Judgment"]["table"]["rows"] = [
        ["Demand signal", "People- and moment-led posts still rank strongly", "The category rewards immediate social recognition"],
        ["Saturation signal", "Official-account advantage is significant", "Copying the shell alone will not be enough"],
        ["Opportunity", "Smaller accounts can compete if they replace platform authority with stronger owned proof", "Opportunity exists but requires sharper proof packaging"],
    ]

    sections["Evidence Clusters"]["table"]["rows"] = [
        [
            "High-recognition editorial packaging",
            clean_text(video.get("video_url")),
            clean_text(video.get("desc"))[:80],
            f"score={video.get('score', 0)}",
        ]
        for video in top_ranked[:3]
    ]

    sections["Recommended Action"]["table"]["rows"] = [
        ["Enter", "Use person-led or strong moment-led framing if you have a credible proof object", "The category responds to fast recognition"],
        ["Avoid", "Avoid explanation-first packaging unless your authority is unusually strong", "The visible winners move faster into the premise"],
        ["Test", "Compare person-led versus proof-object-led versions", "This separates social recognition from pure utility appeal"],
    ]

    sections["Open Questions"]["bullets"] = [
        "A fuller market-insight call would need more than one account and more than one capture window.",
        f"Comment-sample count available in this pack: {len(comment_entries)}.",
    ]


def fill_scene_09(payload: dict, ranked_videos: list[dict], qualified_videos: list[dict]) -> None:
    sections = {section["heading"]: section for section in payload["sections"]}
    source = qualified_videos[0] if qualified_videos else (top_videos(ranked_videos, limit=1)[0] if ranked_videos else {})
    source_url = clean_text(source.get("video_url"))
    source_desc = clean_text(source.get("desc"))

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
        ["Hook", source_desc[:90], "Swap in your own recognizable cue or outcome in the first frame"],
        ["Problem framing", "Low-friction, premise-first", "Do not over-explain before the viewer understands why the post matters"],
        ["Proof device", "Account authority / featured person / context", "Replace platform authority with owned proof or collaborator trust"],
        ["CTA", "Soft continuation toward more content", "Ask for the next watch or save, not a hard sales jump"],
    ]

    sections["Structure"]["numbered"] = [
        "Open with the clearest recognizable person, object, or emotional cue.",
        "Compress the explanation so the post stays premise-led.",
        "Add one trust anchor or proof object before the soft close.",
        "Close with a continuation move rather than a heavy conversion push.",
    ]

    sections["Creative Constraints"]["bullets"] = [
        "Do not copy official-account authority cues literally.",
        "Do not replace the simple premise with a dense explainer.",
        "Keep the adapted version TikTok-native and socially legible.",
    ]

    sections["Next Action"]["paragraphs"] = [
        "Write two adapted versions: one with a person-led hook and one with a proof-object-led hook.",
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
        f"Source account baseline: {profile_url}",
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

    sections["What To Learn"]["table"]["rows"] = build_scene_12_learning_matrix(references)

    sections["Next Action"]["numbered"] = [
        "Choose one owned product and one owned proof asset before shooting.",
        "Launch the top two style families first, then keep the other two as contrast tests.",
        "Record which variant wins on hold, saves, and comment quality before expanding volume.",
    ]


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
    fill_common(payload, project, context, capture_root, aggregate_summary, profile_summary, ranked_videos, qualified_videos)
    target_markets = parse_target_markets(args.target_markets)
    target_languages = parse_target_languages(args.target_languages)
    if scene["id"] == "15" and not target_languages:
        raise SystemExit("Scene 15 capture-pack import requires --target-languages with one or more explicit target languages.")

    if scene["id"] == "01":
        fill_scene_01(payload, ranked_videos)
    elif scene["id"] == "03":
        fill_scene_03(payload, ranked_videos, qualified_videos, aggregate_summary)
    elif scene["id"] == "07":
        fill_scene_07(payload, ranked_videos, comment_entries)
    elif scene["id"] == "08":
        fill_scene_08(payload, capture_root, ranked_videos)
    elif scene["id"] == "09":
        fill_scene_09(payload, ranked_videos, qualified_videos)
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
        fill_scene_18(payload, ranked_videos, profile_summary)
    elif scene["id"] == "19":
        fill_scene_19(payload, ranked_videos, profile_summary)
    elif scene["id"] == "17":
        fill_scene_17(payload, ranked_videos, profile_summary)
    else:
        raise SystemExit("This importer currently supports scene auto, 01, 03, 07, 08, 09, 11, 12, 13, 14, 15, 16, 17, 18, and 19.")

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output = output.with_name(f"scene-{scene['id']}-{output.name.split('scene-', 1)[-1]}" if output.name.startswith("scene-auto-") else output.name)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8-sig")
    print(output)


if __name__ == "__main__":
    main()
