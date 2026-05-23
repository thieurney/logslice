"""Tests for logslice.cli_severity."""

import argparse

import pytest

from logslice.cli_severity import (
    add_severity_args,
    apply_severity_filter,
    validate_severity_args,
)


def _make_args(**kwargs) -> argparse.Namespace:
    defaults = {"min_level": None, "include_unlevelled": False}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


class TestAddSeverityArgs:
    def test_adds_min_level_argument(self):
        parser = argparse.ArgumentParser()
        add_severity_args(parser)
        args = parser.parse_args(["--min-level", "ERROR"])
        assert args.min_level == "ERROR"

    def test_adds_include_unlevelled_flag(self):
        parser = argparse.ArgumentParser()
        add_severity_args(parser)
        args = parser.parse_args(["--include-unlevelled"])
        assert args.include_unlevelled is True

    def test_defaults_are_none_and_false(self):
        parser = argparse.ArgumentParser()
        add_severity_args(parser)
        args = parser.parse_args([])
        assert args.min_level is None
        assert args.include_unlevelled is False


class TestValidateSeverityArgs:
    def test_no_min_level_is_valid(self):
        assert validate_severity_args(_make_args()) == []

    def test_valid_level_is_accepted(self):
        assert validate_severity_args(_make_args(min_level="WARNING")) == []

    def test_invalid_level_returns_error(self):
        errors = validate_severity_args(_make_args(min_level="VERBOSE"))
        assert len(errors) == 1
        assert "VERBOSE" in errors[0]


class TestApplySeverityFilter:
    _LINES = [
        "[DEBUG] startup",
        "[INFO] ready",
        "[ERROR] failure",
        "plain line",
    ]

    def test_no_min_level_returns_all_lines(self):
        args = _make_args()
        result = list(apply_severity_filter(iter(self._LINES), args))
        assert result == self._LINES

    def test_min_error_filters_correctly(self):
        args = _make_args(min_level="ERROR")
        result = list(apply_severity_filter(iter(self._LINES), args))
        assert result == ["[ERROR] failure"]

    def test_include_unlevelled_passes_plain_lines(self):
        args = _make_args(min_level="INFO", include_unlevelled=True)
        result = list(apply_severity_filter(iter(self._LINES), args))
        assert "plain line" in result
        assert "[DEBUG] startup" not in result
