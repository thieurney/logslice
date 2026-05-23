"""Tests for logslice.stats_collector."""

from datetime import datetime, timezone

import pytest

from logslice.stats_collector import SliceStats, StatsCollector


DT1 = datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
DT2 = datetime(2024, 1, 1, 10, 0, 30, tzinfo=timezone.utc)
DT3 = datetime(2024, 1, 1, 10, 1, 0, tzinfo=timezone.utc)


class TestSliceStats:
    def test_match_rate_zero_when_no_lines(self):
        stats = SliceStats()
        assert stats.match_rate == 0.0

    def test_match_rate_calculation(self):
        stats = SliceStats(total_lines_read=10, lines_matched=4)
        assert stats.match_rate == pytest.approx(0.4)

    def test_time_span_none_when_no_timestamps(self):
        stats = SliceStats()
        assert stats.time_span_seconds is None

    def test_time_span_none_when_only_first(self):
        stats = SliceStats(first_timestamp=DT1)
        assert stats.time_span_seconds is None

    def test_time_span_seconds(self):
        stats = SliceStats(first_timestamp=DT1, last_timestamp=DT3)
        assert stats.time_span_seconds == pytest.approx(60.0)


class TestStatsCollector:
    def test_initial_state_is_empty(self):
        sc = StatsCollector()
        s = sc.stats
        assert s.total_lines_read == 0
        assert s.lines_matched == 0
        assert s.lines_skipped == 0
        assert s.unparseable_lines == 0

    def test_matched_line_increments_correctly(self):
        sc = StatsCollector()
        sc.record_line(DT1, matched=True)
        s = sc.stats
        assert s.total_lines_read == 1
        assert s.lines_matched == 1
        assert s.lines_skipped == 0

    def test_unmatched_line_increments_skipped(self):
        sc = StatsCollector()
        sc.record_line(DT1, matched=False)
        assert sc.stats.lines_skipped == 1
        assert sc.stats.lines_matched == 0

    def test_unparseable_line_increments_counter(self):
        sc = StatsCollector()
        sc.record_line(None, matched=False)
        assert sc.stats.unparseable_lines == 1
        assert sc.stats.total_lines_read == 1

    def test_first_and_last_timestamp_tracking(self):
        sc = StatsCollector()
        sc.record_line(DT1, matched=True)
        sc.record_line(DT2, matched=True)
        sc.record_line(DT3, matched=True)
        assert sc.stats.first_timestamp == DT1
        assert sc.stats.last_timestamp == DT3

    def test_unparseable_does_not_update_timestamps(self):
        sc = StatsCollector()
        sc.record_line(DT1, matched=True)
        sc.record_line(None, matched=False)
        assert sc.stats.last_timestamp == DT1

    def test_reset_clears_all_state(self):
        sc = StatsCollector()
        sc.record_line(DT1, matched=True)
        sc.reset()
        s = sc.stats
        assert s.total_lines_read == 0
        assert s.first_timestamp is None
