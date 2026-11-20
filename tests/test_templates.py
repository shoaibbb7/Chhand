"""Unit tests for meter templates and custom pattern validation."""

import pytest

from app.errors import InvalidCustomPatternError, InvalidMeterError
from app.meter.templates import get_template


def test_doha_template():
    tmpl = get_template("doha")
    assert tmpl.name == "doha"
    assert tmpl.charan_targets == [13, 11, 13, 11]
    assert len(tmpl.charan_targets) == 4


def test_chaupai_template():
    tmpl = get_template("chaupai")
    assert tmpl.name == "chaupai"
    assert tmpl.charan_targets == [16, 16, 16, 16]
    assert len(tmpl.charan_targets) == 4


def test_custom_valid_pattern():
    tmpl = get_template("custom", custom_pattern=[12, 12, 14, 12])
    assert tmpl.name == "custom"
    assert tmpl.charan_targets == [12, 12, 14, 12]


def test_custom_invalid_pattern():
    # Empty pattern
    with pytest.raises(InvalidCustomPatternError):
        get_template("custom", custom_pattern=[])

    # Non-list pattern
    with pytest.raises(InvalidCustomPatternError):
        get_template("custom", custom_pattern=None)

    # Zero or negative target
    with pytest.raises(InvalidCustomPatternError):
        get_template("custom", custom_pattern=[12, 0, 14])

    with pytest.raises(InvalidCustomPatternError):
        get_template("custom", custom_pattern=[12, -2, 14])


def test_unsupported_meter():
    with pytest.raises(InvalidMeterError):
        get_template("unsupported_meter_xyz")
