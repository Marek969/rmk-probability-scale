"""End-to-end build script for the probability scale challenge."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from .data_fetch import BASE_URL, fetch_all_datasets, save_raw_pages
from .events import portal_catalog_events, reference_events, to_records, validate
from .plotting import build_probability_scale_figure, save_figure

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

PAGE_LIMIT = 200


def run() -> None:
    """Build the full dataset and probability-scale chart."""

    raw_files = save_raw_pages(limit=PAGE_LIMIT, out_dir=RAW_DIR)
    datasets = fetch_all_datasets(limit=PAGE_LIMIT)

    events = portal_catalog_events(datasets) + reference_events()
    ordered_events = validate(events)

    records = to_records(ordered_events)
    df = pd.DataFrame(records)

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

    csv_path = PROCESSED_DIR / "probability_events.csv"
    df.to_csv(csv_path, index=False)

    metadata = {
        "generated_by": "probability_scale.main:run",
        "rows": len(df),
        "datasets_in_catalog": len(datasets),
        "raw_pages_written": len(raw_files),
        "source": f"{BASE_URL}?page=<n>&limit={PAGE_LIMIT}",
    }
    (PROCESSED_DIR / "metadata.json").write_text(
        json.dumps(metadata, indent=2),
        encoding="utf-8",
    )

    fig = build_probability_scale_figure(df, title="Probability Scale from andmed.eesti.ee")
    save_figure(
        fig,
        out_png=OUTPUTS_DIR / "probability_scale.png",
        out_svg=OUTPUTS_DIR / "probability_scale.svg",
    )

    print(f"Saved dataset to {csv_path}")
    print(f"Saved chart to {OUTPUTS_DIR / 'probability_scale.png'}")


if __name__ == "__main__":
    run()
