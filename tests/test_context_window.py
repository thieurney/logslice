"""Tests for logslice.context_window."""

from __future__ import annotations

import pytest

from logslice.context_window import collect_context_lines, lines_with_context


LINES = [
    "alpha\n",
    "beta\n",
    "MATCH\n",
    "delta\n",
    "epsilon\n",
]


def is_match(line: str) -> bool:
    return "MATCH" in line


class TestCollectContextLines:
    def test_no_context_returns_match_only(self):
        result = collect_context_lines(LINES, is_match)
        assert result == ["MATCH\n"]

    def test_before_context(self):
        result = collect_context_lines(LINES, is_match, before=2)
        assert result == ["alpha\n", "beta\n", "MATCH\n"]

    def test_after_context(self):
        result = collect_context_lines(LINES, is_match, after=2)
        assert result == ["MATCH\n", "delta\n", "epsilon\n"]

    def test_before_and_after_context(self):
        result = collect_context_lines(LINES, is_match, before=1, after=1)
        assert result == ["beta\n", "MATCH\n", "delta\n"]

    def test_before_larger_than_available(self):
        result = collect_context_lines(LINES, is_match, before=10)
        assert result == ["alpha\n", "beta\n", "MATCH\n"]

    def test_after_larger_than_available(self):
        result = collect_context_lines(LINES, is_match, after=10)
        assert result == ["MATCH\n", "delta\n", "epsilon\n"]

    def test_no_matches_returns_empty(self):
        result = collect_context_lines(LINES, lambda l: False, before=2, after=2)
        assert result == []

    def test_all_lines_match_no_duplicates(self):
        data = ["a\n", "b\n", "c\n"]
        result = collect_context_lines(data, lambda _: True, before=1, after=1)
        assert result == data


class TestLinesWithContext:
    def test_match_flag_set_correctly(self):
        data = ["x\n", "MATCH\n", "z\n"]
        pairs = list(lines_with_context(data, is_match, before=1, after=1))
        flags = {line.strip(): flag for line, flag in pairs}
        assert flags["MATCH"] is True
        assert flags["x"] is False
        assert flags["z"] is False

    def test_empty_input(self):
        assert list(lines_with_context([], is_match)) == []
