from __future__ import annotations

import json
import unicodedata
from pathlib import Path


INVISIBLE_CONTROL_CHARS = (
    "\u200b",
    "\u200c",
    "\u200d",
    "\u200e",
    "\u200f",
    "\u202a",
    "\u202b",
    "\u202c",
    "\u202d",
    "\u202e",
    "\u2066",
    "\u2067",
    "\u2068",
    "\u2069",
)

COMMON_MOJIBAKE_REPLACEMENTS = {
    "â€™": "'",
    "â€˜": "'",
    "â€œ": '"',
    "â€": '"',
    "â€“": "-",
    "â€”": "-",
    "â€¦": "...",
    "Â ": " ",
    "Â·": "·",
    "Ã—": "×",
    "Ã©": "é",
}


def strip_invisible_controls(text: str) -> str:
    cleaned = text
    for token in INVISIBLE_CONTROL_CHARS:
        cleaned = cleaned.replace(token, "")
    return cleaned


def repair_common_mojibake(text: str) -> str:
    repaired = text
    for source, target in COMMON_MOJIBAKE_REPLACEMENTS.items():
        repaired = repaired.replace(source, target)
    return repaired


def normalize_text(value: object, *, strip: bool = True) -> str:
    if value is None:
        return ""
    text = str(value)
    text = text.replace("\ufeff", "")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = strip_invisible_controls(text)
    text = repair_common_mojibake(text)
    text = unicodedata.normalize("NFC", text)
    return text.strip() if strip else text


def normalize_nested(value: object) -> object:
    if isinstance(value, str):
        return normalize_text(value)
    if isinstance(value, list):
        return [normalize_nested(item) for item in value]
    if isinstance(value, dict):
        return {
            normalize_text(key) if isinstance(key, str) else key: normalize_nested(item)
            for key, item in value.items()
        }
    return value


def read_utf8_text(path: Path) -> str:
    return normalize_text(path.read_text(encoding="utf-8-sig"), strip=False)


def read_json_file(path: Path) -> dict | list:
    return normalize_nested(json.loads(read_utf8_text(path)))


def write_utf8_text(path: Path, text: str, *, bom: bool = False) -> None:
    normalized = normalize_text(text, strip=False)
    path.write_text(normalized, encoding="utf-8-sig" if bom else "utf-8")


def write_json_file(path: Path, payload: object, *, bom: bool = False, indent: int = 2) -> None:
    normalized_payload = normalize_nested(payload)
    write_utf8_text(
        path,
        json.dumps(normalized_payload, ensure_ascii=False, indent=indent) + "\n",
        bom=bom,
    )
