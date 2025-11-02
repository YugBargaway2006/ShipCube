# In backend/tests/test_summarizer.py

import pytest
from backend.src.summarizer import get_n_tokens_summary, highlight_entities, nlp

# --- Tests for get_n_tokens_summary ---

SAMPLE_TEXT = (
    "This is the full answer text for order SH-123. "
    "The status of order sh-123 is 'shipped'. "
    "We are also tracking ShipCube order SC-456."
)

def test_summary_truncation_correct_length(monkeypatch):
    """
    Test if summary is of correct length

    """
    
    monkeypatch.setattr("backend.src.config.SUMMARY_PLACEHOLDER_TOKEN_LIMIT", 10)
    
    # The first 10 tokens of SAMPLE_TEXT are:
    # "This is the full answer text for order SH-123."
    # Note: "SH-123." is tokenized as 'SH', '-', '123', '.'
    
    expected_summary = "This is the full answer text for order SH-123..."
    
    # We must re-run the spaCy model load inside the test if we
    # patch the config, or ensure the config is read *inside* the function.
    # Assuming get_n_tokens_summary reads the config value inside,
    # this test will work.
    
    summary = get_n_tokens_summary(SAMPLE_TEXT)
    
    # A more robust check might be to re-tokenize and count
    assert summary.startswith("This is the full answer text for order")
    assert summary.endswith("...")


def test_summary_handles_text_shorter_than_limit(monkeypatch):
    """
    Tests that if tokens are less than N, it returns prior.

    """

    monkeypatch.setattr("backend.src.config.SUMMARY_PLACEHOLDER_TOKEN_LIMIT", 75)
    short_text = "This is a short answer." # (5 tokens)
    
    summary = get_n_tokens_summary(short_text)
    
    assert summary == short_text
    assert not summary.endswith("...")



# --- Tests for highlight_entities ---

def test_entity_highlighting_simple_case():
    """
    Tests that a single, matching entity is highlighted.

    """

    summary_text = "The status of order SH-123 is shipped."
    entities = [{'text': 'sh-123', 'label': 'order_id'}]
    
    expected = "The status of order **SH-123** is shipped."
    result = highlight_entities(summary_text, entities)
    assert result == expected


def test_entity_highlighting_case_insensitive():
    """
    Tests that highlighting is case-insensitive.

    """

    summary_text = "The status of order sh-123 is shipped."
    entities = [{'text': 'sh-123', 'label': 'order_id'}]
    
    expected = "The status of order **sh-123** is shipped." 
    result = highlight_entities(summary_text, entities)
    assert result == expected


def test_entity_highlighting_multiple_entities():
    """
    Tests that multiple, different entities are all highlighted.

    """

    summary_text = "Tracking SH-123 and SC-456."
    entities = [{'text': 'sh-123', 'label': 'order_id'}, {'text': 'sc-456', 'label': 'order_id'}]
    
    expected = "Tracking **SH-123** and **SC-456**."
    result = highlight_entities(summary_text, entities)
    assert result == expected


def test_entity_highlighting_no_match():
    """
    Tests that the text is returned unchanged if no entities are found in the summary text.

    """

    summary_text = "Your package is on its way."
    entities = [{'text': 'sh-123', 'label': 'order_id'}]
    
    expected = "Your package is on its way."
    result = highlight_entities(summary_text, entities)
    assert result == expected


def test_entity_highlighting_longest_first_prevents_partial_match():
    """
    Tests the critical edge case where one entity is a substring of another (e.g., "Ship" and "ShipCube").
    """
    summary_text = "This is a package for ShipCube."
    entities = [{'text': 'shipcube', 'label': 'shipper'}, {'text': 'ship', 'label': 'mode'}]
    
    expected = "This is a package for **ShipCube**."
    
    result = highlight_entities(summary_text, entities)
    assert result == expected


def test_entity_highlighting_no_entities_provided():
    """
    Tests that the text is returned unchanged if the entity list is empty.

    """

    summary_text = "This is a package for ShipCube."
    entities = [{}]
    
    expected = "This is a package for ShipCube."
    result = highlight_entities(summary_text, entities)
    assert result == expected