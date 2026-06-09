"""Shared helpers for the research thesis assistant scripts."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INDEX_PATH = PROJECT_ROOT / "outputs" / "literature_index.json"
MISSING = "【待补充】"
NO_LOCAL_SOURCE = "【本地文献库未检索到来源】"


def load_index(path: Path = DEFAULT_INDEX_PATH) -> dict[str, Any]:
    """Load and minimally validate the literature index."""
    if not path.exists():
        raise FileNotFoundError(
            f"未找到索引：{path}。请先运行 scripts/ingest_literature.py。"
        )
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict) or not isinstance(data.get("documents"), list):
        raise ValueError("索引格式无效：缺少 documents 数组。")
    return data


def save_text(path: Path, content: str) -> None:
    """Save UTF-8 text and create the parent directory when needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def normalize_space(text: str) -> str:
    """Collapse repeated whitespace while preserving readable text."""
    return re.sub(r"\s+", " ", text or "").strip()


def split_fragments(text: str, max_chars: int = 700) -> list[str]:
    """Split text into search-sized fragments without inventing content."""
    cleaned = normalize_space(text)
    if not cleaned:
        return []
    sentences = re.split(r"(?<=[。！？.!?；;])\s*", cleaned)
    fragments: list[str] = []
    current = ""
    for sentence in sentences:
        if not sentence:
            continue
        if current and len(current) + len(sentence) + 1 > max_chars:
            fragments.append(current)
            current = sentence
        else:
            current = f"{current} {sentence}".strip()
    if current:
        fragments.append(current)
    return fragments


def select_documents(
    documents: list[dict[str, Any]], selectors: list[str]
) -> list[dict[str, Any]]:
    """Select documents by exact id, path, file name, or unique substring."""
    if not selectors:
        return documents
    selected: list[dict[str, Any]] = []
    for selector in selectors:
        needle = selector.casefold()
        matches = [
            document
            for document in documents
            if needle
            in " ".join(
                str(document.get(field, "")).casefold()
                for field in ("id", "file_name", "relative_path", "title")
            )
        ]
        for match in matches:
            if match not in selected:
                selected.append(match)
    return selected


def markdown_escape(value: Any) -> str:
    """Make a scalar safe for a compact Markdown table cell."""
    return normalize_space(str(value or MISSING)).replace("|", r"\|")

