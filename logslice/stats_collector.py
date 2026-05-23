"""Statistics collection for log slicing operations."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class SliceStats:
    """Holds statistics gathered during a log slice operation."""

    total_lines_read: int = 0
    lines_matched: int = 0
    lines_skipped: int = 0
    first_timestamp: Optional[datetime] = None
    last_timestamp: Optional[datetime] = None
    unparseable_lines: int = 0

    @property
    def match_rate(self) -> float:
        """Fraction of read lines that were matched (0.0 if none read)."""
        if self.total_lines_read == 0:
            return 0.0
        return self.lines_matched / self.total_lines_read

    @property
    def time_span_seconds(self) -> Optional[float]:
        """Elapsed seconds between first and last parsed timestamp, or None."""
        if self.first_timestamp is None or self.last_timestamp is None:
            return None
        return (self.last_timestamp - self.first_timestamp).total_seconds()


class StatsCollector:
    """Accumulates statistics as lines are processed."""

    def __init__(self) -> None:
        self._stats = SliceStats()

    def record_line(self, timestamp: Optional[datetime], matched: bool) -> None:
        """Record a single processed line.

        Args:
            timestamp: Parsed timestamp for the line, or None if unparseable.
            matched:   Whether the line fell within the requested range.
        """
        self._stats.total_lines_read += 1

        if timestamp is None:
            self._stats.unparseable_lines += 1
        else:
            if self._stats.first_timestamp is None:
                self._stats.first_timestamp = timestamp
            self._stats.last_timestamp = timestamp

        if matched:
            self._stats.lines_matched += 1
        else:
            self._stats.lines_skipped += 1

    @property
    def stats(self) -> SliceStats:
        """Return a snapshot of the current statistics."""
        return self._stats

    def reset(self) -> None:
        """Reset all counters to zero."""
        self._stats = SliceStats()
