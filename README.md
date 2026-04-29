# RMK Data Team Internship 2026: Probability Scale

This repository contains a reproducible Python workflow for building a probability scale: a visual list of events ordered by their probabilities, aimed at improving intuition about probability.

## Why this approach

I focused on:

- Programmatic ingestion from official Estonia open data sources.
- Clean, readable code with small modules.
- Reproducible output artifacts (CSV + metadata + charts).
- A graph style optimized for communication, not dashboard complexity.

## Data sources

Current implemented source: forest and landscape fires CSV linked from andmed.eesti.ee.

Direct CSV used:

- https://opendata.smit.ee/paa/csv/metsa_ja_maastikutulekahjud_jooksev_aasta.csv

The fetch step saves the raw CSV into `data/raw/`.

Current probability events derived from the raw fire file include:

- A forest fire happens on a random day
- A forest fire is in Harju county

Additional reference anchors (exact-calculation events):

- Rolling a six on a fair die
- Four heads in a row with a fair coin
- Birth on leap day

## Repository structure

```text
rmk-probability-scale/
  data/
    raw/
    processed/
  output/
    events.csv
    probability_scale.png
  src/
    fetch_data.py
    build_events.py
    plot_scale.py
    main.py
  pyproject.toml
  README.md
  LICENSE
```

## Run instructions

### 1) Create and activate environment

```bash
python -m venv .venv
source .venv/bin/activate
```

### 2) Install dependencies

```bash
pip install -e .
```

### 3) Build data and chart

```bash
build-scale
```

or

```bash
PYTHONPATH=src python3 -m main --fetch
```

To only download the raw file without processing:

```bash
PYTHONPATH=src python3 -m main --fetch-only
```

## Outputs

After running, you will get:

- data/raw/forest_fires_current_year.csv - saved raw CSV
- output/events.csv - final event table
- output/probability_scale.png - final figure

## Notes on interpretation

- Event probabilities are estimated from counts in the raw file.
- To improve readability, all values are mapped to a unified probability scale p in (0,1].
- The chart is on a logarithmic axis to show both rare and common events together.

## Suggested extensions

- Add births, deaths, traffic, and company-registration sources one by one.
- Add uncertainty bands and Bayesian updates by year.
- Build a notebook that narrates assumptions and trade-offs.

## License

MIT
