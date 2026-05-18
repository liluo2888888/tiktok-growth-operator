from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Scene 06 FastAPI shop gateway (uvicorn).")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8791)
    parser.add_argument(
        "--backend",
        default="",
        help="Optional SHOP_GATEWAY_BACKEND override: auto, research, partner, structured.",
    )
    parser.add_argument(
        "--install-deps",
        action="store_true",
        help="pip install -r services/shop_gateway/requirements.txt before starting.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    skill_root = Path(__file__).resolve().parents[1]
    gateway_dir = skill_root / "services" / "shop_gateway"
    requirements = gateway_dir / "requirements.txt"
    app_import = "services.shop_gateway.app:app"

    if args.install_deps:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", str(requirements)],
            check=True,
        )

    env = dict(**{k: v for k, v in __import__("os").environ.items()})
    if args.backend.strip():
        env["SHOP_GATEWAY_BACKEND"] = args.backend.strip()

    command = [
        sys.executable,
        "-m",
        "uvicorn",
        app_import,
        "--host",
        args.host,
        "--port",
        str(args.port),
        "--app-dir",
        str(skill_root),
    ]
    print(
        json.dumps(
            {
                "status": "starting",
                "url": f"http://{args.host}:{args.port}",
                "search_endpoint": f"http://{args.host}:{args.port}/v1/shop/products/search",
                "health": f"http://{args.host}:{args.port}/health",
                "command": command,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    raise SystemExit(subprocess.call(command, cwd=str(skill_root), env=env))


if __name__ == "__main__":
    main()
