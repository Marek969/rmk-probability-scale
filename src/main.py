"""Orchestrator: fetch -> build -> plot

Run `python -m main` from repository root (uses PYTHONPATH=src) or
install dependencies via `pip install -r requirements.txt` and run
`python -m main`.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from fetch_data import fetch_births_table, fetch_deaths_table, fetch_forest_fire_csv

OUTPUT_DIR = Path(__file__).resolve().parents[1] / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def run(fetch: bool = False) -> None:
    if fetch:
        print("Fetching raw source pages/files")
        try:
            fetch_births_table()
            fetch_deaths_table()
            fetch_forest_fire_csv()
        except Exception as e:
            print("Fetch failed:", e)

    from build_events import build_events_from_raw, write_events_csv

    from plot_scale import plot_probability_scale

    rows = build_events_from_raw()
    csv_out = OUTPUT_DIR / "events.csv"
    write_events_csv(rows, csv_out)
    print("Wrote", csv_out)

    png = OUTPUT_DIR / "probability_scale.png"
    plot_probability_scale(rows, png, title="Probability Scale — Estonia (2024)")
    print("Wrote", png)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fetch", action="store_true", help="Fetch raw datasets before processing")
    ap.add_argument("--fetch-only", action="store_true", help="Only fetch raw datasets and exit")
    args = ap.parse_args()
    if args.fetch_only:
        fetch_births_table()
        fetch_deaths_table()
        fetch_forest_fire_csv()
        print("Fetched raw births, deaths and forest-fire sources only")
        return
    run(fetch=args.fetch)


if __name__ == "__main__":
    main()
