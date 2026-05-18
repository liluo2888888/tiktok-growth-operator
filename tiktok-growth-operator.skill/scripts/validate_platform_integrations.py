from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
import subprocess
import sys

from generation_jobs import create_generation_job, poll_generation_job
from generation_renderer_backend import poll_generation_job_remote, submit_generation_job
from tiktok_shop_source import fetch_via_http, sync_competitor_products
from text_normalization import read_json_file


def skill_root() -> Path:
    return Path(__file__).resolve().parents[1]


class MockHandler(BaseHTTPRequestHandler):
    shop_products = [
        {
            "product_id": "mock-sku-1",
            "title": "Mock Shop Product",
            "platform": "TikTok Shop",
            "price": "19.99",
            "rating": "4.7",
            "review_count": "321",
            "sales_signal": "mock-rising",
            "url": "https://shop.example.com/mock-1",
        }
    ]
    verified_shop_source = {
        "source_type": "official",
        "provider": "tiktok_shop_open_platform",
        "auth_mode": "merchant_oauth",
        "issuer": "tiktok",
        "gateway_id": "mock-gateway",
    }
    include_shop_source_metadata = True
    generation_jobs: dict[str, dict] = {}

    def _json(self, code: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args) -> None:
        return

    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length else b"{}"
        payload = json.loads(raw.decode("utf-8"))
        if self.path == "/v1/shop/products/search":
            body: dict = {"products": self.shop_products}
            if self.include_shop_source_metadata:
                body["source"] = dict(self.verified_shop_source)
            self._json(200, body)
            return
        if self.path == "/v1/generation/jobs":
            job_id = payload.get("job_id", "mock-job")
            external = f"ext-{job_id}"
            self.generation_jobs[external] = {
                "status": "submitted",
                "artifact_links": [],
            }
            self._json(200, {"external_job_id": external, "status": "submitted"})
            return
        self._json(404, {"error": "not found"})

    def do_GET(self) -> None:
        if self.path.startswith("/v1/generation/jobs/"):
            external = self.path.rsplit("/", 1)[-1]
            job = self.generation_jobs.get(
                external,
                {
                    "status": "succeeded",
                    "artifact_links": ["https://example.com/mock-render.mp4"],
                },
            )
            job["status"] = "succeeded"
            job["artifact_links"] = ["https://example.com/mock-render.mp4"]
            self.generation_jobs[external] = job
            self._json(200, job)
            return
        self._json(404, {"error": "not found"})


def run_mock_server() -> tuple[HTTPServer, threading.Thread, str]:
    server = HTTPServer(("127.0.0.1", 0), MockHandler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread, f"http://127.0.0.1:{port}"


def validate_shop_http() -> dict:
    import os

    server, thread, base = run_mock_server()
    try:
        os.environ["TIKTOK_SHOP_HTTP_URL"] = base
        products, _http_meta = fetch_via_http(keyword="beauty", region="US", limit=5)
        if len(products) != 1:
            raise RuntimeError("mock shop http did not return one product")
        capture_root = skill_root() / "testdata" / "validation" / "tmp-shop-http"
        capture_root.mkdir(parents=True, exist_ok=True)
        result = sync_competitor_products(capture_root, keyword="beauty", force_refresh=True)
        if result.get("status") != "ok":
            raise RuntimeError(f"shop sync failed: {result}")
        return {"products": len(products), "source": result.get("source")}
    finally:
        server.shutdown()
        thread.join(timeout=2)


def validate_scene06_capture_run_http() -> dict:
    import os
    import tempfile

    server, thread, base = run_mock_server()
    try:
        fixture_root = skill_root() / "testdata" / "validation" / "captures" / "scene01-strong-inputs-pass"
        with tempfile.TemporaryDirectory(prefix="tgo-scene06-http-") as temp_dir:
            output_root = Path(temp_dir) / "scene06_http_run"
            env = os.environ.copy()
            env["TIKTOK_SHOP_HTTP_URL"] = base
            command = [
                sys.executable,
                str(skill_root() / "scripts" / "start_capture_pack_run.py"),
                "--scene",
                "06",
                "--capture-root",
                str(fixture_root),
                "--name",
                "validation-scene06-http",
                "--project",
                "TikTok Validation Scene 06 HTTP",
                "--platform",
                "TikTok",
                "--market",
                "US",
                "--formats",
                "md",
                "--shop-sync",
                "--shop-source-mode",
                "http",
                "--shop-keyword",
                "beauty",
                "--shop-region",
                "US",
                "--shop-limit",
                "5",
                "--shop-http-url",
                base,
                "--output-root",
                str(output_root),
            ]
            completed = subprocess.run(command, text=True, capture_output=True, encoding="utf-8", env=env, check=False)
            if completed.returncode != 0:
                raise RuntimeError(completed.stderr or completed.stdout or "scene06 capture run failed")
            payload = json.loads(completed.stdout)
            shop_sync = payload.get("shop_sync") or {}
            if shop_sync.get("status") != "ok":
                raise RuntimeError(f"scene06 shop sync did not succeed: {shop_sync}")
            report_path = Path(payload.get("report_json", ""))
            if not report_path.exists():
                raise RuntimeError(f"scene06 report missing: {report_path}")
            report = read_json_file(report_path)
            board = report.get("competitor_product_board") or {}
            if board.get("data_source_mode") not in {"tiktok_shop_live_http", "tiktok_shop_unverified_http"}:
                raise RuntimeError(f"unexpected scene06 board mode: {board.get('data_source_mode')}")
            if not board.get("rows"):
                raise RuntimeError("scene06 board rows missing after HTTP sync")
            return {
                "source": shop_sync.get("source"),
                "mode": board.get("data_source_mode"),
                "rows": len(board.get("rows") or []),
            }
    finally:
        server.shutdown()
        thread.join(timeout=2)


def validate_shop_official_metadata_reject() -> dict:
    import os

    server, thread, base = run_mock_server()
    try:
        MockHandler.include_shop_source_metadata = False
        os.environ["TIKTOK_SHOP_HTTP_URL"] = base
        capture_root = skill_root() / "testdata" / "validation" / "tmp-shop-metadata-reject"
        capture_root.mkdir(parents=True, exist_ok=True)
        result = sync_competitor_products(
            capture_root,
            keyword="beauty",
            force_refresh=True,
            source_mode="http",
            http_url=base,
            source_attestation="official",
            require_verified_source=True,
        )
        if result.get("status") != "blocked" or result.get("reason") != "invalid-source-metadata":
            raise RuntimeError(f"expected invalid-source-metadata block, got: {result}")
        return {"blocked": True, "reason": result.get("reason")}
    finally:
        MockHandler.include_shop_source_metadata = True
        server.shutdown()
        thread.join(timeout=2)


def validate_shop_official_metadata_accept() -> dict:
    import os

    server, thread, base = run_mock_server()
    try:
        os.environ["TIKTOK_SHOP_HTTP_URL"] = base
        capture_root = skill_root() / "testdata" / "validation" / "tmp-shop-metadata-accept"
        capture_root.mkdir(parents=True, exist_ok=True)
        result = sync_competitor_products(
            capture_root,
            keyword="beauty",
            force_refresh=True,
            source_mode="http",
            http_url=base,
            source_attestation="official",
            require_verified_source=True,
        )
        if result.get("status") != "ok":
            raise RuntimeError(f"official metadata sync failed: {result}")
        validation = (result.get("meta") or {}).get("source_metadata_validation") or {}
        if not validation.get("ok"):
            raise RuntimeError(f"metadata validation missing ok flag: {result}")
        return {"products": result.get("product_count"), "source": result.get("source")}
    finally:
        server.shutdown()
        thread.join(timeout=2)


def validate_scene06_verified_source_guard() -> dict:
    import tempfile

    fixture_root = skill_root() / "testdata" / "validation" / "captures" / "scene01-strong-inputs-pass"
    with tempfile.TemporaryDirectory(prefix="tgo-scene06-guard-") as temp_dir:
        output_root = Path(temp_dir) / "scene06_guard_run"
        command = [
            sys.executable,
            str(skill_root() / "scripts" / "start_capture_pack_run.py"),
            "--scene",
            "06",
            "--capture-root",
            str(fixture_root),
            "--name",
            "validation-scene06-guard",
            "--project",
            "TikTok Validation Scene 06 Guard",
            "--platform",
            "TikTok",
            "--market",
            "US",
            "--formats",
            "md",
            "--shop-sync",
            "--shop-source-mode",
            "http",
            "--shop-require-verified-source",
            "--output-root",
            str(output_root),
        ]
        completed = subprocess.run(command, text=True, capture_output=True, encoding="utf-8", check=False)
        if completed.returncode == 0:
            raise RuntimeError("scene06 verified-source guard should have blocked unverified sync")
        joined = f"{completed.stdout}\n{completed.stderr}"
        if "unverified-shop-source" not in joined:
            raise RuntimeError(f"scene06 verified-source guard returned unexpected output: {joined}")
        return {"blocked": True}


def validate_shop_gateway_partner_mock() -> dict:
    import os

    root = skill_root()
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    os.environ["SHOP_GATEWAY_PARTNER_MOCK"] = "1"
    os.environ["SHOP_GATEWAY_BACKEND"] = "partner"

    from fastapi.testclient import TestClient

    from services.shop_gateway.app import app  # noqa: WPS433

    client = TestClient(app)
    response = client.post("/v1/shop/products/search", json={"keyword": "velvet", "region": "US", "limit": 5})
    if response.status_code != 200:
        raise RuntimeError(f"partner mock gateway returned {response.status_code}: {response.text}")
    body = response.json()
    if not body.get("products"):
        raise RuntimeError(f"partner mock gateway returned no products: {body}")
    source = body.get("source") or {}
    if source.get("source_type") != "official":
        raise RuntimeError(f"partner mock source metadata unexpected: {source}")
    if source.get("auth_mode") != "merchant_oauth":
        raise RuntimeError(f"partner mock auth_mode unexpected: {source}")
    return {"products": len(body["products"]), "provider": body.get("provider")}


def validate_renderer_http() -> dict:
    import os

    server, thread, base = run_mock_server()
    try:
        os.environ["GENERATION_RENDERER_URL"] = base
        capture_root = skill_root() / "testdata" / "validation" / "tmp-renderer-http"
        capture_root.mkdir(parents=True, exist_ok=True)
        write_handoff = capture_root / "production_spec_handoff.json"
        write_handoff.write_text(
            json.dumps({"generator_branches": {"sora": {"style": "mock", "shots": []}}}, ensure_ascii=False),
            encoding="utf-8",
        )
        job = create_generation_job(
            capture_root,
            scene_id="09",
            project="integration-test",
            brief_summary="mock brief",
            backend_hint="sora",
        )
        submit = submit_generation_job(capture_root, job["job_id"])
        if submit.get("status") not in {"submitted", "pending", "running"}:
            raise RuntimeError(f"submit failed: {submit}")
        polled = poll_generation_job(capture_root, job["job_id"])
        if polled.get("status") != "succeeded":
            polled = poll_generation_job_remote(capture_root, job["job_id"])
        if polled.get("status") != "succeeded":
            raise RuntimeError(f"poll did not succeed: {polled}")
        return {"job_id": job["job_id"], "status": polled.get("status"), "links": len(polled.get("artifact_links") or [])}
    finally:
        server.shutdown()
        thread.join(timeout=2)


def main() -> None:
    results = {
        "shop_http": validate_shop_http(),
        "shop_official_metadata_accept": validate_shop_official_metadata_accept(),
        "shop_official_metadata_reject": validate_shop_official_metadata_reject(),
        "scene06_capture_run_http": validate_scene06_capture_run_http(),
        "scene06_verified_source_guard": validate_scene06_verified_source_guard(),
        "shop_gateway_partner_mock": validate_shop_gateway_partner_mock(),
        "renderer_http": validate_renderer_http(),
    }
    print(json.dumps({"ok": True, "results": results}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False), file=__import__("sys").stderr)
        raise SystemExit(1) from exc
