"""Tests for logslice.timestamp_parser module."""

import pytest
from datetime import datetime
from logslice.timestamp_parser import extract_timestamp, parse_datetime_arg


class TestExtractTimestamp:
    def test_iso8601_with_milliseconds(self):
        line = '2024-01-15T13:45:00.123Z INFO starting service'
        result = extract_timestamp(line)
        assert result == datetime(2024, 1, 15, 13, 45, 0)

    def test_iso8601_basic(self):
        line = '[2024-03-22T08:00:00] ERROR disk full'
        result = extract_timestamp(line)
        assert result == datetime(2024, 3, 22, 8, 0, 0)

    def test_common_log_format_comma_separator(self):
        line = '2024-01-15 13:45:00,456 DEBUG connection established'
        result = extract_timestamp(line)
        assert result == datetime(2024, 1, 15, 13, 45, 0)

    def test_simple_datetime(self):
        line = '2024-06-01 00:00:01 WARN retry attempt 3'
        result = extract_timestamp(line)
        assert result == datetime(2024, 6, 1, 0, 0, 1)

    def test_apache_format(self):
        line = '127.0.0.1 - - [15/Jan/2024:13:45:00 +0000] "GET / HTTP/1.1" 200'
        result = extract_timestamp(line)
        assert result is not None
        assert result.day == 15
        assert result.month == 1

    def test_epoch_seconds(self):
        line = 'ts=1705322700 level=info msg="hello"'
        result = extract_timestamp(line)
        assert result is not None
        assert isinstance(result, datetime)

    def test_epoch_milliseconds(self):
        line = '{"time": 1705322700000, "msg": "boot"}'
        result = extract_timestamp(line)
        assert result is not None

    def test_no_timestamp_returns_none(self):
        line = 'This log line has no timestamp at all.'
        assert extract_timestamp(line) is None

    def test_empty_string_returns_none(self):
        assert extract_timestamp('') is None


class TestParseDatetimeArg:
    def test_date_only(self):
        result = parse_datetime_arg('2024-01-15')
        assert result == datetime(2024, 1, 15)

    def test_datetime_with_seconds(self):
        result = parse_datetime_arg('2024-01-15T13:45:00')
        assert result == datetime(2024, 1, 15, 13, 45, 0)

    def test_datetime_space_separator(self):
        result = parse_datetime_arg('2024-01-15 13:45:00')
        assert result == datetime(2024, 1, 15, 13, 45, 0)

    def test_datetime_minutes_only(self):
        result = parse_datetime_arg('2024-01-15T13:45')
        assert result == datetime(2024, 1, 15, 13, 45, 0)

    def test_invalid_format_raises(self):
        with pytest.raises(ValueError, match="Cannot parse datetime"):
            parse_datetime_arg('15-01-2024')

    def test_invalid_string_raises(self):
        with pytest.raises(ValueError):
            parse_datetime_arg('not-a-date')
