"""Deduplication filter for log lines."""

from __future__ import annotations

import hashlib
from collections import OrderedDict
from typing import Iterable, Iterator, Optional


def _line_key(line: str, ignore_timestamps: bool) -> str:
    """Return a stable key for a log line, optionally stripping leading timestamp."""
    if ignore_timestamps:
        # Strip up to the first space-delimited token that looks like a timestamp
        # by skipping the first two whitespace-separated tokens (date + time).
        parts = line.split(None, 2)
        content = parts[2] if len(parts) >= 3 else line
    else:
        content = line
    return hashlib.md5(content.encode("utf-8", errors="replace")).hexdigest()


def dedup_lines(
    lines: Iterable[str],
    *,
    ignore_timestamps: bool = True,
    max_cache: Optional[int] = 10_000,
) -> Iterator[str]:
    """Yield unique log lines, dropping exact duplicates.

    Args:
        lines: Iterable of raw log line strings.
        ignore_timestamps: When True, leading timestamp tokens are excluded
            from the uniqueness key so lines that differ only by timestamp
            are considered duplicates.
        max_cache: Maximum number of seen keys to keep in memory.  Oldest
            entries are evicted when the cache is full (LRU-style via
            OrderedDict).  Pass ``None`` for an unbounded cache.
    """
    seen: OrderedDict[str, None] = OrderedDict()
    for line in lines:
        key = _line_key(line.rstrip("\n"), ignore_timestamps)
        if key in seen:
            seen.move_to_end(key)
            continue
        seen[key] = None
        if max_cache is not None and len(seen) > max_cache:
            seen.popitem(last=False)
        yield line


def count_duplicates(
    lines: Iterable[str],
    *,
    ignore_timestamps: bool = True,
) -> tuple[int, int]:
    """Return ``(total, duplicates)`` counts for *lines*."""
    seen: set[str] = set()
    total = 0
    duplicates = 0
    for line in lines:
        total += 1
        key = _line_key(line.rstrip("\n"), ignore_timestamps)
        if key in seen:
            duplicates += 1
        else:
            seen.add(key)
    return total, duplicates
