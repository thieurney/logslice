"""Tests for logslice.dedup_filter."""

from __future__ import annotations

import pytest

from logslice.dedup_filter import count_duplicates, dedup_lines


LINES_WITH_TIMESTAMPS = [
    "2024-01-01 10:00:00 ERROR something broke\n",
    "2024-01-01 10:00:01 ERROR something broke\n",  # dup (ignore_timestamps=True)
    "2024-01-01 10:00:02 INFO all good\n",
    "2024-01-01 10:00:03 INFO all good\n",          # dup
    "2024-01-01 10:00:04 WARN watch out\n",
]


class TestDedupLines:
    def test_empty_input_yields_nothing(self):
        assert list(dedup_lines([])) == []

    def test_no_duplicates_returns_all(self):
        lines = ["a\n", "b\n", "c\n"]
        assert list(dedup_lines(lines)) == lines

    def test_exact_duplicates_removed(self):
        lines = ["hello\n", "hello\n", "world\n"]
        result = list(dedup_lines(lines, ignore_timestamps=False))
        assert result == ["hello\n", "world\n"]

    def test_ignore_timestamps_deduplicates_by_content(self):
        result = list(dedup_lines(LINES_WITH_TIMESTAMPS, ignore_timestamps=True))
        assert len(result) == 3
        assert result[0] == LINES_WITH_TIMESTAMPS[0]
        assert result[2] == LINES_WITH_TIMESTAMPS[2]
        assert result[4] == LINES_WITH_TIMESTAMPS[4]

    def test_keep_timestamps_treats_lines_as_unique(self):
        result = list(dedup_lines(LINES_WITH_TIMESTAMPS, ignore_timestamps=False))
        assert result == LINES_WITH_TIMESTAMPS

    def test_max_cache_evicts_old_entries(self):
        # With max_cache=2, the first key gets evicted after 3 unique lines,
        # so a repeat of line 1 should pass through again.
        lines = ["a\n", "b\n", "c\n", "a\n"]
        result = list(dedup_lines(lines, ignore_timestamps=False, max_cache=2))
        assert result == ["a\n", "b\n", "c\n", "a\n"]

    def test_unbounded_cache_removes_all_duplicates(self):
        lines = ["x\n"] * 50 + ["y\n"]
        result = list(dedup_lines(lines, ignore_timestamps=False, max_cache=None))
        assert result == ["x\n", "y\n"]

    def test_preserves_newlines_in_output(self):
        lines = ["line one\n", "line two\n"]
        result = list(dedup_lines(lines))
        assert all(r.endswith("\n") for r in result)


class TestCountDuplicates:
    def test_no_duplicates(self):
        total, dupes = count_duplicates(["a\n", "b\n", "c\n"], ignore_timestamps=False)
        assert total == 3
        assert dupes == 0

    def test_all_same(self):
        total, dupes = count_duplicates(["x\n"] * 5, ignore_timestamps=False)
        assert total == 5
        assert dupes == 4

    def test_with_timestamp_stripping(self):
        total, dupes = count_duplicates(LINES_WITH_TIMESTAMPS, ignore_timestamps=True)
        assert total == 5
        assert dupes == 2

    def test_empty_input(self):
        total, dupes = count_duplicates([], ignore_timestamps=False)
        assert total == 0
        assert dupes == 0
