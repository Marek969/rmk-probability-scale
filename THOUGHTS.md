# Notes and Decisions

## Why Estonia

The assignment asks for Estonian open data, so the project uses Rescue Board fire
data linked from the Estonian Data Portal.

## Event Selection

There are 8 events in the final scale:

- 2 exact anchors: leap-day birthday and fair die
- 4 Statistics Estonia rows: drowning, traffic injuries, marriages, births in Tallinn
- 2 Rescue Board fire probabilities: Harju county and 1+ hectare

The mix keeps the scale spread out while staying easy to check. Every non-anchor
number comes from a real source and is written to the CSV with its method and source.

## Method

Each row uses a simple ratio:

```text
probability = numerator / denominator
```

The final CSV stores `source_name`, `source_url`, `method`, and `notes`, so every
value can be traced back to the source.

