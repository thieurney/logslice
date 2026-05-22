"""Tests for logslice.line_filter and logslice.log_reader."""

import io
from datetime import datetime

import pytest

from logslice.line_filter import filter_lines_by_range, filter_lines_after_first_match
from logslice.log_reader import slice_log


SAMPLE_LINES = [
    "2024-01-10T08:00:00 INFO  server started\n",
    "2024-01-10T09:00:00 INFO  request received\n",
    "2024-01-10T10:00:00 WARN  slow query detected\n",
    "2024-01-10T11:00:00 ERROR database timeout\n",
    "2024-01-10T12:00:00 INFO  request received\n",
    "no timestamp here, just noise\n",
]

T08 = datetime(2024, 1, 10, 8, 0, 0)
T09 = datetime(2024, 1, 10, 9, 0, 0)
T11 = datetime(2024, 1, 10, 11, 0, 0)
T12 = datetime(2024, 1, 10, 12, 0, 0)


class TestFilterLinesByRange:
    def test_no_bounds_returns_all_timestamped(self):
        results = list(filter_lines_by_range(iter(SAMPLE_LINES)))
        assert len(results) == 5  # noise line excluded

    def test_start_bound_only(self):
        results = list(filter_lines_by_range(iter(SAMPLE_LINES), start=T09))
        assert len(results) == 4
        assert all("08:00:00" not in line for _, line in results)

    def test_end_bound_only(self):
        results = list(filter_lines_by_range(iter(SAMPLE_LINES), end=T09))
        assert len(results) == 2

    def test_both_bounds(self):
        results = list(filter_lines_by_range(iter(SAMPLE_LINES), start=T09, end=T11))
        assert len(results) == 3
        lines = [l for _, l in results]
        assert any("09:00:00" in l for l in lines)
        assert any("11:00:00" in l for l in lines)
        assert not any("08:00:00" in l for l in lines)
        assert not any("12:00:00" in l for l in lines)

    def test_line_numbers_are_correct(self):
        results = list(filter_lines_by_range(iter(SAMPLE_LINES), start=T11, end=T12))
        linenos = [n for n, _ in results]
        assert linenos == [4, 5]

    def test_unparseable_lines_skipped(self):
        noisy = ["garbage line\n", "more garbage\n"]
        results = list(filter_lines_by_range(iter(noisy)))
        assert results == []


class TestFilterLinesAfterFirstMatch:
    def test_stops_after_end(self):
        results = list(
            filter_lines_after_first_match(iter(SAMPLE_LINES), start=T08, end=T09)
        )
        assert len(results) == 2

    def test_all_in_range(self):
        results = list(
            filter_lines_after_first_match(iter(SAMPLE_LINES), start=T08, end=T12)
        )
        assert len(results) == 5


class TestSliceLog:
    def test_slice_from_file(self, tmp_path):
        log_file = tmp_path / "app.log"
        log_file.write_text("".join(SAMPLE_LINES), encoding="utf-8")
        result = slice_log(str(log_file), start=T09, end=T11)
        assert len(result) == 3

    def test_empty_result_when_no_match(self, tmp_path):
        log_file = tmp_path / "empty.log"
        log_file.write_text("".join(SAMPLE_LINES), encoding="utf-8")
        future = datetime(2030, 1, 1)
        result = slice_log(str(log_file), start=future)
        assert result == []
