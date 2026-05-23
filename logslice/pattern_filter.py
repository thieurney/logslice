"""Pattern-based line filtering using regex or plain string matching."""

import re
from typing import Iterable, Iterator, Optional


def compile_pattern(
    pattern: str,
    ignore_case: bool = False,
    use_regex: bool = True,
) -> re.Pattern:
    """Compile a pattern string into a regex Pattern object.

    Args:
        pattern: The pattern string (regex or literal).
        ignore_case: Whether to match case-insensitively.
        use_regex: If False, treat pattern as a plain substring.

    Returns:
        A compiled re.Pattern.
    """
    flags = re.IGNORECASE if ignore_case else 0
    if not use_regex:
        pattern = re.escape(pattern)
    return re.compile(pattern, flags)


def line_matches(
    line: str,
    pattern: re.Pattern,
    invert: bool = False,
) -> bool:
    """Return True if the line matches the pattern (or doesn't, if inverted).

    Args:
        line: The log line to test.
        pattern: A compiled regex pattern.
        invert: If True, return True when the line does NOT match.

    Returns:
        Boolean match result.
    """
    matched = bool(pattern.search(line))
    return not matched if invert else matched


def filter_by_pattern(
    lines: Iterable[str],
    pattern: Optional[re.Pattern],
    invert: bool = False,
) -> Iterator[str]:
    """Yield lines from *lines* that satisfy the pattern filter.

    If *pattern* is None every line is yielded unchanged.

    Args:
        lines: Iterable of raw log lines.
        pattern: Compiled regex pattern, or None to pass all lines through.
        invert: Yield lines that do NOT match when True.

    Yields:
        Matching (or non-matching) lines.
    """
    if pattern is None:
        yield from lines
        return

    for line in lines:
        if line_matches(line, pattern, invert=invert):
            yield line
