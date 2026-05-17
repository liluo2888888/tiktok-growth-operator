from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from validator_runtime import create_validator_runtime


DEFAULT_NEWEST_REPLY = Path(
    r"E:\tiktok\TikMatrix\tmp\live-newest-reply-final-2\newest-reply\newest_reply.json"
)
DEFAULT_NOTICE_MULTI = Path(
    r"E:\tiktok\TikMatrix\tmp\live-notice-multi-final-3\notice-multi\notice_multi.json"
)
DEFAULT_FOLLOWING_REQUESTS = Path(
    r"E:\tiktok\TikMatrix\tmp\live-following-requests-final\following-requests\following_request_list.json"
)
DEFAULT_FOLLOWING_LIST = Path(
    r"E:\tiktok\TikMatrix\tmp\live-following-list-final\following\following_list.json"
)
DEFAULT_FOLLOWER_LIST = Path(
    r"E:\tiktok\TikMatrix\tmp\live-follower-list-final\followers\follower_list.json"
)
DEFAULT_LIVE_FOLLOWING = Path(
    r"E:\tiktok\TikMatrix\tmp\live-following-final\live-following\live_following.json"
)


def resolve_fixture_path(*candidates: Path) -> Path:
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise SystemExit(f"Missing required validation fixture. Checked: {[str(candidate) for candidate in candidates]}")


def require_path(path: Path, label: str) -> None:
    if not path.exists():
        raise SystemExit(f"Missing required {label}: {path}")


def main() -> int:
    skill_root = Path(__file__).resolve().parents[1]
    fixture_root = skill_root / "testdata" / "validation" / "tikmatrix"
    resolved_inputs = [
        (
            "newest_reply",
            resolve_fixture_path(
                fixture_root / "live-newest-reply-final-2" / "newest-reply" / "newest_reply.json",
                DEFAULT_NEWEST_REPLY,
            ),
        ),
        (
            "notice_multi",
            resolve_fixture_path(
                fixture_root / "live-notice-multi-final-3" / "notice-multi" / "notice_multi.json",
                DEFAULT_NOTICE_MULTI,
            ),
        ),
        (
            "following_requests",
            resolve_fixture_path(
                fixture_root / "live-following-requests-final" / "following-requests" / "following_request_list.json",
                DEFAULT_FOLLOWING_REQUESTS,
            ),
        ),
        (
            "following_list",
            resolve_fixture_path(
                fixture_root / "live-following-list-final" / "following" / "following_list.json",
                DEFAULT_FOLLOWING_LIST,
            ),
        ),
        (
            "follower_list",
            resolve_fixture_path(
                fixture_root / "live-follower-list-final" / "followers" / "follower_list.json",
                DEFAULT_FOLLOWER_LIST,
            ),
        ),
        (
            "live_following",
            resolve_fixture_path(
                fixture_root / "live-following-final" / "live-following" / "live_following.json",
                DEFAULT_LIVE_FOLLOWING,
            ),
        ),
    ]
    for label, path in resolved_inputs:
        require_path(path, label)

    output_root = create_validator_runtime(skill_root, "account-ops-bridge")
    resolved = dict(resolved_inputs)
    command = [
        sys.executable,
        str(skill_root / "scripts" / "run_tikmatrix_account_ops_bridge.py"),
        "--name",
        "validate-account-ops-bridge",
        "--project",
        "Validate Account Ops Bridge",
        "--platform",
        "TikTok",
        "--market",
        "US",
        "--output-root",
        str(output_root),
        "--newest-reply-json",
        str(resolved["newest_reply"]),
        "--notice-multi-json",
        str(resolved["notice_multi"]),
        "--following-requests-json",
        str(resolved["following_requests"]),
        "--following-list-json",
        str(resolved["following_list"]),
        "--follower-list-json",
        str(resolved["follower_list"]),
        "--live-following-json",
        str(resolved["live_following"]),
    ]
    completed = subprocess.run(command, text=True, capture_output=True)
    payload = {
        "command": command,
        "returncode": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }
    if completed.returncode != 0:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 1

    data = json.loads(completed.stdout)
    expected = [
        Path(data["summary_path"]),
        Path(data["source_report_path"]),
        Path(data["pack"]["output_path"]),
        Path(data["pack"]["manifest_path"]),
        Path(data["bridge_root"]) / "source_manifest.json",
    ]
    missing = [str(path) for path in expected if not path.exists()]
    if missing:
        payload["returncode"] = 1
        payload["stderr"] = "Missing expected account-ops bridge outputs: " + "; ".join(missing)
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 1

    payload["parsed"] = data
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
