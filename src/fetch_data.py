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
PXWEB_BASE = "https://andmed.stat.ee/api/v1/en/stat"

def _write_text(url: str, out_name: str, timeout: int = 30) -> Path:
    """Fetch a text endpoint and persist it to `data/raw/`."""
    resp = requests.get(url, timeout=timeout, headers=HEADERS)
    resp.raise_for_status()
    out = RAW_DIR / out_name
    out.write_text(resp.text, encoding="utf-8")
    return out


def fetch_forest_fire_csv() -> Path:
    """Fetch the current forest and landscape fires CSV."""
    return _write_text(
        "https://opendata.smit.ee/paa/csv/metsa_ja_maastikutulekahjud_jooksev_aasta.csv",
        out_name="forest_fires_current_year.csv",
    )


def _post_pxweb_to_file(endpoint: str, query: dict[str, Any], out_name: str, timeout: int = 30) -> Path:
    """Run a PxWeb API query and store JSON-stat2 response."""
    resp = requests.post(
        f"{PXWEB_BASE}/{endpoint}",
        json=query,
        timeout=timeout,
        headers=HEADERS,
    )
    resp.raise_for_status()
    out = RAW_DIR / out_name
    out.write_text(json.dumps(resp.json(), indent=2), encoding="utf-8")
    return out


def fetch_population_rv021() -> Path:
    """Fetch total population for Estonia (RV021, 2024)."""
    query = {
        "query": [
            {"code": "Sugu", "selection": {"filter": "item", "values": ["1"]}},
            {"code": "Aasta", "selection": {"filter": "item", "values": ["2024"]}},
            {"code": "Vanuserühm", "selection": {"filter": "item", "values": ["1"]}},
        ],
        "response": {"format": "json-stat2"},
    }
    return _post_pxweb_to_file(
        "rahvastik/rahvastikunaitajad-ja-koosseis/rahvaarv-ja-rahvastiku-koosseis/RV021.PX",
        query,
        "population_RV021_2024.json",
    )


def fetch_traffic_injuries_ts093() -> Path:
    """Fetch annual monthly traffic injuries (TS093, 2024)."""
    query = {
        "query": [
            {"code": "Näitaja", "selection": {"filter": "item", "values": ["6"]}},
            {
                "code": "Kuu",
                "selection": {
                    "filter": "item",
                    "values": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"],
                },
            },
            {"code": "Aasta", "selection": {"filter": "item", "values": ["2024"]}},
        ],
        "response": {"format": "json-stat2"},
    }
    return _post_pxweb_to_file(
        "majandus/transport/liiklusennetused/TS093.PX",
        query,
        "traffic_injuries_TS093_2024.json",
    )


def fetch_drowning_rv57() -> Path:
    """Fetch accidental drowning deaths per 100,000 (RV57, 2024)."""
    query = {
        "query": [
            {"code": "Aasta", "selection": {"filter": "item", "values": ["2024"]}},
            {"code": "Surmapõhjus RHK-10 järgi", "selection": {"filter": "item", "values": ["77"]}},
            {"code": "Sugu", "selection": {"filter": "item", "values": ["1"]}},
            {"code": "Vanuserühm", "selection": {"filter": "item", "values": ["1"]}},
        ],
        "response": {"format": "json-stat2"},
    }
    return _post_pxweb_to_file(
        "rahvastik/rahvastikusundmused/surmad/RV57.PX",
        query,
        "drowning_rate_RV57_2024.json",
    )


def fetch_births_rv11u() -> Path:
    """Fetch live births by county including Tallinn (RV11U, 2024)."""
    query = {
        "query": [
            {"code": "Maakond", "selection": {"filter": "item", "values": ["1", "784"]}},
            {"code": "Aasta", "selection": {"filter": "item", "values": ["2024"]}},
        ],
        "response": {"format": "json-stat2"},
    }
    return _post_pxweb_to_file(
        "rahvastik/rahvastikusundmused/sunnid/RV11U.PX",
        query,
        "births_RV11U_2024.json",
    )


def fetch_marriages_rv047() -> Path:
    """Fetch all marriages count (RV047, 2024)."""
    query = {
        "query": [
            {"code": "Aasta", "selection": {"filter": "item", "values": ["2024"]}},
            {"code": "Näitaja", "selection": {"filter": "item", "values": ["1"]}},
        ],
        "response": {"format": "json-stat2"},
    }
    return _post_pxweb_to_file(
        "rahvastik/rahvastikunaitajad-ja-koosseis/demograafilised-pehinaitajad/RV047.PX",
        query,
        "marriages_RV047_2024.json",
    )


def fetch_all_sources() -> list[Path]:
    """Download every raw source used by the build step."""
    return [
        fetch_forest_fire_csv(),
        fetch_population_rv021(),
        fetch_traffic_injuries_ts093(),
        fetch_drowning_rv57(),
        fetch_births_rv11u(),
        fetch_marriages_rv047(),
    ]
