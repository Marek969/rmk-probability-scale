"""Orchestrator: fetch -> build -> plot."""

from __future__ import annotations

import argparse
from pathlib import Path

from fetch_data import fetch_all_sources

OUTPUT_DIR = Path(__file__).resolve().parents[1] / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def run(fetch: bool = True) -> None:
    if fetch:
        print("Fetching raw source files")
        for path in fetch_all_sources():
            print("Fetched", path)

    from build_events import build_events_from_raw, write_events_csv
    from plot_scale import plot_probability_scale

    rows = build_events_from_raw()
    csv_out = OUTPUT_DIR / "events.csv"
    write_events_csv(rows, csv_out)
    print("Wrote", csv_out)

    png = OUTPUT_DIR / "probability_scale.png"
    plot_probability_scale(rows, png, title="Probability Scale - Estonia")
    print("Wrote", png)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fetch", action="store_true", help="Fetch raw datasets before processing")
    ap.add_argument("--fetch-only", action="store_true", help="Only fetch raw datasets and exit")
    ap.add_argument("--no-fetch", action="store_true", help="Build from existing files in data/raw/")
    args = ap.parse_args()
    if args.fetch_only:
        for path in fetch_all_sources():
            print("Fetched", path)
        return
    run(fetch=args.fetch or not args.no_fetch)


if __name__ == "__main__":
    main()
