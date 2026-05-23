"""Context-window helpers: emit N lines before/after each matching line."""

from __future__ import annotations

from collections import deque
from typing import Callable, Iterable, Iterator, List, Tuple


LinePredicate = Callable[[str], bool]


def lines_with_context(
    lines: Iterable[str],
    predicate: LinePredicate,
    before: int = 0,
    after: int = 0,
) -> Iterator[Tuple[str, bool]]:
    """Yield *(line, is_match)* tuples, honouring before/after context.

    Lines inside a context window are yielded with ``is_match=False``.
    Matched lines are yielded with ``is_match=True``.
    Duplicate lines (overlap between windows) are deduplicated by index.
    """
    before = max(0, before)
    after = max(0, after)

    buf: deque[str] = deque(maxlen=before + 1)
    pending_after: int = 0
    emitted_up_to: int = -1  # last absolute index already emitted
    history: List[Tuple[int, str]] = []  # (abs_index, line)

    abs_index = 0
    for line in lines:
        buf.append(line)
        history.append((abs_index, line))
        abs_index += 1

        if predicate(line):
            # emit before-context
            start = max(0, len(history) - len(buf))
            for rel, (idx, ctx_line) in enumerate(history[-len(buf):-1] if before else []):
                if idx > emitted_up_to:
                    yield ctx_line, False
                    emitted_up_to = idx

            # emit the match itself
            match_idx = history[-1][0]
            if match_idx > emitted_up_to:
                yield line, True
                emitted_up_to = match_idx

            pending_after = after
        elif pending_after > 0:
            cur_idx = history[-1][0]
            if cur_idx > emitted_up_to:
                yield line, False
                emitted_up_to = cur_idx
            pending_after -= 1


def collect_context_lines(
    lines: Iterable[str],
    predicate: LinePredicate,
    before: int = 0,
    after: int = 0,
) -> List[str]:
    """Convenience wrapper that returns only the line strings."""
    return [line for line, _ in lines_with_context(lines, predicate, before, after)]
