from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any

from text_normalization import normalize_text, read_json_file, write_json_file


def clean_text(value: object) -> str:
    return normalize_text(value)


GRAPH_VERSION = "1.0"


def video_identity(video: dict) -> str:
    return clean_text(video.get("video_id") or video.get("video_url") or video.get("desc"))


def creator_key(video: dict) -> str:
    unique_id = clean_text(video.get("unique_id") or video.get("author_unique_id"))
    nickname = clean_text(video.get("nickname"))
    if unique_id:
        return unique_id.lower()
    if nickname:
        return nickname.lower()
    return ""


def sound_key(video: dict) -> str:
    return clean_text(video.get("music_title")).lower()


def hashtag_keys(video: dict) -> list[str]:
    tags = video.get("hashtags") or []
    normalized: list[str] = []
    if isinstance(tags, list):
        for tag in tags:
            text = clean_text(tag).lstrip("#").lower()
            if text and text not in normalized:
                normalized.append(text)
    return normalized


def cluster_label(kind: str, label: str, size: int) -> str:
    if kind == "creator":
        return f"creator cluster (@{label}, {size} posts)"
    if kind == "sound":
        return f"sound cluster ({label}, {size} posts)"
    if kind == "hashtag":
        return f"#hashtag neighborhood (#{label}, {size} posts)"
    return f"{kind} cluster ({label}, {size} posts)"


def build_content_graph(ranked_videos: list[dict]) -> dict[str, Any]:
    videos = [item for item in ranked_videos if isinstance(item, dict)]
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, str]] = []
    provenance_by_video: dict[str, list[str]] = {}

    creator_groups: dict[str, list[str]] = defaultdict(list)
    sound_groups: dict[str, list[str]] = defaultdict(list)
    hashtag_groups: dict[str, list[str]] = defaultdict(list)

    for video in videos:
        vid = video_identity(video)
        if not vid:
            continue
        nodes.append(
            {
                "id": f"video:{vid}",
                "type": "video",
                "label": sentence_clip(clean_text(video.get("desc")), 72) or vid,
                "video_id": clean_text(video.get("video_id")),
                "video_url": clean_text(video.get("video_url")),
            }
        )
        creator = creator_key(video)
        if creator:
            creator_groups[creator].append(vid)
            edges.append({"from": f"video:{vid}", "to": f"creator:{creator}", "type": "authored_by"})
        sound = sound_key(video)
        if sound:
            sound_groups[sound].append(vid)
            edges.append({"from": f"video:{vid}", "to": f"sound:{sound}", "type": "uses_sound"})
        for tag in hashtag_keys(video):
            hashtag_groups[tag].append(vid)
            edges.append({"from": f"video:{vid}", "to": f"hashtag:{tag}", "type": "tagged_with"})

    for creator, members in creator_groups.items():
        nodes.append({"id": f"creator:{creator}", "type": "creator", "label": creator, "member_count": len(members)})
        if len(members) > 1:
            for left, right in zip(members, members[1:]):
                edges.append({"from": f"video:{left}", "to": f"video:{right}", "type": "shared_creator_cluster"})

    for sound, members in sound_groups.items():
        display = clean_text(members and next((item.get("music_title") for item in videos if video_identity(item) == members[0]), "")) or sound
        nodes.append({"id": f"sound:{sound}", "type": "sound", "label": display or sound, "member_count": len(members)})
        if len(members) > 1:
            for left, right in zip(members, members[1:]):
                edges.append({"from": f"video:{left}", "to": f"video:{right}", "type": "shared_sound_cluster"})

    for tag, members in hashtag_groups.items():
        nodes.append({"id": f"hashtag:{tag}", "type": "hashtag", "label": f"#{tag}", "member_count": len(members)})
        if len(members) > 1:
            for left, right in zip(members, members[1:]):
                edges.append({"from": f"video:{left}", "to": f"video:{right}", "type": "shared_hashtag_cluster"})

    ranked_ids = [video_identity(item) for item in videos if video_identity(item)]
    for index, video in enumerate(videos, start=1):
        vid = video_identity(video)
        if not vid:
            continue
        paths: list[str] = []
        creator = creator_key(video)
        if creator and len(creator_groups.get(creator, [])) > 1:
            paths.append(cluster_label("creator", creator, len(creator_groups[creator])))
        sound = sound_key(video)
        if sound and len(sound_groups.get(sound, [])) > 1:
            display = clean_text(video.get("music_title")) or sound
            paths.append(cluster_label("sound", display, len(sound_groups[sound])))
        tag_sizes = [(tag, len(hashtag_groups[tag])) for tag in hashtag_keys(video) if len(hashtag_groups.get(tag, [])) > 1]
        tag_sizes.sort(key=lambda item: item[1], reverse=True)
        for tag, size in tag_sizes[:2]:
            paths.append(cluster_label("hashtag", tag, size))
        profile_rank = safe_int(video.get("profile_rank") or video.get("reuse_rank") or index)
        if profile_rank:
            paths.append(f"reuse-value rank #{profile_rank}")
        score = safe_int(video.get("reuse_value_score"))
        if score:
            paths.append(f"reuse score {score}")
        if not paths:
            paths.append("standalone candidate (no shared creator/sound/hashtag cluster in this pack)")
        provenance_by_video[vid] = paths

    return {
        "version": GRAPH_VERSION,
        "node_count": len(nodes),
        "edge_count": len(edges),
        "nodes": nodes,
        "edges": edges,
        "shortlist_provenance": provenance_by_video,
        "cluster_summary": {
            "creator_clusters": sum(1 for members in creator_groups.values() if len(members) > 1),
            "sound_clusters": sum(1 for members in sound_groups.values() if len(members) > 1),
            "hashtag_neighborhoods": sum(1 for members in hashtag_groups.values() if len(members) > 1),
            "video_count": len(ranked_ids),
        },
    }


def sentence_clip(value: str, limit: int) -> str:
    text = clean_text(value)
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 1)].rstrip() + "…"


def safe_int(value: object, default: int = 0) -> int:
    try:
        if value is None or value == "":
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def apply_graph_to_videos(videos: list[dict], graph: dict[str, Any]) -> list[dict]:
    provenance_map = graph.get("shortlist_provenance") or {}
    enriched: list[dict] = []
    for video in videos:
        if not isinstance(video, dict):
            continue
        merged = dict(video)
        vid = video_identity(merged)
        paths = provenance_map.get(vid, [])
        if isinstance(paths, list) and paths:
            merged["content_graph_paths"] = paths
            merged["shortlist_provenance"] = paths
            merged["shortlist_provenance_text"] = " → ".join(paths[:4])
        enriched.append(merged)
    return enriched


def load_or_build_content_graph(capture_root: Path, ranked_videos: list[dict]) -> dict[str, Any]:
    graph_path = capture_root / "content_graph.json"
    if graph_path.exists():
        loaded = read_json_file(graph_path)
        if isinstance(loaded, dict) and loaded.get("shortlist_provenance"):
            return loaded
    graph = build_content_graph(ranked_videos)
    if capture_root.exists():
        write_json_file(graph_path, graph)
    return graph


def ensure_pack_content_graph(capture_root: Path, ranked_videos: list[dict], qualified_videos: list[dict]) -> dict[str, Any]:
    graph = load_or_build_content_graph(capture_root, ranked_videos)
    ranked_videos[:] = apply_graph_to_videos(ranked_videos, graph)
    if qualified_videos:
        qualified_videos[:] = apply_graph_to_videos(qualified_videos, graph)
    return graph


def shortlist_provenance_cell(video: dict) -> str:
    explicit = clean_text(video.get("shortlist_provenance_text"))
    if explicit:
        return explicit
    paths = video.get("shortlist_provenance") or video.get("content_graph_paths") or []
    if isinstance(paths, list) and paths:
        return " → ".join(str(item) for item in paths[:4])
    return clean_text(video.get("why_selected") or video.get("scene03_reason"))[:160]
