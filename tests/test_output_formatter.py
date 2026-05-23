"""Tests for logslice.output_formatter."""

from __future__ import annotations

import io
import pytest

from logslice.output_formatter import format_line, write_lines, write_summary


class TestFormatLine:
    def test_strips_trailing_newline_by_default(self):
        assert format_line("hello\n") == "hello"

    def test_no_strip_preserves_newline(self):
        assert format_line("hello\n", strip=False) == "hello\n"

    def test_prefix_is_prepended(self):
        assert format_line("world\n", prefix=">> ") == ">> world"

    def test_empty_line(self):
        assert format_line("\n") == ""

    def test_no_newline_unchanged(self):
        assert format_line("abc") == "abc"


class TestWriteLines:
    def _buf(self) -> io.StringIO:
        return io.StringIO()

    def test_returns_line_count(self):
        buf = self._buf()
        count = write_lines(["a\n", "b\n", "c\n"], dest=buf)
        assert count == 3

    def test_content_written(self):
        buf = self._buf()
        write_lines(["foo\n", "bar\n"], dest=buf)
        assert buf.getvalue() == "foo\nbar\n"

    def test_prefix_applied_to_every_line(self):
        buf = self._buf()
        write_lines(["x\n", "y\n"], dest=buf, prefix="- ")
        assert buf.getvalue() == "- x\n- y\n"

    def test_custom_separator(self):
        buf = self._buf()
        write_lines(["a", "b"], dest=buf, separator="|")
        assert buf.getvalue() == "a|b|"

    def test_empty_iterable_returns_zero(self):
        buf = self._buf()
        count = write_lines([], dest=buf)
        assert count == 0
        assert buf.getvalue() == ""


class TestWriteSummary:
    def test_default_label(self):
        buf = io.StringIO()
        write_summary(42, dest=buf)
        assert buf.getvalue() == "42 lines matched\n"

    def test_custom_label(self):
        buf = io.StringIO()
        write_summary(7, dest=buf, label="records found")
        assert buf.getvalue() == "7 records found\n"

    def test_zero_count(self):
        buf = io.StringIO()
        write_summary(0, dest=buf)
        assert buf.getvalue() == "0 lines matched\n"
