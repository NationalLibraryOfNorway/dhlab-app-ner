# Test Suite for dhlab-app-ner

This directory contains comprehensive tests for the dhlab-app-ner application.

## Test Structure

- **`conftest.py`** - Shared test fixtures and utilities
- **`test_helpers.py`** - Tests for utility functions (URN extraction, label mapping, choices generation, filename handling)
- **`test_analysis.py`** - Tests for analysis processing (NER/POS analysis, page range validation)
- **`test_constants.py`** - Tests for application constants and configuration

## Running Tests

Install development dependencies:
```bash
uv sync --dev
```

Run all tests:
```bash
uv run pytest tests/
```

Run with verbose output:
```bash
uv run pytest tests/ -v
```

Run specific test file:
```bash
uv run pytest tests/test_helpers.py -v
```

Run specific test:
```bash
uv run pytest tests/test_helpers.py::TestURNExtraction::test_extract_urns_from_clean_text -v
```

## Test Coverage

### Helper Functions (test_helpers.py)
- ✅ URN extraction from text with various formats
- ✅ NER label mapping (Navn, Steder, Organisasjoner, Produkter, Andre)
- ✅ POS label mapping (Substantiv, Verb, Adjektiv, Preposisjon, Andre)
- ✅ Corpus choices generation
- ✅ Filename validation and .xlsx extension handling
- ✅ URN ID extraction

### Analysis Processing (test_analysis.py)
- ✅ NER analysis processing
- ✅ POS analysis processing
- ✅ Page range validation and adjustment
- ✅ Default filename generation

### Constants (test_constants.py)
- ✅ NER options constant
- ✅ POS options constant
- ✅ Selection options based on analysis type

## Current Test Status

All 26 tests are passing ✅

## Purpose

These tests ensure that:
1. The refactored code maintains the same functionality as the original
2. Helper functions work correctly in isolation
3. Edge cases are handled properly
4. Future changes don't break existing functionality

## Next Steps

After refactoring `app.py` to use the helper functions in `app_helpers.py`, run these tests to verify that everything still works correctly.
