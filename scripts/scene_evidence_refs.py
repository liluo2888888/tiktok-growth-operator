from __future__ import annotations

from evidence_refs import (
    account_week_evidence_ref,
    clean_text,
    comment_evidence_ref,
    creator_evidence_ref,
    merge_evidence_refs,
    screenshot_evidence_ref,
    transcript_evidence_ref,
    video_evidence_ref,
)


def require_section(sections: dict, *names: str) -> dict:
    for name in names:
        if name in sections:
            return sections[name]
    raise KeyError(names[0])


def attach_scene_03_evidence_refs(sections: dict, top_ranked: list[dict], winner: dict) -> None:
    if winner:
        merge_evidence_refs(
            sections["Executive Conclusion"],
            [
                video_evidence_ref(
                    winner,
                    supports="Executive conclusion: top shortlist hook and authority packaging",
                    time_range="00:00-00:03",
                )
            ],
        )
    for index, video in enumerate(top_ranked[:3], start=1):
        merge_evidence_refs(
            sections["Structure Logic"],
            [
                video_evidence_ref(
                    video,
                    supports=f"Shortlist row P{index}: hook, proof style, and traction metrics",
                    time_range="00:00-00:05",
                )
            ],
        )
        merge_evidence_refs(
            sections["Core Mechanism"],
            [
                video_evidence_ref(
                    video,
                    supports=f"Per-video teardown: hook-to-proof timeline for candidate {index}",
                    time_range="00:00-00:14",
                ),
                transcript_evidence_ref(
                    video,
                    supports=f"Recovered caption / script lines for candidate {index}",
                ),
            ],
        )
    if top_ranked:
        merge_evidence_refs(
            sections["Reusable Formula"],
            [
                video_evidence_ref(
                    top_ranked[0],
                    supports="Shared hook formula distilled from the strongest shortlisted video",
                    time_range="00:00-00:02",
                ),
            ],
        )
        if len(top_ranked) > 1:
            merge_evidence_refs(
                sections["Reusable Formula"],
                [
                    video_evidence_ref(
                        top_ranked[1],
                        supports="Proof-beat pattern that repeats without relying on the same product shell",
                        time_range="00:03-00:08",
                    ),
                ],
            )
        merge_evidence_refs(
            sections["Risks And Adaptation Notes"],
            [
                video_evidence_ref(
                    top_ranked[0],
                    supports="Risk note: borrowed authority or thin-caption candidates must stay flagged",
                    time_range="full-video",
                ),
            ],
        )


def attach_scene_04_evidence_refs(sections: dict, source: dict, profile_summary: dict) -> None:
    if not source:
        return
    source_url = clean_text(source.get("video_url"))
    merge_evidence_refs(
        sections["Executive Conclusion"],
        [
            video_evidence_ref(
                source,
                supports="Executive conclusion: recognition-first hook and compressed proof path",
                time_range="00:00-00:03",
            ),
            creator_evidence_ref(
                source,
                profile_summary,
                supports="Account baseline that may inflate lift for this reference video",
            ),
        ],
    )
    merge_evidence_refs(
        sections["Structure Logic"],
        [
            video_evidence_ref(source, supports="Timeline row: hook beat", time_range="00:00-00:03"),
            video_evidence_ref(source, supports="Timeline row: setup-to-proof transition", time_range="00:03-00:08"),
            transcript_evidence_ref(source, supports="Timeline row: proof segment supported by caption/subtitle"),
            video_evidence_ref(source, supports="Timeline row: continuation close", time_range="00:14-00:20"),
        ],
    )
    merge_evidence_refs(
        sections["Core Mechanism"],
        [
            video_evidence_ref(source, supports="Mechanism: recognition-first compression logic", time_range="full-video"),
        ],
    )
    merge_evidence_refs(
        require_section(sections, "可复用公式", "Reusable Formula"),
        [
            video_evidence_ref(source, supports="Hook formula", time_range="00:00-00:02"),
            screenshot_evidence_ref(
                source_id=f"{clean_text(source.get('video_id')) or 'primary'}-style",
                source_url=source_url,
                supports="Visual style reference",
                excerpt=clean_text(source.get("core_topic") or source.get("desc")),
            ),
            video_evidence_ref(source, supports="Proof formula", time_range="00:06-00:14"),
        ],
    )
    merge_evidence_refs(
        sections["Risks And Adaptation Notes"],
        [
            video_evidence_ref(source, supports="Opening hook adaptation risk", time_range="00:00-00:03"),
            video_evidence_ref(source, supports="Conversion pacing adaptation risk", time_range="00:03-00:14"),
        ],
    )
    merge_evidence_refs(
        sections["BGM And Sensory Layer"],
        [
            video_evidence_ref(
                source,
                supports="BGM / sensory layer judgment",
                time_range="audio-layer",
                excerpt=clean_text(source.get("music_title") or "native platform audio"),
            ),
            transcript_evidence_ref(source, supports="Subtitle style that keeps logic readable without heavy VO"),
        ],
    )
    if "Production-Spec Handoff" in sections:
        merge_evidence_refs(
            sections["Production-Spec Handoff"],
            [
                video_evidence_ref(source, supports="Shot-by-shot production handoff", time_range="00:00-00:20"),
            ],
        )
    merge_evidence_refs(
        sections["Next Action"],
        [video_evidence_ref(source, supports="Storyboard / generator handoff row", time_range="00:00-00:20")],
    )


def attach_scene_05_evidence_refs(sections: dict, source: dict, profile_summary: dict) -> None:
    if not source:
        return
    merge_evidence_refs(
        sections["Executive Conclusion"],
        [
            video_evidence_ref(
                source,
                supports="Executive conclusion: infer-layer prompt brief from the reference video",
                time_range="00:00-00:03",
            ),
            creator_evidence_ref(source, profile_summary, supports="Source account context for infer vs adapt split"),
        ],
    )
    merge_evidence_refs(
        sections["Structure Logic"],
        [video_evidence_ref(source, supports="Generator schema: style / environment / pacing fields", time_range="full-video")],
    )
    merge_evidence_refs(
        sections["Core Mechanism"],
        [
            video_evidence_ref(source, supports="Hook design", time_range="00:00-00:03"),
            video_evidence_ref(source, supports="Proof design", time_range="00:06-00:14"),
            video_evidence_ref(source, supports="Pacing and close design", time_range="00:14-00:20"),
        ],
    )
    merge_evidence_refs(
        sections["Reusable Formula"],
        [video_evidence_ref(source, supports="Generator-ready schema evidence fields", time_range="full-video")],
    )
    merge_evidence_refs(
        sections["Risks And Adaptation Notes"],
        [
            video_evidence_ref(source, supports="Shot table: opening recognition beat", time_range="0-3s"),
            video_evidence_ref(source, supports="Shot table: proof beat", time_range="8-14s"),
        ],
    )
    merge_evidence_refs(
        sections["Next Action"],
        [video_evidence_ref(source, supports="Product adaptation field mapping", time_range="full-video")],
    )
    if "Production-Spec Handoff" in sections:
        merge_evidence_refs(
            sections["Production-Spec Handoff"],
            [transcript_evidence_ref(source, supports="Production handoff: caption/subtitle evidence for generator fill")],
        )


def reply_chain_anchor_entry(chain: dict | None) -> dict:
    if not isinstance(chain, dict):
        return {}
    anchor = chain.get("anchor_entry")
    if isinstance(anchor, dict) and anchor:
        return anchor
    top_entry = chain.get("top_entry")
    return top_entry if isinstance(top_entry, dict) else {}


def attach_scene_08_evidence_refs(
    sections: dict,
    comment_entries: list[dict],
    comment_snapshot: dict,
    top_purchase: dict | None,
    top_complaint: dict | None,
    top_reply: dict | None,
    top_trust: dict | None,
    top_reply_chain: dict | None = None,
) -> None:
    top_entry = (top_purchase or {}).get("top_entry") if isinstance(top_purchase, dict) else {}
    if isinstance(top_entry, dict) and top_entry:
        merge_evidence_refs(
            sections["Executive Conclusion"],
            [
                comment_evidence_ref(
                    top_entry,
                    supports="Executive conclusion: strongest purchase-factor language",
                )
            ],
        )
    chain_anchor = reply_chain_anchor_entry(top_reply_chain)
    if chain_anchor:
        merge_evidence_refs(
            sections["High-Level Judgment"],
            [
                comment_evidence_ref(
                    chain_anchor,
                    supports="High-level judgment: synthesized reply-chain anchor comment",
                    excerpt=clean_text(top_reply_chain.get("synthesis")) if isinstance(top_reply_chain, dict) else "",
                )
            ],
        )
    for cluster, label in [
        (top_purchase, "High-level judgment: purchase-factor cluster"),
        (top_complaint, "High-level judgment: complaint / objection cluster"),
        (top_reply, "High-level judgment: reply-chain pressure cluster"),
        (top_trust, "High-level judgment: trust-signal cluster"),
    ]:
        entry = (cluster or {}).get("top_entry") if isinstance(cluster, dict) else {}
        if isinstance(entry, dict) and entry:
            merge_evidence_refs(
                sections["High-Level Judgment"],
                [comment_evidence_ref(entry, supports=label)],
            )
    for entry in comment_entries[:4]:
        if not isinstance(entry, dict):
            continue
        merge_evidence_refs(
            sections["Evidence Clusters"],
            [
                comment_evidence_ref(
                    entry,
                    supports="Evidence cluster row: cleaned buyer-language theme",
                )
            ],
        )
    for cluster, action_label in [
        (top_purchase, "Recommended action: purchase-factor copy and proof"),
        (top_complaint, "Recommended action: complaint preemption"),
        (top_reply, "Recommended action: reply-chain handling"),
    ]:
        entry = (cluster or {}).get("top_entry") if isinstance(cluster, dict) else {}
        if isinstance(entry, dict) and entry:
            merge_evidence_refs(
                sections["Recommended Action"],
                [comment_evidence_ref(entry, supports=action_label)],
            )
    cleaned_count = comment_snapshot.get("cleaned_count") if isinstance(comment_snapshot, dict) else 0
    if cleaned_count:
        merge_evidence_refs(
            sections["Open Questions"],
            [
                comment_evidence_ref(
                    comment_entries[0] if comment_entries else {},
                    supports="Open question: sampling coverage still partial across source videos",
                    excerpt=f"Cleaned comment count in current pack: {cleaned_count}",
                )
            ],
        )


def attach_scene_17_evidence_refs(
    sections: dict,
    top_ranked: list[dict],
    high_video: dict,
    low_video: dict,
    profile_summary: dict,
) -> None:
    if high_video:
        merge_evidence_refs(
            sections["Executive Conclusion"],
            [
                video_evidence_ref(
                    high_video,
                    supports="Executive conclusion: high-engagement packaging reference",
                    time_range="00:00-00:05",
                ),
            ],
        )
    if low_video and low_video is not high_video:
        merge_evidence_refs(
            sections["Executive Conclusion"],
            [
                video_evidence_ref(
                    low_video,
                    supports="Executive conclusion: low-engagement contrast sample",
                    time_range="00:00-00:05",
                ),
            ],
        )
    merge_evidence_refs(
        sections["Structure Logic"],
        [
            creator_evidence_ref(
                high_video or {},
                profile_summary,
                supports="Account snapshot: positioning and cadence baseline",
            ),
        ],
    )
    if high_video:
        merge_evidence_refs(
            sections["Structure Logic"],
            [video_evidence_ref(high_video, supports="Account snapshot: top engagement metrics", time_range="full-video")],
        )
    if high_video and low_video:
        merge_evidence_refs(
            sections["Core Mechanism"],
            [
                video_evidence_ref(high_video, supports="High vs low comparison: high-engagement sample"),
                video_evidence_ref(low_video, supports="High vs low comparison: low-engagement sample"),
            ],
        )
    for video in top_ranked[:3]:
        merge_evidence_refs(
            sections["Reusable Formula"],
            [
                video_evidence_ref(
                    video,
                    supports="Creator formula library row",
                    excerpt=clean_text(video.get("hook_text") or video.get("desc")),
                )
            ],
        )
    if high_video:
        merge_evidence_refs(
            sections["Visual And Distribution Signature"],
            [
                video_evidence_ref(high_video, supports="Visual / audio / hashtag distribution signature"),
                creator_evidence_ref(high_video, profile_summary, supports="Publish-window baseline still sample-thin"),
            ],
        )
    if high_video:
        merge_evidence_refs(
            sections["Next Action"],
            [video_evidence_ref(high_video, supports="Next action: hook / proof / publish experiment plan")],
        )


def attach_scene_18_evidence_refs(
    sections: dict,
    top_ranked: list[dict],
    compare: dict,
    profile_summary: dict,
    comment_snapshot: dict | None,
) -> None:
    profile_url = clean_text(profile_summary.get("profile_url") or profile_summary.get("profile_final_url"))
    if compare.get("mode") == "compare":
        merge_evidence_refs(
            sections["Executive Conclusion"],
            [
                account_week_evidence_ref(
                    week_label=clean_text(compare.get("latest_week")),
                    source_url=profile_url,
                    source_id=f"week-{clean_text(compare.get('latest_week'))}",
                    supports="Executive conclusion: latest-week strategy shift",
                    excerpt=f"Compared against prior week {clean_text(compare.get('prior_week'))}",
                ),
            ],
        )
    if top_ranked:
        merge_evidence_refs(
            sections["Executive Conclusion"],
            [
                video_evidence_ref(
                    top_ranked[0],
                    supports="Executive conclusion: strongest packaging line this week",
                    time_range="00:00-00:05",
                ),
            ],
        )
    for video in top_ranked[:3]:
        week = clean_text(video.get("publish_week") or video.get("publish_window"))
        merge_evidence_refs(
            sections["Objects To Track"],
            [
                account_week_evidence_ref(
                    week_label=week or "week-unknown",
                    source_url=clean_text(video.get("video_url")) or profile_url,
                    source_id=clean_text(video.get("video_id")) or clean_text(video.get("unique_id")),
                    supports="Tracked account/week object row",
                    excerpt=clean_text(video.get("desc") or video.get("hook_text")),
                )
            ],
        )
    for video in top_ranked[:2]:
        merge_evidence_refs(
            sections["Why They Matter"],
            [
                video_evidence_ref(
                    video,
                    supports="Weekly shift / breakout interpretation",
                    time_range="00:00-00:05",
                )
            ],
        )
    reply_chain = (comment_snapshot or {}).get("top_reply_chain")
    reply_entry = reply_chain_anchor_entry(reply_chain if isinstance(reply_chain, dict) else None)
    if not reply_entry:
        reply_entry = ((comment_snapshot or {}).get("top_reply_pattern") or {}).get("top_entry")
    if isinstance(reply_entry, dict) and reply_entry:
        merge_evidence_refs(
            sections["Why They Matter"],
            [
                comment_evidence_ref(
                    reply_entry,
                    supports="Comment-language pressure behind this week's breakout interpretation",
                    excerpt=clean_text(reply_chain.get("synthesis")) if isinstance(reply_chain, dict) else "",
                )
            ],
        )
    if top_ranked:
        merge_evidence_refs(
            sections["Next Action"],
            [
                video_evidence_ref(
                    top_ranked[0],
                    supports="Dispatch action: continue / borrow / ignore decision for this week",
                )
            ],
        )


def attach_scene_19_evidence_refs(
    sections: dict,
    high_video: dict,
    low_video: dict,
    compare: dict,
    comment_snapshot: dict | None,
    top_ranked: list[dict],
) -> None:
    if compare.get("mode") == "compare":
        merge_evidence_refs(
            sections["Executive Conclusion"],
            [
                account_week_evidence_ref(
                    week_label=clean_text(compare.get("latest_week")),
                    source_url=clean_text(high_video.get("video_url")),
                    source_id=f"week-{clean_text(compare.get('latest_week'))}",
                    supports="Executive conclusion: two-week retro comparison",
                    excerpt=f"Prior week baseline: {clean_text(compare.get('prior_week'))}",
                ),
            ],
        )
    if high_video:
        merge_evidence_refs(
            sections["Executive Conclusion"],
            [
                video_evidence_ref(
                    high_video,
                    supports="Executive conclusion: high-performing cluster reference",
                    time_range="00:00-00:05",
                ),
            ],
        )
    if low_video and low_video is not high_video:
        merge_evidence_refs(
            sections["Executive Conclusion"],
            [
                video_evidence_ref(
                    low_video,
                    supports="Executive conclusion: low-performing contrast reference",
                    time_range="00:00-00:05",
                ),
            ],
        )
    for video in (high_video, low_video):
        if not video:
            continue
        merge_evidence_refs(
            sections["High-Level Judgment"],
            [
                video_evidence_ref(
                    video,
                    supports="High-level judgment: publish-window and proxy signal comparison",
                    excerpt=(
                        f"window={clean_text(video.get('publish_window'))}; "
                        f"conversion={clean_text(video.get('conversion_proxy'))}; "
                        f"roi={clean_text(video.get('roi_proxy'))}"
                    ),
                )
            ],
        )
    for video in top_ranked[:3]:
        merge_evidence_refs(
            sections["Evidence Clusters"],
            [
                video_evidence_ref(
                    video,
                    supports="Evidence cluster: ROI / window / weekly pattern row",
                    time_range="cluster-window",
                )
            ],
        )
    reply_chain = (comment_snapshot or {}).get("top_reply_chain")
    reply_entry = reply_chain_anchor_entry(reply_chain if isinstance(reply_chain, dict) else None)
    if not reply_entry:
        reply_entry = ((comment_snapshot or {}).get("top_reply_pattern") or {}).get("top_entry")
    complaint_entry = ((comment_snapshot or {}).get("top_complaint_cluster") or {}).get("top_entry")
    entry = reply_entry if isinstance(reply_entry, dict) and reply_entry else complaint_entry
    if isinstance(entry, dict) and entry:
        merge_evidence_refs(
            sections["Evidence Clusters"],
            [comment_evidence_ref(entry, supports="Evidence cluster: comment-side friction or trust pattern")],
        )
    if high_video:
        merge_evidence_refs(
            sections["Recommended Action"],
            [
                video_evidence_ref(
                    high_video,
                    supports="Recommended action: scale the winning content pattern next cycle",
                )
            ],
        )
