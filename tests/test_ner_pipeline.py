# tests/test_pipeline.py

import pytest
import spacy
from ml.ner_entity.nlp.build_pipeline import create_pii_redactor

@pytest.fixture(scope="session")
def nlp():
    """Load the final hybrid NLP pipeline once for all tests."""
    model_path = "/media/yug/Skills/ShipCube//ml/ner_entity/models/final_hybrid_pipeline"
    try:
        nlp = spacy.load(model_path)
        return nlp
    except Exception as e:
        pytest.fail(f"❌ Failed to load NLP model from {model_path}: {e}")


import pytest
import spacy

# Make sure your 'ml/pii_redactor.py' file is accessible
from ml.pii_redactor import redact_prompt


# --- Test 1: PII Redaction Unit Test ---

def test_pii_redactor():
    """
    Tests the 'redact_prompt' function from Phase 2 in isolation.
    """
    raw_prompt = (
        "Hi, this is John Doe, my order SC12345 is late. "
        "Call me at 212-555-5555 or email john.doe@example.com."
    )
    
    # This is what we expect after redaction
    expected_safe_prompt = (
        "Hi, this is John Doe, my order SC12345 is late. "
        "Call me at <PHONE> or email <EMAIL>."
    )
    
    # Run the function
    safe_prompt = redact_prompt(raw_prompt)
    
    # Check if the output is what we expected
    assert safe_prompt == expected_safe_prompt


# --- Test 2: Hybrid NER Model Test ---

def test_hybrid_model_logic(nlp):
    """
    Tests the 'final_pipeline' model from Phase 5.
    
    It checks if BOTH the 'EntityRuler' (for ORDER_ID)
    and the 'statistical ner' (for DATE/ROUTE) are working together.
    """
    # We test the "safe" prompt, because in our real API,
    # PII redaction happens *before* this model is called.
    test_prompt = (
        "Hi, my name is John Doe, my order is EU98765, is it "
        "going from Berlin to Warsaw next week?"
    )
    
    doc = nlp(test_prompt)
    
    # Get the entities found by the model as (text, label) tuples
    entities = [(ent.text, ent.label_) for ent in doc.ents]
    
    # Check that our rule-based entity was found [6]
    assert ("EU98765", "ORDER_ID") in entities
    
    # Check that our custom-trained ML entities were found
    # (Note: "Berlin" and "Warsaw" would be GPE or ROUTE
    # and "next week" would be DATE, assuming they were in your training data)
    assert ("next week", "DATE") in entities
    assert ("Berlin", "GPE") in entities  # Or 'ROUTE' if you trained it that way
    assert ("Warsaw", "GPE") in entities  # Or 'ROUTE'
    
    # Check that the base model's entity (from Presidio/spaCy) is still there
    assert ("John Doe", "PERSON") in entities


def test_pipeline_loads(nlp):
    """Test that the NLP pipeline loads and contains required components."""
    component_names = nlp.pipe_names
    assert "ner" in component_names, "NER component missing"
    assert "entity_ruler" in component_names, "EntityRuler missing"
    assert any("pii" in name for name in component_names), "PII redactor missing"
    print(f"✅ Loaded pipeline with components: {component_names}")


def test_order_id_detection(nlp):
    """Ensure ORDER_IDs are detected by regex pattern."""
    doc = nlp("Where is my order SC12345? I also need update for EU54321.")
    order_ids = [ent.text for ent in doc.ents if ent.label_ == "ORDER_ID"]
    assert "SC12345" in order_ids, "SC12345 not detected as ORDER_ID"
    assert "EU54321" in order_ids, "EU54321 not detected as ORDER_ID"
    print(f"✅ Detected order IDs: {order_ids}")


def test_pii_redaction(nlp):
    """Ensure PII redactor replaces sensitive info."""
    text = "My name is John Doe and my phone is 212-555-5555."
    doc = nlp(text)
    assert "<PHONE>" in doc.text or "5555" not in doc.text, \
        "PII redactor did not anonymize phone numbers"
    print("✅ PII successfully redacted.")


def test_combined_entities(nlp):
    """Verify the pipeline handles mixed cases with both PII and ORDER_ID."""
    text = "This is John Doe. Please check order SC99999 and call me at 111-222-3333."
    doc = nlp(text)
    entities = [(ent.text, ent.label_) for ent in doc.ents]
    labels = [ent.label_ for ent in doc.ents]

    assert "ORDER_ID" in labels, "ORDER_ID not detected in mixed input"
    assert any(l in labels for l in ["PERSON", "PHONE_NUMBER"]), \
        "PII entity missing in mixed input"
    print(f"✅ Combined entity detection passed: {entities}")
