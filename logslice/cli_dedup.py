"""CLI helpers for the --dedup / --count-dupes flags."""

from __future__ import annotations

import argparse
from typing import Iterable, Iterator

from logslice.dedup_filter import count_duplicates, dedup_lines


def add_dedup_args(parser: argparse.ArgumentParser) -> None:
    """Register deduplication-related arguments on *parser*."""
    group = parser.add_argument_group("deduplication")
    group.add_argument(
        "--dedup",
        action="store_true",
        default=False,
        help="Remove duplicate log lines from output.",
    )
    group.add_argument(
        "--dedup-keep-timestamps",
        action="store_true",
        default=False,
        help=(
            "When deduplicating, treat lines with different timestamps as "
            "distinct even if the rest of the message is identical."
        ),
    )
    group.add_argument(
        "--count-dupes",
        action="store_true",
        default=False,
        help="Print a duplicate-count summary to stderr and exit.",
    )
    group.add_argument(
        "--dedup-cache",
        type=int,
        default=10_000,
        metavar="N",
        help="Max number of line hashes to keep in memory (default: 10000).",
    )


def apply_dedup(
    lines: Iterable[str],
    args: argparse.Namespace,
) -> Iterator[str]:
    """Wrap *lines* with deduplication if requested by *args*.

    Returns the original iterable unchanged when ``--dedup`` is not set.
    """
    if not getattr(args, "dedup", False):
        yield from lines
        return

    ignore_ts = not getattr(args, "dedup_keep_timestamps", False)
    cache = getattr(args, "dedup_cache", 10_000)
    yield from dedup_lines(lines, ignore_timestamps=ignore_ts, max_cache=cache)


def report_duplicate_count(
    lines: Iterable[str],
    args: argparse.Namespace,
    out,
) -> None:
    """Print a duplicate summary for *lines* to *out* and return.

    Intended to be called when ``--count-dupes`` is active.
    """
    ignore_ts = not getattr(args, "dedup_keep_timestamps", False)
    total, dupes = count_duplicates(lines, ignore_timestamps=ignore_ts)
    unique = total - dupes
    rate = (dupes / total * 100) if total else 0.0
    out.write(
        f"lines={total}  unique={unique}  duplicates={dupes}  "
        f"dup_rate={rate:.1f}%\n"
    )
