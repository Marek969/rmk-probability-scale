"""Helpers to fetch raw data from official Estonia open-data sources.

This module downloads dataset URLs and persists the raw response into
`data/raw/` for reproducibility.
"""

from __future__ import annotations

from pathlib import Path
import json
from typing import Any

import requests

RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {"User-Agent": "rmk-probability-scale/0.1 (+https://github.com/)"}


def _write_text(url: str, out_name: str, timeout: int = 30) -> Path:
    """Fetch a text endpoint and persist it to `data/raw/`."""

    resp = requests.get(url, timeout=timeout, headers=HEADERS)
    resp.raise_for_status()

    out = RAW_DIR / out_name
    out.write_text(resp.text, encoding="utf-8")
    return out


def fetch_json_to_file(url: str, out_name: str, timeout: int = 30) -> Path:
    """Fetch `url` and write raw JSON to `data/raw/{out_name}`.

    Returns the path to the written file.
    """
    resp = requests.get(url, timeout=timeout, headers=HEADERS)
    resp.raise_for_status()

    payload: Any = resp.json()
    out = RAW_DIR / out_name
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return out


def fetch_births_table() -> Path:
    """Fetch the births PxWeb landing page as raw HTML."""

    return _write_text(
        "https://andmed.stat.ee/et/stat/rahvastik__rahvastikusundmused__sunnid/RV061",
        out_name="births_RV061.html",
    )


def fetch_deaths_table() -> Path:
    """Fetch the deaths PxWeb landing page as raw HTML."""

    return _write_text(
        "https://andmed.stat.ee/et/stat/rahvastik__rahvastikusundmused__surmad/RV56",
        out_name="deaths_RV56.html",
    )


def fetch_forest_fire_csv() -> Path:
    """Fetch the current forest and landscape fires CSV."""

    return _write_text(
        "https://opendata.smit.ee/paa/csv/metsa_ja_maastikutulekahjud_jooksev_aasta.csv",
        out_name="forest_fires_current_year.csv",
    )
