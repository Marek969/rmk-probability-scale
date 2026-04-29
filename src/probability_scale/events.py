"""Transform dataset metadata and anchors into comparable probabilities."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Iterable

from .data_fetch import DatasetSummary


@dataclass(frozen=True)
class ProbabilityEvent:
    """Single event on probability scale."""

    event: str
    probability: float
    source: str
    details: str
    year: int | None


def portal_catalog_events(datasets: list[DatasetSummary]) -> list[ProbabilityEvent]:
    """Build probability events from andmed.eesti.ee catalog-level properties."""

    if not datasets:
        raise ValueError("No datasets fetched from andmed.eesti.ee")

    total = len(datasets)
    now = datetime.now(timezone.utc)

    public_count = sum(1 for d in datasets if d.access == "PUBLIC")
    completed_count = sum(1 for d in datasets if d.status == "COMPLETED")
    english_title_count = sum(1 for d in datasets if d.title_en is not None and d.title_en.strip() != "")
    working_access_url_count = sum(1 for d in datasets if d.access_url_broken is False)
    org_count = sum(1 for d in datasets if d.has_organization)

    updated_recently_count = 0
    for d in datasets:
        if not d.updated_at:
            continue
        updated = datetime.fromisoformat(d.updated_at.replace("Z", "+00:00"))
        if (now - updated).days <= 365:
            updated_recently_count += 1

    return [
        ProbabilityEvent(
            event="Random portal dataset has public access",
            probability=public_count / total,
            source="andmed.eesti.ee /api/datasets",
            details=f"{public_count}/{total}",
            year=None,
        ),
        ProbabilityEvent(
            event="Random portal dataset status is COMPLETED",
            probability=completed_count / total,
            source="andmed.eesti.ee /api/datasets",
            details=f"{completed_count}/{total}",
            year=None,
        ),
        ProbabilityEvent(
            event="Random portal dataset has English title metadata",
            probability=english_title_count / total,
            source="andmed.eesti.ee /api/datasets",
            details=f"{english_title_count}/{total}",
            year=None,
        ),
        ProbabilityEvent(
            event="Random portal dataset has non-broken access URL",
            probability=working_access_url_count / total,
            source="andmed.eesti.ee /api/datasets",
            details=f"{working_access_url_count}/{total}",
            year=None,
        ),
        ProbabilityEvent(
            event="Random portal dataset has organization metadata",
            probability=org_count / total,
            source="andmed.eesti.ee /api/datasets",
            details=f"{org_count}/{total}",
            year=None,
        ),
        ProbabilityEvent(
            event="Random portal dataset was updated in last 365 days",
            probability=updated_recently_count / total,
            source="andmed.eesti.ee /api/datasets",
            details=f"{updated_recently_count}/{total}",
            year=None,
        ),
    ]


def reference_events() -> list[ProbabilityEvent]:
    """Provide simple non-country anchors to improve probability intuition."""

    return [
        ProbabilityEvent(
            event="Flip a fair coin 4 times and get heads every time",
            probability=(0.5**4),
            source="Exact calculation",
            details="(1/2)^4",
            year=None,
        ),
        ProbabilityEvent(
            event="Roll a fair die and get a six",
            probability=(1.0 / 6.0),
            source="Exact calculation",
            details="1/6",
            year=None,
        ),
        ProbabilityEvent(
            event="Be born on leap day (Feb 29)",
            probability=(1.0 / 1461.0),
            source="Calendar approximation",
            details="~1 day in 4 years",
            year=None,
        ),
    ]


def validate(events: Iterable[ProbabilityEvent]) -> list[ProbabilityEvent]:
    """Validate and return events sorted by probability."""

    checked = []
    for event in events:
        if not (0.0 < event.probability <= 1.0):
            raise ValueError(f"Invalid probability for event: {event}")
        checked.append(event)

    return sorted(checked, key=lambda e: e.probability)


def to_records(events: Iterable[ProbabilityEvent]) -> list[dict[str, object]]:
    """Serialize event objects for DataFrame/CSV export."""

    return [asdict(e) for e in events]
