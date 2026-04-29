"""Load and normalize dataset metadata from andmed.eesti.ee."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

import requests

BASE_URL = "https://andmed.eesti.ee/api/datasets"
DEFAULT_HEADERS = {"User-Agent": "Mozilla/5.0 (rmk-probability-scale)"}


@dataclass(frozen=True)
class DatasetSummary:
    """Dataset summary row returned by andmed.eesti.ee list endpoint."""

    dataset_id: str
    slug: str
    title: str
    title_en: str | None
    access: str | None
    status: str | None
    access_url_broken: bool | None
    has_organization: bool
    created_at: str
    updated_at: str


def _page_url(page: int, limit: int) -> str:
    return f"{BASE_URL}?page={page}&limit={limit}"


def fetch_dataset_page(page: int, limit: int, timeout_seconds: int = 30) -> dict[str, Any]:
    """Fetch one page from the Estonian data portal datasets endpoint."""

    url = _page_url(page=page, limit=limit)
    response = requests.get(url, timeout=timeout_seconds, headers=DEFAULT_HEADERS)
    response.raise_for_status()
    payload: dict[str, Any] = response.json()
    if "data" not in payload or "metadata" not in payload:
        raise ValueError("Unexpected datasets response format")
    return payload


def save_raw_pages(limit: int, out_dir: Path, timeout_seconds: int = 30) -> list[Path]:
    """Persist every list page payload to raw JSON files for traceability."""

    out_dir.mkdir(parents=True, exist_ok=True)
    first = fetch_dataset_page(page=1, limit=limit, timeout_seconds=timeout_seconds)
    total = int(first["metadata"]["total"])
    pages = (total + limit - 1) // limit

    written = []
    first_path = out_dir / "andmed_datasets_page_1.json"
    first_path.write_text(json.dumps(first, indent=2), encoding="utf-8")
    written.append(first_path)

    for page in range(2, pages + 1):
        payload = fetch_dataset_page(page=page, limit=limit, timeout_seconds=timeout_seconds)
        out_file = out_dir / f"andmed_datasets_page_{page}.json"
        out_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        written.append(out_file)

    return written


def fetch_all_datasets(limit: int = 200, timeout_seconds: int = 30) -> list[DatasetSummary]:
    """Fetch all dataset summary rows from andmed.eesti.ee."""

    first = fetch_dataset_page(page=1, limit=limit, timeout_seconds=timeout_seconds)
    total = int(first["metadata"]["total"])
    pages = (total + limit - 1) // limit

    rows: list[dict[str, Any]] = list(first["data"])
    for page in range(2, pages + 1):
        payload = fetch_dataset_page(page=page, limit=limit, timeout_seconds=timeout_seconds)
        rows.extend(payload["data"])

    datasets = []
    for row in rows:
        datasets.append(
            DatasetSummary(
                dataset_id=str(row.get("id", "")),
                slug=str(row.get("slug", "")),
                title=str(row.get("title", "")),
                title_en=row.get("titleEn"),
                access=row.get("access"),
                status=row.get("status"),
                access_url_broken=row.get("accessUrlBroken"),
                has_organization=row.get("organization") is not None,
                created_at=str(row.get("createdAt", "")),
                updated_at=str(row.get("updatedAt", "")),
            )
        )

    return datasets
