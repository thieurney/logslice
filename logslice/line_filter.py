"""Line-level filtering logic for logslice.

Provides utilities to filter log lines by time range using parsed timestamps.
"""

from datetime import datetime
from typing import Iterator, Optional, Tuple

from logslice.timestamp_parser import extract_timestamp


def filter_lines_by_range(
    lines: Iterator[str],
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
) -> Iterator[Tuple[int, str]]:
    """Yield (line_number, line) tuples whose timestamps fall within [start, end].

    Lines whose timestamps cannot be parsed are skipped.
    If start or end is None the respective bound is treated as open.

    Args:
        lines: Iterable of raw log lines.
        start: Inclusive lower bound (timezone-aware or naive, must match log).
        end:   Inclusive upper bound.

    Yields:
        Tuples of (1-based line number, original line string).
    """
    for lineno, line in enumerate(lines, start=1):
        ts = extract_timestamp(line)
        if ts is None:
            continue
        if start is not None and ts < start:
            continue
        if end is not None and ts > end:
            continue
        yield lineno, line


def filter_lines_after_first_match(
    lines: Iterator[str],
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
) -> Iterator[Tuple[int, str]]:
    """Like filter_lines_by_range but stops yielding once a timestamp exceeds *end*.

    Useful for large, chronologically ordered log files where early termination
    saves significant I/O.

    Args:
        lines: Iterable of raw log lines (assumed roughly chronological).
        start: Inclusive lower bound.
        end:   Inclusive upper bound; iteration stops on first line past this.

    Yields:
        Tuples of (1-based line number, original line string).
    """
    for lineno, line in enumerate(lines, start=1):
        ts = extract_timestamp(line)
        if ts is None:
            continue
        if end is not None and ts > end:
            return
        if start is not None and ts < start:
            continue
        yield lineno, line
