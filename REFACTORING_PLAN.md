# Test-Driven Refactoring Plan for dhlab-app-ner

## Summary

This document outlines the test suite created to support safe refactoring of `app.py`.

## ✅ What We've Created

### 1. Test Infrastructure
- **pytest** setup with fixtures
- **26 comprehensive tests** covering all helper functions
- All tests currently **passing** ✅

### 2. Helper Module (`app_helpers.py`)
Created a new module with extracted utility functions:

#### Constants
- `NER_OPTIONS` - List of NER analysis types
- `POS_OPTIONS` - List of POS analysis types

#### URN Processing Functions
- `extract_urns_from_text()` - Extract URNs from mixed text
- `extract_urn_id()` - Parse URN to get ID
- `generate_default_filename()` - Create filename from URN + page range
- `ensure_xlsx_extension()` - Validate filename extension

#### Data Processing Functions
- `generate_choices_from_corpus()` - Format corpus data for UI
- `create_ner_label_mapping()` - Map NER results to Norwegian labels
- `create_pos_label_mapping()` - Map POS results to Norwegian labels
- `process_ner_analysis()` - Complete NER processing pipeline
- `process_pos_analysis()` - Complete POS processing pipeline

#### Validation Functions
- `validate_page_range()` - Validate and adjust page ranges
- `get_selection_options()` - Get options based on analysis type

### 3. Test Coverage

#### test_helpers.py (16 tests)
- URN extraction from various text formats
- Label mapping for both NER and POS
- Corpus choices generation
- Filename handling and validation
- URN parsing

#### test_analysis.py (8 tests)
- NER and POS analysis processing (with mocks)
- Page range validation edge cases
- Filename generation from URN data

#### test_constants.py (3 tests)
- Verification of constant values
- Selection option retrieval logic

## 📋 Next Steps for Refactoring

### Phase 1: Extract Corpus Definition Logic
**Function to create:** `define_corpus_from_ui()`
- Handles all three corpus definition methods
- Returns: `(corpus_defined, corpus, choices)`

### Phase 2: Extract UI Components
**Functions to create:**
- `render_text_selection_ui(choices)` - Document selection and page range
- `render_analysis_config_ui()` - Analysis type, model, filter selection
- `display_dataframes_in_columns(types, lab_to_frame)` - Results display

### Phase 3: Refactor Main Application Flow
Update `app.py` to use the new helper functions, making the main flow:
```python
# 1. Define corpus
corpus_defined, corpus, choices = define_corpus_from_ui()

# 2. Select text and configure (if corpus defined)
if choices:
    urn, start_to, filename = render_text_selection_ui(choices)
    analyse_type, model, types = render_analysis_config_ui()
    
    # 3. Run analysis
    with st.form(key="my_form"):
        if st.form_submit_button("Analyser URN"):
            df, lab_to_frame = process_ner_analysis(...) if analyse_type == "NER" else process_pos_analysis(...)
            display_dataframes_in_columns(types, lab_to_frame)
    
    # 4. Download
    if df_defined:
        render_download_button(df, filename)
```

### Phase 4: Run Tests and Verify
After each refactoring step:
```bash
uv run pytest tests/ -v
```

## 🎯 Benefits of This Approach

1. **Safety**: Tests catch regressions immediately
2. **Confidence**: All 26 tests passing before any changes
3. **Documentation**: Tests show how functions should behave
4. **Modularity**: Functions can be tested in isolation
5. **Maintainability**: Future changes easier with clear structure

## 📊 Current Status

- ✅ Test infrastructure set up
- ✅ Helper functions implemented
- ✅ All 26 tests passing
- ⏳ Ready for refactoring `app.py`
- ⏳ Additional UI component tests needed

## Running the Tests

```bash
# Install dependencies
uv sync --dev

# Run all tests
uv run pytest tests/ -v

# Watch mode (if needed)
uv run pytest tests/ -v --watch
```

## Files Created

- `app_helpers.py` - Helper functions module
- `tests/__init__.py` - Test package
- `tests/conftest.py` - Shared fixtures
- `tests/test_helpers.py` - Utility function tests
- `tests/test_analysis.py` - Analysis processing tests
- `tests/test_constants.py` - Constants tests
- `tests/README.md` - Test documentation
- `pyproject.toml` - Updated with pytest dependencies
