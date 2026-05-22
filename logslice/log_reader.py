"""High-level log reading helpers for logslice.

Ties together file I/O, encoding handling, and line filtering.
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import Iterator, Optional, Tuple

from logslice.line_filter import filter_lines_after_first_match, filter_lines_by_range


def _open_source(path: Optional[str]):
    """Return an open text stream for *path* or stdin if path is None."""
    if path is None:
        return sys.stdin
    return open(path, "r", encoding="utf-8", errors="replace")


def read_filtered(
    path: Optional[str],
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    fast: bool = True,
) -> Iterator[Tuple[int, str]]:
    """Open a log file (or stdin) and yield matching (lineno, line) tuples.

    Args:
        path:  Path to the log file, or None to read from stdin.
        start: Inclusive start timestamp filter.
        end:   Inclusive end timestamp filter.
        fast:  When True, use early-exit strategy (assumes chronological order).

    Yields:
        (1-based line number, line text) for every matching line.
    """
    filter_fn = filter_lines_after_first_match if fast else filter_lines_by_range
    source = _open_source(path)
    try:
        yield from filter_fn(source, start=start, end=end)
    finally:
        if path is not None:
            source.close()


def slice_log(
    path: Optional[str],
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    fast: bool = True,
) -> list:
    """Return a list of matching lines (without line numbers).

    Convenience wrapper around :func:`read_filtered` for small files or tests.

    Args:
        path:  Path to the log file, or None for stdin.
        start: Inclusive start bound.
        end:   Inclusive end bound.
        fast:  Enable early-exit optimisation.

    Returns:
        List of matching log line strings.
    """
    return [line for _, line in read_filtered(path, start=start, end=end, fast=fast)]
