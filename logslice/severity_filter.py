"""Severity/log-level filtering for logslice."""

import re
from typing import Iterable, Iterator, List, Optional

# Ordered from lowest to highest severity
SEVERITY_LEVELS = ["DEBUG", "INFO", "WARNING", "WARN", "ERROR", "CRITICAL", "FATAL"]

# Normalise aliases to a canonical name
_CANONICAL = {
    "DEBUG": "DEBUG",
    "INFO": "INFO",
    "WARNING": "WARNING",
    "WARN": "WARNING",
    "ERROR": "ERROR",
    "CRITICAL": "CRITICAL",
    "FATAL": "CRITICAL",
}

_SEVERITY_RANK = {
    "DEBUG": 0,
    "INFO": 1,
    "WARNING": 2,
    "ERROR": 3,
    "CRITICAL": 4,
}

_LEVEL_RE = re.compile(
    r"\b(DEBUG|INFO|WARNING|WARN|ERROR|CRITICAL|FATAL)\b", re.IGNORECASE
)


def parse_severity(level: str) -> Optional[str]:
    """Return canonical severity name or None if unrecognised."""
    return _CANONICAL.get(level.upper())


def extract_severity(line: str) -> Optional[str]:
    """Return the first severity token found in *line*, or None."""
    match = _LEVEL_RE.search(line)
    if match:
        return _CANONICAL.get(match.group(0).upper())
    return None


def severity_passes(line: str, min_level: str) -> bool:
    """Return True when the line's severity is >= *min_level*."""
    canonical_min = parse_severity(min_level)
    if canonical_min is None:
        raise ValueError(f"Unknown severity level: {min_level!r}")
    line_level = extract_severity(line)
    if line_level is None:
        return False
    return _SEVERITY_RANK[line_level] >= _SEVERITY_RANK[canonical_min]


def filter_by_severity(
    lines: Iterable[str],
    min_level: str,
    include_unlevelled: bool = False,
) -> Iterator[str]:
    """Yield lines whose severity is >= *min_level*.

    If *include_unlevelled* is True, lines with no detectable severity
    token are always passed through.
    """
    canonical_min = parse_severity(min_level)
    if canonical_min is None:
        raise ValueError(f"Unknown severity level: {min_level!r}")
    min_rank = _SEVERITY_RANK[canonical_min]

    for line in lines:
        level = extract_severity(line)
        if level is None:
            if include_unlevelled:
                yield line
        elif _SEVERITY_RANK[level] >= min_rank:
            yield line
