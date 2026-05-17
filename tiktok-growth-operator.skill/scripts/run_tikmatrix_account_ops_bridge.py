from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

from generate_operator_pack import generate_pack_output
from text_normalization import read_json_file, write_json_file


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Bridge TikMatrix inbox/account-operation exports into an operator-facing account-ops-assist pack."
    )
    parser.add_argument("--name", required=True, help="Short run name.")
    parser.add_argument("--project", required=True, help="Operator project title.")
    parser.add_argument("--output-root", default="", help="Optional explicit output root.")
    parser.add_argument("--platform", default="TikTok", help="Platform label for outputs.")
    parser.add_argument("--market", default="US", help="Market label for outputs.")
    parser.add_argument("--newest-reply-json", default="", help="Optional newest_reply.json export path.")
    parser.add_argument("--notice-multi-json", default="", help="Optional notice_multi.json export path.")
    parser.add_argument("--following-requests-json", default="", help="Optional following_request_list.json export path.")
    parser.add_argument("--following-list-json", default="", help="Optional following_list.json export path.")
    parser.add_argument("--follower-list-json", default="", help="Optional follower_list.json export path.")
    parser.add_argument("--live-following-json", default="", help="Optional live_following.json export path.")
    return parser.parse_args()


def load_json(path: Path) -> dict | list:
    return read_json_file(path)


def ensure_root(output_root: str, skill_root: Path, run_name: str) -> Path:
    if output_root.strip():
        root = Path(output_root).expanduser().resolve()
    else:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        root = skill_root / "tmp" / f"{stamp}-tikmatrix-account-ops-{run_name}"
    root.mkdir(parents=True, exist_ok=True)
    return root


def clean_text(value: object) -> str:
    if value is None:
        return ""
    return str(value).replace("\r\n", "\n").strip()


def safe_int(value: object) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def render_following_users(payload: dict, limit: int = 5) -> list[str]:
    users = payload.get("users") or []
    lines: list[str] = []
    for user in users[:limit]:
        if not isinstance(user, dict):
            continue
        lines.append(
            f"- @{clean_text(user.get('unique_id'))}: followers={safe_int(user.get('follower_count'))}, "
            f"following={safe_int(user.get('following_count'))}, videos={safe_int(user.get('video_count'))}"
        )
    return lines


def render_live_rooms(payload: dict, limit: int = 5) -> list[str]:
    items = payload.get("items") or payload.get("lives") or payload.get("rooms") or []
    lines: list[str] = []
    for item in items[:limit]:
        if not isinstance(item, dict):
            continue
        title = clean_text(item.get("title") or item.get("room_title") or item.get("nickname") or item.get("owner_nickname"))
        room_id = clean_text(item.get("room_id") or item.get("id"))
        viewer_count = safe_int(item.get("viewer_count") or item.get("user_count") or item.get("live_viewer_count"))
        lines.append(f"- live room `{room_id or 'unknown'}`: {title or 'untitled'}, viewers={viewer_count}")
    return lines


def build_summary(args: argparse.Namespace) -> tuple[dict, dict]:
    evidence: list[dict] = []
    sections: list[dict] = []
    inputs: list[str] = []
    requested_outputs = [
        "account operations summary",
        "inbox reply triage",
        "notice radar",
        "following request review",
        "safe response drafting",
    ]

    def maybe_load(raw_path: str, label: str) -> dict:
        if not raw_path.strip():
            return {}
        path = Path(raw_path).expanduser().resolve()
        payload = load_json(path)
        if not isinstance(payload, dict):
            raise SystemExit(f"{label} must be a JSON object: {path}")
        evidence.append({"label": label, "detail": str(path)})
        inputs.append(f"{label}: {path.name}")
        return payload

    newest_reply = maybe_load(args.newest_reply_json, "newest_reply")
    notice_multi = maybe_load(args.notice_multi_json, "notice_multi")
    following_requests = maybe_load(args.following_requests_json, "following_requests")
    following_list = maybe_load(args.following_list_json, "following_list")
    follower_list = maybe_load(args.follower_list_json, "follower_list")
    live_following = maybe_load(args.live_following_json, "live_following")

    if not evidence:
        raise SystemExit("Provide at least one TikMatrix account-operations export JSON.")

    has_reply = bool(newest_reply.get("has_reply"))
    notice_count = safe_int(notice_multi.get("item_count"))
    request_count = safe_int(following_requests.get("item_count"))
    following_count = safe_int(following_list.get("item_count"))
    follower_count = safe_int(follower_list.get("item_count"))
    live_count = safe_int(live_following.get("item_count"))

    sections.append(
        {
            "heading": "Inbox Signals",
            "bullets": [
                f"Has newest reply signal: {'yes' if has_reply else 'no'}",
                f"Newest reply source URL: {clean_text(newest_reply.get('source_url')) or 'n/a'}",
                f"Reply push suggested by source: {'yes' if newest_reply.get('need_push') else 'no'}",
            ],
        }
    )
    sections.append(
        {
            "heading": "Notice Signals",
            "bullets": [
                f"Unread or grouped notice items captured: {notice_count}",
                f"Notice source URL: {clean_text(notice_multi.get('source_url')) or 'n/a'}",
            ],
        }
    )
    sections.append(
        {
            "heading": "Following Request Signals",
            "bullets": [
                f"Pending following requests captured: {request_count}",
                f"Following-request source URL: {clean_text(following_requests.get('source_url')) or 'n/a'}",
            ],
        }
    )
    sections.append(
        {
            "heading": "Relationship Radar",
            "bullets": [
                f"Visible following accounts captured: {following_count}",
                f"Visible follower accounts captured: {follower_count}",
                f"Live-following rooms captured: {live_count}",
            ]
            + render_following_users(following_list)
            + render_following_users(follower_list)
            + render_live_rooms(live_following),
        }
    )
    sections.append(
        {
            "heading": "Priority Queue",
            "bullets": [
                "1. Check whether any real reply or inbox follow-up needs a human response now.",
                "2. Check whether notice or request counts changed versus the last review.",
                "3. Review whether any following or live-following account should be added to competitor watch.",
                "4. Draft only safe human-reviewed replies; do not auto-send anything from this package.",
            ],
        }
    )
    sections.append(
        {
            "heading": "Safe Response Guidance",
            "bullets": [
                "Use short, factual, non-spammy replies.",
                "Never impersonate the platform or promise account actions you cannot complete.",
                "Escalate unusual moderation, legal, or abuse cases to a human owner.",
            ],
        }
    )

    summary = {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "project": args.project,
        "has_reply": has_reply,
        "notice_count": notice_count,
        "following_request_count": request_count,
        "following_count": following_count,
        "follower_count": follower_count,
        "live_following_count": live_count,
        "evidence_count": len(evidence),
    }

    report = {
        "metadata": {
            "title": "TikTok Account Ops Inbox Assist",
            "project": args.project,
            "scene": "account-ops",
            "scene_title": "TikTok Account Ops Inbox Assist",
        },
        "working_context": {
            "summary": "Review logged-in TikTok account signals from TikMatrix inbox and relationship exports, then turn them into a safe human-reviewed operating pack.",
            "inputs": inputs,
            "requested_outputs": requested_outputs,
            "minimum_evidence": [item["label"] for item in evidence],
            "ideal_evidence": [
                "newest_reply",
                "notice_multi",
                "following_requests",
                "following_list",
                "follower_list",
                "live_following",
            ],
        },
        "executive_summary": {
            "conclusion": "Treat inbox, notice, and relationship surfaces as one daily account-operations review queue.",
            "why_it_matters": "This captures the platform-adjacent account-ops layer without pretending auto-reply or risky mutations already exist.",
            "next_action": "Review the highest-priority inbox or notice signal first, then update the relationship watch list.",
        },
        "sections": sections,
        "evidence": evidence,
        "account_ops_summary": summary,
    }
    return summary, report


def main() -> None:
    args = parse_args()
    skill_root = Path(__file__).resolve().parents[1]
    root = ensure_root(args.output_root, skill_root, args.name.strip())
    summary, report = build_summary(args)

    bridge_root = root / "account-ops-bridge"
    bridge_root.mkdir(parents=True, exist_ok=True)
    summary_path = bridge_root / "account_ops_summary.json"
    report_path = bridge_root / "account_ops_source_report.json"
    source_manifest_path = bridge_root / "source_manifest.json"

    write_json_file(summary_path, summary)
    write_json_file(report_path, report)
    write_json_file(
        source_manifest_path,
        {
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "newest_reply_json": args.newest_reply_json,
            "notice_multi_json": args.notice_multi_json,
            "following_requests_json": args.following_requests_json,
            "following_list_json": args.following_list_json,
            "follower_list_json": args.follower_list_json,
            "live_following_json": args.live_following_json,
        },
    )

    pack_result = generate_pack_output(
        pack_type="account-ops-assist",
        output_dir=root / "operator-packs" / "account-ops-assist",
        project=args.project,
        platform=args.platform,
        market=args.market,
        source_report_path=report_path,
    )

    print(
        json.dumps(
            {
                "bridge_root": str(bridge_root),
                "summary_path": str(summary_path),
                "source_report_path": str(report_path),
                "pack": pack_result,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
