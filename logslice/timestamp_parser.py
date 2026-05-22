"""Timestamp detection and parsing for structured and unstructured log lines."""

import re
from datetime import datetime
from typing import Optional

# Common log timestamp patterns ordered by specificity
TIMESTAMP_PATTERNS = [
    # ISO 8601: 2024-01-15T13:45:00.123Z or 2024-01-15T13:45:00+00:00
    (r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?', '%Y-%m-%dT%H:%M:%S'),
    # Common log format: 2024-01-15 13:45:00,123 or 2024-01-15 13:45:00.123
    (r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}[.,]\d+', '%Y-%m-%d %H:%M:%S'),
    # Simple datetime: 2024-01-15 13:45:00
    (r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', '%Y-%m-%d %H:%M:%S'),
    # Apache/nginx: 15/Jan/2024:13:45:00 +0000
    (r'\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2} [+-]\d{4}', '%d/%b/%Y:%H:%M:%S %z'),
    # Syslog: Jan 15 13:45:00
    (r'\w{3} [ \d]\d \d{2}:\d{2}:\d{2}', '%b %d %H:%M:%S'),
    # Epoch seconds (10 digits)
    (r'\b\d{10}\b', 'epoch'),
    # Epoch milliseconds (13 digits)
    (r'\b\d{13}\b', 'epoch_ms'),
]

_COMPILED_PATTERNS = [
    (re.compile(pattern), fmt) for pattern, fmt in TIMESTAMP_PATTERNS
]


def extract_timestamp(line: str) -> Optional[datetime]:
    """Extract the first recognizable timestamp from a log line.

    Args:
        line: A single log line string.

    Returns:
        A datetime object if a timestamp is found, otherwise None.
    """
    for pattern, fmt in _COMPILED_PATTERNS:
        match = pattern.search(line)
        if not match:
            continue
        raw = match.group(0)
        try:
            if fmt == 'epoch':
                return datetime.utcfromtimestamp(int(raw))
            if fmt == 'epoch_ms':
                return datetime.utcfromtimestamp(int(raw) / 1000.0)
            # Strip sub-second and timezone for formats that don't include them
            clean = raw.split(',')[0].split('.')[0].rstrip('Z')
            return datetime.strptime(clean, fmt)
        except (ValueError, OSError):
            continue
    return None


def parse_datetime_arg(value: str) -> datetime:
    """Parse a user-supplied datetime string from CLI arguments.

    Supports ISO 8601 and common shorthand formats.

    Args:
        value: A datetime string such as '2024-01-15T13:00:00' or '2024-01-15'.

    Returns:
        A datetime object.

    Raises:
        ValueError: If the string cannot be parsed.
    """
    formats = [
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%dT%H:%M',
        '%Y-%m-%d %H:%M',
        '%Y-%m-%d',
    ]
    for fmt in formats:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    raise ValueError(
        f"Cannot parse datetime '{value}'. "
        "Expected formats: YYYY-MM-DD, YYYY-MM-DDTHH:MM:SS, etc."
    )
