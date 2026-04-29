# Thoughts, tradeoffs and next steps

This document records design decisions and tradeoffs for the RMK probability
scale challenge. Keep it short and focused — reviewers read this first when
they want to understand your reasoning.

## Why Estonia-centric events

- The brief explicitly encourages Estonian open data; using local datasets
  demonstrates domain familiarity and data discovery skills.

## Event selection

- Keep the first commit intentionally small: one real file-backed source,
  two derived events, and a readable pipeline.
- Prioritize readily accessible Statistikaamet tables (births, deaths,
  causes, transport accidents) in the next steps.

## Methodology

P(event) = numerator / denominator

Where numerator and denominator are chosen to reflect the population at risk
for the given event in the same year (2024).

For the current first increment, the forest-fire CSV is used to estimate:

- probability of a fire on a random day in the current year
- probability that an observed fire is in Harju county

## Next steps

1. Wire actual Statistikaamet endpoints in `src/fetch_data.py`.
2. Implement parsers in `src/build_events.py` to extract counts.
3. Add simple 95% binomial confidence intervals for low-frequency events.
4. Produce final graphic and create 5–7 focused commits.
