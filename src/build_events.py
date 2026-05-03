"""Transform raw datasets into standardized event probabilities.

The functions here expect raw files saved by `fetch_data.py` in `data/raw/`.
They compute numerator/denominator pairs and return the final event schema.
"""

from __future__ import annotations

from pathlib import Path
import csv
import io
import json
from collections import Counter

RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"
FOREST_FIRE_URL = "https://opendata.smit.ee/paa/csv/metsa_ja_maastikutulekahjud_jooksev_aasta.csv"
RV021_URL = "https://andmed.stat.ee/api/v1/en/stat/rahvastik/rahvastikunaitajad-ja-koosseis/rahvaarv-ja-rahvastiku-koosseis/RV021.PX"
TS093_URL = "https://andmed.stat.ee/api/v1/en/stat/majandus/transport/liiklusennetused/TS093.PX"
RV57_URL = "https://andmed.stat.ee/api/v1/en/stat/rahvastik/rahvastikusundmused/surmad/RV57.PX"
RV11U_URL = "https://andmed.stat.ee/api/v1/en/stat/rahvastik/rahvastikusundmused/sunnid/RV11U.PX"
RV047_URL = "https://andmed.stat.ee/api/v1/en/stat/rahvastik/rahvastikunaitajad-ja-koosseis/demograafilised-pehinaitajad/RV047.PX"


def _require_raw_file(name: str) -> Path:
    """Return a raw-data path or fail with a reproducibility hint."""
    path = RAW_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"Missing {path}. Run `PYTHONPATH=src python3 -m main --fetch` first.")
    return path


def _read_json(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected object payload in {path}")
    return payload


def _jsonstat_value(payload: dict[str, object], selections: dict[str, str]) -> float:
    """Extract a single value from JSON-stat2 by dimension code values."""
    ids = payload["id"]
    sizes = payload["size"]
    dimensions = payload["dimension"]
    values = payload["value"]
    if not isinstance(ids, list) or not isinstance(sizes, list) or not isinstance(values, list):
        raise ValueError("Unexpected JSON-stat2 payload layout")

    stride = 1
    strides: dict[str, int] = {}
    for dim_id, size in reversed(list(zip(ids, sizes))):
        if not isinstance(dim_id, str):
            raise ValueError("Dimension id is not a string")
        strides[dim_id] = stride
        stride *= int(size)

    offset = 0
    for dim_id in ids:
        if not isinstance(dim_id, str):
            continue
        category_index = dimensions[dim_id]["category"]["index"]
        offset += int(category_index[selections[dim_id]]) * strides[dim_id]

    value = values[offset]
    if value is None:
        raise ValueError(f"Missing JSON-stat value for {selections}")
    return float(value)


def _event(
    event: str,
    probability: float,
    numerator: float | int,
    denominator: float | int,
    year: int,
    source_name: str,
    source_url: str,
    method: str,
    notes: str,
) -> dict[str, object]:
    """Create one normalized event row."""
    return {
        "event": event,
        "probability": probability,
        "numerator": numerator,
        "denominator": denominator,
        "year": year,
        "source_name": source_name,
        "source_url": source_url,
        "method": method,
        "notes": notes,
    }


def _read_forest_fire_rows() -> list[dict[str, str]]:
    """Parse the tab-separated forest fire CSV into dictionaries."""
    path = _require_raw_file("forest_fires_current_year.csv")
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
    """Parse raw files and compute the final probability-scale events.

    Each dataset has its own shape, so keep parsing code explicit.
    """
    forest_rows = _read_forest_fire_rows()
    if not forest_rows:
        raise ValueError("Forest-fire raw file exists but contains no parseable rows.")

    # Derive event counts from the current-year forest-fire file.
    year = int(max(row["sundmuse_kuupaev_dt"] for row in forest_rows if row.get("sundmuse_kuupaev_dt"))[:4])
    total_fires = len(forest_rows)
    by_county = Counter(row.get("maakond", "unknown") for row in forest_rows)
    harju_fires = by_county.get("Harju maakond", 0)
    population_payload = _read_json(_require_raw_file("population_RV021_2024.json"))
    traffic_payload = _read_json(_require_raw_file("traffic_injuries_TS093_2024.json"))
    drowning_payload = _read_json(_require_raw_file("drowning_rate_RV57_2024.json"))
    births_payload = _read_json(_require_raw_file("births_RV11U_2024.json"))
    marriages_payload = _read_json(_require_raw_file("marriages_RV047_2024.json"))

    def burned_area_m2(row: dict[str, str]) -> float:
        """Return burned area in the source file's numeric units."""
        forest = float(row.get("metsa_polenud_pind_alates_25_05_2021") or 0)
        landscape = float(row.get("maastiku_polenud_pind_alates_25_05_2021") or 0)
        return forest + landscape

    large_fires = sum(1 for row in forest_rows if burned_area_m2(row) >= 10_000)
    harju_fires = by_county.get("Harju maakond", 0)

    population_total = _jsonstat_value(population_payload, {"Sugu": "1", "Aasta": "2024", "Vanuserühm": "1"})
    drowning_per_100k = _jsonstat_value(
        drowning_payload,
        {"Aasta": "2024", "Surmapõhjus RHK-10 järgi": "77", "Sugu": "1", "Vanuserühm": "1"},
    )
    traffic_injuries_total = sum(float(v) for v in traffic_payload.get("value", []) if v is not None)
    total_births = _jsonstat_value(births_payload, {"Maakond": "1", "Aasta": "2024"})
    tallinn_births = _jsonstat_value(births_payload, {"Maakond": "784", "Aasta": "2024"})
    marriages_total = _jsonstat_value(marriages_payload, {"Aasta": "2024", "Näitaja": "1"})

    rows = [
        _event(
            "Being born on leap day",
            1 / 1461,
            1,
            1461,
            2024,
            "Probability benchmark",
            "",
            "one leap day in a four-year cycle",
            "exact-calculation anchor",
        ),
        _event(
            "Rolling a six on a fair die",
            1 / 6,
            1,
            6,
            2024,
            "Probability benchmark",
            "",
            "one target face on a fair six-sided die",
            "exact-calculation anchor",
        ),
        _event(
            "Being born in Tallinn",
            tallinn_births / total_births if total_births > 0 else 0,
            tallinn_births,
            total_births,
            2024,
            "Statistics Estonia (RV11U)",
            RV11U_URL,
            "Births in Tallinn divided by births in Estonia",
            "probability among live births",
        ),
        _event(
            "Getting married this year",
            marriages_total / population_total if population_total > 0 else 0,
            marriages_total,
            population_total,
            2024,
            "Statistics Estonia (RV047 + RV021)",
            RV047_URL,
            "All marriages divided by total population",
            "annual population-level probability proxy",
        ),
        _event(
            "Traffic injury during a year in Estonia",
            traffic_injuries_total / population_total if population_total > 0 else 0,
            traffic_injuries_total,
            population_total,
            2024,
            "Statistics Estonia (TS093 + RV021)",
            TS093_URL,
            "Total injured in traffic accidents divided by total population",
            "year-level risk approximation",
        ),
        _event(
            "Death by drowning during a year in Estonia",
            drowning_per_100k / 100000 if drowning_per_100k > 0 else 0,
            drowning_per_100k,
            100000,
            2024,
            "Statistics Estonia (RV57)",
            RV57_URL,
            "Published deaths per 100,000 population converted to probability",
            "cause-specific annual mortality rate",
        ),
        _event(
            "Fire occurs in Harju county",
            harju_fires / total_fires if total_fires > 0 else 0,
            harju_fires,
            total_fires,
            year,
            "Derived from Rescue Board open data",
            FOREST_FIRE_URL,
            "Harju county incidents divided by all observed fires",
            "conditional county probability among fires",
        ),
        _event(
            "Fire burns 1+ hectare",
            large_fires / total_fires if total_fires > 0 else 0,
            large_fires,
            total_fires,
            year,
            "Derived from Rescue Board open data",
            FOREST_FIRE_URL,
            "Incidents with burned area >= 10,000 m2 divided by all fires",
            "significant fire size event",
        ),
    ]

    rows = [r for r in rows if 0 < float(r["probability"]) <= 1]
    return sorted(rows, key=lambda row: float(row["probability"]))


def write_events_csv(rows: list[dict[str, object]], out_path: Path) -> Path:
    """Write the final event rows to CSV using the standard library."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "event",
        "probability",
        "numerator",
        "denominator",
        "year",
        "source_name",
        "source_url",
        "method",
        "notes",
    ]
    with out_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})
    return out_path
