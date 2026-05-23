"""Integration tests: severity filter wired through filter_by_severity + cli helpers."""

from logslice.severity_filter import filter_by_severity
from logslice.cli_severity import apply_severity_filter
import argparse

_SAMPLE_LOG = [
    "2024-03-01T10:00:00 DEBUG  booting",
    "2024-03-01T10:00:01 INFO   service ready",
    "2024-03-01T10:00:02 WARNING high cpu",
    "2024-03-01T10:00:03 ERROR  connection lost",
    "2024-03-01T10:00:04 CRITICAL disk full",
    "2024-03-01T10:00:05 continuation line with no level",
]


def test_pipeline_debug_passes_all_levelled():
    result = list(filter_by_severity(_SAMPLE_LOG, "DEBUG"))
    # All lines with a level token should pass; unlevelled is excluded by default
    assert len(result) == 5


def test_pipeline_warning_and_above():
    result = list(filter_by_severity(_SAMPLE_LOG, "WARNING"))
    assert len(result) == 3
    assert all(any(lvl in r for lvl in ("WARNING", "ERROR", "CRITICAL")) for r in result)


def test_pipeline_with_include_unlevelled():
    result = list(filter_by_severity(_SAMPLE_LOG, "ERROR", include_unlevelled=True))
    assert "2024-03-01T10:00:05 continuation line with no level" in result
    assert "2024-03-01T10:00:03 ERROR  connection lost" in result
    assert "2024-03-01T10:00:01 INFO   service ready" not in result


def test_apply_severity_filter_via_namespace():
    ns = argparse.Namespace(min_level="CRITICAL", include_unlevelled=False)
    result = list(apply_severity_filter(iter(_SAMPLE_LOG), ns))
    assert result == ["2024-03-01T10:00:04 CRITICAL disk full"]


def test_apply_severity_filter_no_level_passthrough():
    ns = argparse.Namespace(min_level=None, include_unlevelled=False)
    result = list(apply_severity_filter(iter(_SAMPLE_LOG), ns))
    assert result == _SAMPLE_LOG
