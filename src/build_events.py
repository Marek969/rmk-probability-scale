"""Transform raw datasets into standardized event probabilities.

The functions here expect raw files saved by `fetch_data.py` in `data/raw/`.
They compute numerator/denominator pairs and return the final event schema.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import csv
import io
import json
from collections import Counter

RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def build_events_from_stubs() -> list[dict[str, object]]:
    """Return a small DataFrame with example events and stub numerators.

    This is useful for offline testing before the real fetcher is wired up.
    Replace the numerators with parsed values from raw JSON files.
    """
    # Fallback rows keep the pipeline runnable without raw inputs.
    rows = [
        {
            "event": "Born in Tallinn",
            "numerator": 3600,  # TODO: fill from births Tallinn 2024
            "denominator": 14000,  # TODO: births in 2024 (or relevant denom)
            "year": 2024,
            "source_url": "https://andmed.stat.ee/...",
            "notes": "placeholder data",
        },
        {
            "event": "Born near Jaanipäev (20-26 June)",
            "numerator": 320,  # TODO
            "denominator": 14000,
            "year": 2024,
            "source_url": "https://andmed.stat.ee/...",
            "notes": "placeholder",
        },
        {
            "event": "Start a new company (registered)",
            "numerator": 8200,
            "denominator": 1000000,  # adult population approx
            "year": 2024,
            "source_url": "https://ettevotjaportaal...",
            "notes": "placeholder",
        },
        {
            "event": "Injured in traffic accident",
            "numerator": 4500,
            "denominator": 1320000,
            "year": 2024,
            "source_url": "https://andmed.stat.ee/traffic",
            "notes": "placeholder",
        },
        {
            "event": "Die by drowning",
            "numerator": 41,
            "denominator": 1320000,
            "year": 2024,
            "source_url": "https://andmed.stat.ee/deaths",
            "notes": "placeholder",
        },
        {
            "event": "Forest fire occurrence (per year)",
            "numerator": 12,
            "denominator": 14000,  # could be per 1000ha; adjust later
            "year": 2024,
            "source_url": "https://andmed.stat.ee/forestfires",
            "notes": "placeholder",
        },
    ]

    for row in rows:
        row["probability"] = row["numerator"] / row["denominator"]
    return rows


def _read_forest_fire_rows() -> list[dict[str, str]]:
    """Parse the tab-separated forest fire CSV into dictionaries.

    The source is intentionally kept raw in `data/raw/` so this parser is the
    only place that knows about column names or delimiters.
    """

    path = RAW_DIR / "forest_fires_current_year.csv"
    if not path.exists():
        return []

    raw_text = path.read_text(encoding="utf-8")
    lines = raw_text.splitlines()
    if not lines:
        return []

    # The source file uses a quoted tab-delimited header.
    header = lines[0].replace('"', '').split('\t')
    reader = csv.reader(io.StringIO("\n".join(lines[1:])), delimiter='\t', quotechar='"')

    rows: list[dict[str, str]] = []
    for row in reader:
        if not row:
            continue
        cleaned = [cell.strip().strip('"') for cell in row]
        if len(cleaned) != len(header):
            # Skip rows that do not match the header width.
            continue
        rows.append(dict(zip(header, cleaned)))
    return rows


def build_events_from_raw() -> list[dict[str, object]]:
    """Parse the raw JSON files and compute the final DataFrame.

    Each dataset has its own shape, so keep parsing code explicit.
    """
    forest_rows = _read_forest_fire_rows()
    if not forest_rows:
        return build_events_from_stubs()

    # Derive counts from the current-year forest fire file.
    fire_days = {row.get("sundmuse_kuupaev_dt") for row in forest_rows if row.get("sundmuse_kuupaev_dt")}
    total_fire_days = len(fire_days)
    total_fires = len(forest_rows)
    by_region = Counter(row.get('maakond', 'unknown') for row in forest_rows)
    harju_fires = by_region.get('Harju maakond', 0)

    rows = [
        {
            "event": "Forest fire happens on a random day",
            "numerator": total_fire_days,
            "denominator": 365,
            "year": 2026,
            "source_url": "https://opendata.smit.ee/paa/csv/metsa_ja_maastikutulekahjud_jooksev_aasta.csv",
            "notes": "probability estimated from distinct fire days in the current year",
        },
        {
            "event": "A forest fire is in Harju county",
            "numerator": harju_fires,
            "denominator": total_fires,
            "year": 2026,
            "source_url": "https://opendata.smit.ee/paa/csv/metsa_ja_maastikutulekahjud_jooksev_aasta.csv",
            "notes": "conditional probability among observed forest fires",
        },
    ]

    for row in rows:
        # Convert counts to probabilities for the output table.
        row["probability"] = row["numerator"] / row["denominator"]
    return rows


def write_events_csv(rows: list[dict[str, object]], out_path: Path) -> Path:
    """Write the final event rows to CSV using the standard library."""

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["event", "probability", "numerator", "denominator", "year", "source_url", "notes"]
    with out_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})
    return out_path
