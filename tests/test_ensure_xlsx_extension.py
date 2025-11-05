"""Tests for ensure_xlsx_extension function."""

from app_helpers import ensure_xlsx_extension


def test_ensure_xlsx_extension_missing():
    """Test adding .xlsx extension when missing."""
    result = ensure_xlsx_extension("myfile")
    assert result == "myfile.xlsx"


def test_ensure_xlsx_extension_present():
    """Test that existing .xlsx extension is preserved."""
    result = ensure_xlsx_extension("myfile.xlsx")
    assert result == "myfile.xlsx"


def test_ensure_xlsx_extension_other_extension():
    """Test replacing non-.xlsx extension."""
    result = ensure_xlsx_extension("myfile.xls")
    assert result == "myfile.xls.xlsx"
