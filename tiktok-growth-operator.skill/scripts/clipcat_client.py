from __future__ import annotations

import json
import os
import shutil
import subprocess
from typing import Any

from text_normalization import normalize_text


def clipcat_binary() -> str:
    return normalize_text(os.environ.get("CLIPCAT_BINARY")) or "clipcat"


def clipcat_configured() -> bool:
    if normalize_text(os.environ.get("CLIPCAT_API_KEY")):
        return True
    return shutil.which(clipcat_binary()) is not None


def run_clipcat(args: list[str], *, timeout_s: int = 90) -> dict[str, Any]:
    binary = clipcat_binary()
    command = [binary, *args]
    completed = subprocess.run(
        command,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        check=False,
        timeout=timeout_s,
        env=os.environ.copy(),
    )
    stdout = normalize_text(completed.stdout, strip=False)
    stderr = normalize_text(completed.stderr, strip=False)
    payload: object = {}
    if stdout.strip():
        try:
            payload = json.loads(stdout)
        except json.JSONDecodeError:
            payload = {"raw_stdout": stdout}
    return {
        "ok": completed.returncode == 0,
        "exit_code": completed.returncode,
        "command": command,
        "stdout": payload,
        "stderr": stderr,
    }


def _dig(payload: object, *keys: str) -> object:
    current = payload
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def _first_list(payload: object) -> list[dict]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if not isinstance(payload, dict):
        return []
    for key in ("items", "products", "data", "list", "results"):
        value = payload.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
        if isinstance(value, dict):
            nested = _first_list(value)
            if nested:
                return nested
    return []


def normalize_shop_product(raw: dict, *, source: str) -> dict:
    product_id = clean_field(
        raw,
        "product_id",
        "id",
        "item_id",
        "sku_id",
        "productId",
    )
    title = clean_field(raw, "title", "name", "product_name", "item_name")
    price = clean_field(raw, "price", "sale_price", "current_price", "min_price")
    rating = clean_field(raw, "rating", "score", "product_rating", "avg_rating")
    review_count = clean_field(raw, "review_count", "reviews", "comment_count", "reviewCount")
    sales_signal = clean_field(raw, "sales", "sold_count", "sales_count", "sales_signal", "sold")
    url = clean_field(raw, "url", "product_url", "detail_url", "link")
    return {
        "product_id": product_id or title or "unknown-product",
        "title": title or "未命名商品",
        "platform": clean_field(raw, "platform") or "TikTok Shop",
        "price": price or "待补",
        "rating": rating or "待补",
        "review_count": review_count or "待补",
        "sales_signal": sales_signal or "待补",
        "url": url,
        "evidence_source": source,
        "raw": raw,
    }


def clean_field(raw: dict, *keys: str) -> str:
    for key in keys:
        value = raw.get(key)
        if value is not None and normalize_text(value):
            return normalize_text(value)
    return ""


def search_shop_items(*, keyword: str, region: str = "US", page_token: str = "") -> dict[str, Any]:
    args = ["search_items", "--keyword", keyword, "--region", region]
    if page_token:
        args.extend(["--page-token", page_token])
    result = run_clipcat(args)
    items = _first_list(result.get("stdout"))
    products = [normalize_shop_product(item, source="clipcat_search_items") for item in items]
    result["products"] = products
    return result


def fetch_product_detail(*, product_input: str, region: str = "US") -> dict[str, Any]:
    result = run_clipcat(["product_detail", "--input", product_input, "--region", region])
    stdout = result.get("stdout")
    detail = stdout if isinstance(stdout, dict) else {}
    nested = _first_list(stdout)
    if nested:
        detail = nested[0]
    product = normalize_shop_product(detail if isinstance(detail, dict) else {}, source="clipcat_product_detail")
    result["product"] = product
    return result


def fetch_product_comments(
    *,
    product_input: str,
    region: str = "US",
    page_start: int = 1,
) -> dict[str, Any]:
    result = run_clipcat(
        [
            "product_comment",
            "--input",
            product_input,
            "--region",
            region,
            "--page-start",
            str(page_start),
        ]
    )
    comments = _first_list(result.get("stdout"))
    result["comments"] = comments
    return result


def submit_generation_task(
    *,
    task_type: str,
    prompt: str,
    model: str = "",
    duration: int = 0,
    extra_args: list[str] | None = None,
) -> dict[str, Any]:
    args = [task_type, "--prompt", prompt]
    if model:
        args.extend(["--model", model])
    if duration:
        args.extend(["--duration", str(duration)])
    if extra_args:
        args.extend(extra_args)
    return run_clipcat(args)


def query_task(*, task_id: str, task_type: str) -> dict[str, Any]:
    return run_clipcat(["query_task", "--task-id", task_id, "--type", task_type])


def extract_task_id(payload: object) -> str:
    if isinstance(payload, dict):
        for key in ("task_id", "taskId", "id", "job_id"):
            value = normalize_text(payload.get(key))
            if value:
                return value
        data = payload.get("data")
        if isinstance(data, dict):
            return extract_task_id(data)
    return ""


def extract_artifact_links(payload: object) -> list[str]:
    links: list[str] = []
    if isinstance(payload, dict):
        for key in ("video_url", "url", "download_url", "result_url", "output_url"):
            value = normalize_text(payload.get(key))
            if value.startswith("http"):
                links.append(value)
        for key in ("artifacts", "outputs", "results"):
            nested = payload.get(key)
            if isinstance(nested, list):
                for item in nested:
                    links.extend(extract_artifact_links(item))
            elif isinstance(nested, dict):
                links.extend(extract_artifact_links(nested))
        data = payload.get("data")
        if isinstance(data, (dict, list)):
            links.extend(extract_artifact_links(data))
    elif isinstance(payload, list):
        for item in payload:
            links.extend(extract_artifact_links(item))
    return list(dict.fromkeys(links))
