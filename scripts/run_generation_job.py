from __future__ import annotations

import argparse
import json
from pathlib import Path

from generation_jobs import load_jobs, poll_generation_job
from generation_renderer_backend import poll_generation_job_remote, submit_generation_job


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Submit or poll a Scene 09-16 generation job.")
    parser.add_argument("--capture-root", required=True, help="Capture-pack root with generation_jobs.json.")
    parser.add_argument("--job-id", default="", help="Job id. Defaults to latest job in registry.")
    parser.add_argument("--submit", action="store_true", help="Submit job to renderer backend.")
    parser.add_argument("--poll", action="store_true", help="Poll remote renderer or local artifacts manifest.")
    return parser.parse_args()


def latest_job_id(capture_root: Path) -> str:
    registry = load_jobs(capture_root)
    jobs = registry.get("jobs") or {}
    if not isinstance(jobs, dict) or not jobs:
        return ""
    return sorted(jobs.keys())[-1]


def main() -> None:
    args = parse_args()
    capture_root = Path(args.capture_root).resolve()
    job_id = args.job_id.strip() or latest_job_id(capture_root)
    if not job_id:
        raise SystemExit("No generation job found. Import scene 09-16 first.")

    results: dict = {"job_id": job_id}
    if args.submit:
        results["submit"] = submit_generation_job(capture_root, job_id)
    if args.poll:
        results["poll"] = poll_generation_job(capture_root, job_id)
        if not args.submit:
            results["poll_remote"] = poll_generation_job_remote(capture_root, job_id)

    if not args.submit and not args.poll:
        results["registry"] = (load_jobs(capture_root).get("jobs") or {}).get(job_id)

    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
