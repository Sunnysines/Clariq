"""FreshnessEngine – evaluates evidence freshness using a configurable temporal decay policy."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional


class FreshnessEngine:
    """Calculates freshness score (0-100) based on publication date.

    Scoring Policy (Clariq Product Assumptions):
    - Today (<= 24h): 100
    - 1-3 days: 95
    - 4-7 days: 90
    - 8-30 days: 75
    - 31-90 days: 50
    - 90+ days: 25
    - Unknown publication date: 40
    """

    DEFAULT_UNKNOWN_SCORE: float = 40.0

    @classmethod
    def calculate_score(
        cls,
        published_at: Optional[datetime],
        reference_time: Optional[datetime] = None,
    ) -> float:
        """Return freshness score from 0 to 100 without fabricating dates."""
        if published_at is None:
            return cls.DEFAULT_UNKNOWN_SCORE

        now = reference_time or datetime.now(timezone.utc)
        if published_at.tzinfo is None:
            published_at = published_at.replace(tzinfo=timezone.utc)

        delta = now - published_at
        days = delta.total_seconds() / 86400.0

        if days <= 1.0:
            return 100.0
        elif days <= 3.0:
            return 95.0
        elif days <= 7.0:
            return 90.0
        elif days <= 30.0:
            return 75.0
        elif days <= 90.0:
            return 50.0
        else:
            return 25.0
