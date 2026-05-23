"""Tests for logslice.severity_filter."""

import pytest

from logslice.severity_filter import (
    extract_severity,
    filter_by_severity,
    parse_severity,
    severity_passes,
)


class TestParseSeverity:
    def test_known_levels_return_canonical(self):
        assert parse_severity("debug") == "DEBUG"
        assert parse_severity("WARN") == "WARNING"
        assert parse_severity("fatal") == "CRITICAL"

    def test_unknown_level_returns_none(self):
        assert parse_severity("VERBOSE") is None
        assert parse_severity("") is None


class TestExtractSeverity:
    def test_extracts_from_bracketed_token(self):
        assert extract_severity("[INFO] server started") == "INFO"

    def test_extracts_warn_alias(self):
        assert extract_severity("2024-01-01 WARN connection reset") == "WARNING"

    def test_extracts_fatal_as_critical(self):
        assert extract_severity("FATAL: out of memory") == "CRITICAL"

    def test_returns_none_when_no_level(self):
        assert extract_severity("just a plain log line") is None

    def test_case_insensitive(self):
        assert extract_severity("error: disk full") == "ERROR"


class TestSeverityPasses:
    def test_exact_match_passes(self):
        assert severity_passes("[ERROR] boom", "ERROR") is True

    def test_higher_level_passes(self):
        assert severity_passes("CRITICAL meltdown", "ERROR") is True

    def test_lower_level_fails(self):
        assert severity_passes("[DEBUG] verbose", "INFO") is False

    def test_no_level_in_line_returns_false(self):
        assert severity_passes("plain text", "INFO") is False

    def test_invalid_min_level_raises(self):
        with pytest.raises(ValueError, match="Unknown severity"):
            severity_passes("[INFO] ok", "TRACE")


class TestFilterBySeverity:
    def _lines(self):
        return [
            "[DEBUG] starting up",
            "[INFO] ready",
            "[WARNING] low memory",
            "[ERROR] disk full",
            "[CRITICAL] system failure",
            "no level here",
        ]

    def test_min_info_excludes_debug(self):
        result = list(filter_by_severity(self._lines(), "INFO"))
        assert "[DEBUG] starting up" not in result
        assert "[INFO] ready" in result

    def test_min_error_returns_error_and_critical(self):
        result = list(filter_by_severity(self._lines(), "ERROR"))
        assert result == ["[ERROR] disk full", "[CRITICAL] system failure"]

    def test_include_unlevelled_passes_plain_lines(self):
        result = list(
            filter_by_severity(self._lines(), "WARNING", include_unlevelled=True)
        )
        assert "no level here" in result

    def test_unlevelled_excluded_by_default(self):
        result = list(filter_by_severity(self._lines(), "DEBUG"))
        assert "no level here" not in result

    def test_invalid_min_level_raises(self):
        with pytest.raises(ValueError):
            list(filter_by_severity(self._lines(), "UNKNOWN"))

    def test_empty_input_yields_nothing(self):
        assert list(filter_by_severity([], "INFO")) == []
