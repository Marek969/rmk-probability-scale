"""Small helpers to fetch raw data from official Estonia open-data sources.

This module contains lightweight functions that download dataset URLs and
persist the raw response into `data/raw/` for reproducibility.

NOTE: Statistikaamet exposes many endpoints (JSON-stat, REST). For reliability
we treat the endpoint URL as an opaque parameter and persist the raw payload.
"""

from __future__ import annotations

from pathlib import Path
import json
from typing import Any

import requests

RAW_DIR = Path(__file__).resolve().parents[2] / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)


def fetch_json_to_file(url: str, out_name: str, timeout: int = 30) -> Path:
    """Fetch `url` and write raw JSON to `data/raw/{out_name}`.

    Returns the path to the written file.
    """
    headers = {"User-Agent": "rmk-probability-scale/0.1 (+https://github.com/)"}
    resp = requests.get(url, timeout=timeout, headers=headers)
    resp.raise_for_status()

    payload: Any = resp.json()
    out = RAW_DIR / out_name
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return out


def example_fetch_births(year: int = 2024) -> Path:
    """Example wrapper for fetching births data.

    Replace the URL below with the concrete Statistikaamet endpoint for births
    (e.g. a JSON-stat or REST URL). We keep the function so pipeline code is
    explicit about which datasets it expects.
    """
    # TODO: replace with the real Statistikaamet endpoint for births by region
    url = f"https://andmed.stat.ee/api/v1/some_births_endpoint?year={year}"
    return fetch_json_to_file(url, out_name=f"births_{year}.json")


def example_fetch_deaths_by_cause(year: int = 2024) -> Path:
    """Fetch mortality by cause (cardiovascular, drowning, etc.).

    Replace with the real endpoint; many mortality datasets are available via
    Statistics Estonia API (JSON-stat)."""
    url = f"https://andmed.stat.ee/api/v1/some_deaths_by_cause?year={year}"
    return fetch_json_to_file(url, out_name=f"deaths_cause_{year}.json")


def fetch_forest_fire_csv() -> Path:
    """Fetch the current forest and landscape fires CSV.

    This is a real, direct downloadable source linked from andmed.eesti.ee.
    It keeps the first commit of the data pipeline simple and readable.
    """

    url = "https://opendata.smit.ee/paa/csv/metsa_ja_maastikutulekahjud_jooksev_aasta.csv"
    headers = {"User-Agent": "rmk-probability-scale/0.1 (+https://github.com/)"}
    resp = requests.get(url, timeout=30, headers=headers)
    resp.raise_for_status()

    out = RAW_DIR / "forest_fires_current_year.csv"
    out.write_text(resp.text, encoding="utf-8")
    return out
