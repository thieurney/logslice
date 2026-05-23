"""Output formatting utilities for logslice."""

from __future__ import annotations

import sys
from typing import Iterable, Optional, TextIO


DEFAULT_SEPARATOR = "\n"


def format_line(line: str, *, prefix: Optional[str] = None, strip: bool = True) -> str:
    """Return a single log line, optionally stripped and prefixed."""
    text = line.rstrip("\n") if strip else line
    if prefix:
        return f"{prefix}{text}"
    return text


def write_lines(
    lines: Iterable[str],
    dest: TextIO = sys.stdout,
    *,
    prefix: Optional[str] = None,
    strip: bool = True,
    separator: str = DEFAULT_SEPARATOR,
) -> int:
    """Write formatted lines to *dest*.

    Returns the number of lines written.
    """
    count = 0
    for raw in lines:
        dest.write(format_line(raw, prefix=prefix, strip=strip))
        dest.write(separator)
        count += 1
    return count


def write_summary(
    count: int,
    dest: TextIO = sys.stderr,
    *,
    label: str = "lines matched",
) -> None:
    """Write a human-readable summary line to *dest* (default: stderr)."""
    dest.write(f"{count} {label}\n")
