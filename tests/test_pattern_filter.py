"""Tests for logslice.pattern_filter."""

import re
import pytest

from logslice.pattern_filter import (
    compile_pattern,
    filter_by_pattern,
    line_matches,
)


class TestCompilePattern:
    def test_basic_regex(self):
        p = compile_pattern(r"\d+")
        assert p.search("error 42")

    def test_plain_string_escapes_special_chars(self):
        p = compile_pattern("1.2.3", use_regex=False)
        # Dot should be treated literally, not as wildcard
        assert p.search("1.2.3")
        assert not p.search("1x2y3")

    def test_ignore_case_flag(self):
        p = compile_pattern("ERROR", ignore_case=True)
        assert p.search("error: disk full")
        assert p.search("Error: disk full")

    def test_case_sensitive_by_default(self):
        p = compile_pattern("ERROR")
        assert not p.search("error: disk full")

    def test_returns_compiled_pattern(self):
        p = compile_pattern("foo")
        assert isinstance(p, re.Pattern)


class TestLineMatches:
    def test_match_returns_true(self):
        p = re.compile("WARN")
        assert line_matches("2024-01-01 WARN something", p) is True

    def test_no_match_returns_false(self):
        p = re.compile("WARN")
        assert line_matches("2024-01-01 INFO something", p) is False

    def test_invert_flips_result(self):
        p = re.compile("DEBUG")
        assert line_matches("INFO line", p, invert=True) is True
        assert line_matches("DEBUG line", p, invert=True) is False


class TestFilterByPattern:
    LINES = [
        "INFO  server started\n",
        "DEBUG loading config\n",
        "ERROR connection refused\n",
        "INFO  request received\n",
        "WARN  slow query\n",
    ]

    def test_none_pattern_yields_all(self):
        result = list(filter_by_pattern(self.LINES, None))
        assert result == self.LINES

    def test_filters_matching_lines(self):
        p = re.compile("ERROR|WARN")
        result = list(filter_by_pattern(self.LINES, p))
        assert len(result) == 2
        assert all("ERROR" in l or "WARN" in l for l in result)

    def test_invert_excludes_matching_lines(self):
        p = re.compile("DEBUG")
        result = list(filter_by_pattern(self.LINES, p, invert=True))
        assert all("DEBUG" not in l for l in result)
        assert len(result) == 4

    def test_no_matches_returns_empty(self):
        p = re.compile("CRITICAL")
        result = list(filter_by_pattern(self.LINES, p))
        assert result == []

    def test_empty_input_returns_empty(self):
        p = re.compile("ERROR")
        result = list(filter_by_pattern([], p))
        assert result == []
