"""Tests for the logslice CLI entry point."""

import io
import textwrap
from unittest import TestCase
from unittest.mock import patch

from logslice.cli import run


SAMPLE_LOG = textwrap.dedent("""\
    2024-01-10T08:00:00 INFO  server started
    2024-01-10T09:00:00 INFO  request received
    2024-01-10T10:00:00 WARN  slow response
    2024-01-10T11:00:00 ERROR connection dropped
    2024-01-10T12:00:00 INFO  server stopped
""")


def _make_log_stream(content: str = SAMPLE_LOG):
    return io.StringIO(content)


class TestCliArgParsing(TestCase):
    def test_invalid_start_returns_exit_code_2(self):
        code = run(["-s", "not-a-date", "-"])
        self.assertEqual(code, 2)

    def test_invalid_end_returns_exit_code_2(self):
        code = run(["-e", "not-a-date", "-"])
        self.assertEqual(code, 2)

    def test_start_after_end_returns_exit_code_2(self):
        code = run(["-s", "2024-01-10T12:00:00", "-e", "2024-01-10T08:00:00", "-"])
        self.assertEqual(code, 2)

    def test_missing_file_returns_exit_code_1(self):
        code = run(["/nonexistent/path/to/logfile.log"])
        self.assertEqual(code, 1)


class TestCliOutput(TestCase):
    def _run_with_log(self, argv, log_content=SAMPLE_LOG):
        stream = _make_log_stream(log_content)
        captured = io.StringIO()
        with patch("logslice.log_reader._open_source", return_value=stream), \
             patch("sys.stdout", captured):
            code = run(argv)
        return code, captured.getvalue()

    def test_no_filters_returns_all_lines(self):
        code, output = self._run_with_log(["-"])
        self.assertEqual(code, 0)
        self.assertEqual(output.count("\n"), 5)

    def test_start_filter_excludes_early_lines(self):
        code, output = self._run_with_log(["-s", "2024-01-10T10:00:00", "-"])
        self.assertEqual(code, 0)
        self.assertNotIn("server started", output)
        self.assertNotIn("request received", output)
        self.assertIn("slow response", output)
        self.assertIn("connection dropped", output)

    def test_end_filter_excludes_late_lines(self):
        code, output = self._run_with_log(["-e", "2024-01-10T10:00:00", "-"])
        self.assertEqual(code, 0)
        self.assertIn("server started", output)
        self.assertIn("slow response", output)
        self.assertNotIn("connection dropped", output)
        self.assertNotIn("server stopped", output)

    def test_start_and_end_filter(self):
        code, output = self._run_with_log(
            ["-s", "2024-01-10T09:00:00", "-e", "2024-01-10T10:00:00", "-"]
        )
        self.assertEqual(code, 0)
        self.assertNotIn("server started", output)
        self.assertIn("request received", output)
        self.assertIn("slow response", output)
        self.assertNotIn("connection dropped", output)

    def test_returns_zero_on_success(self):
        code, _ = self._run_with_log(["-"])
        self.assertEqual(code, 0)
