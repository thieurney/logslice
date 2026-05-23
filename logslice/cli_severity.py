"""CLI helpers for severity filtering integration."""

import argparse
from typing import Iterator, List

from logslice.severity_filter import SEVERITY_LEVELS, filter_by_severity, parse_severity


def add_severity_args(parser: argparse.ArgumentParser) -> None:
    """Attach severity-related arguments to *parser*."""
    parser.add_argument(
        "--min-level",
        metavar="LEVEL",
        default=None,
        help=(
            "Only output lines at or above this severity. "
            f"Choices: {', '.join(SEVERITY_LEVELS)}"
        ),
    )
    parser.add_argument(
        "--include-unlevelled",
        action="store_true",
        default=False,
        help="Pass through lines that contain no recognisable severity token.",
    )


def validate_severity_args(args: argparse.Namespace) -> List[str]:
    """Return a list of error messages; empty list means valid."""
    errors: List[str] = []
    if args.min_level is not None and parse_severity(args.min_level) is None:
        errors.append(
            f"Invalid --min-level {args.min_level!r}. "
            f"Choose from: {', '.join(SEVERITY_LEVELS)}"
        )
    return errors


def apply_severity_filter(
    lines: Iterator[str], args: argparse.Namespace
) -> Iterator[str]:
    """Apply severity filtering to *lines* based on parsed *args*.

    If ``--min-level`` is not set the original iterator is returned unchanged.
    """
    if not args.min_level:
        return lines
    return filter_by_severity(
        lines,
        min_level=args.min_level,
        include_unlevelled=args.include_unlevelled,
    )
