# Thoughts and tradeoffs

This document records the main design decisions and tradeoffs for the RMK
probability scale challenge.

## Why Estonia-centric events

- The brief explicitly encourages Estonian open data; the implementation uses
  local datasets.

## Event selection

- The initial commit included one real file-backed source, two derived events,
  and a readable pipeline.
- Statistikaamet tables for births, deaths, causes, and transport accidents
  were the next sources considered.

## Methodology

P(event) = numerator / denominator

Where numerator and denominator are chosen to reflect the population at risk
for the given event in the same year (2024).

For the current first increment, the forest-fire CSV is used to estimate:

- probability of a fire on a random day in the current year
- probability that an observed fire is in Harju county

## Open items

1. Wire actual Statistikaamet endpoints in `src/fetch_data.py`.
2. Implement parsers in `src/build_events.py` to extract counts.
3. Add 95% binomial confidence intervals for low-frequency events.
4. Produce the final graphic and create 5–7 focused commits.
