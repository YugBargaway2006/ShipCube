import spacy
from ml.ner_entity.nlp.build_pipeline import create_pii_redactor
from ml.pii_redactor import redact_prompt
from typing import List


"""Load the final hybrid NLP pipeline."""

model_path = "ml/ner_entity/models/final_hybrid_pipeline"
try:
    nlp = spacy.load(model_path)
except Exception as e:
    print(f"Failed to load NLP model from {model_path}: {e}")


def process_text_for_entities(text: str) -> List[dict]:
    """
    Processes a text string and extracts named entities using spaCy.
    Based on the NER processing pattern.
    """
    if nlp is None:
        return []

    doc = nlp(text)
    entities = []
    
    # Iterate over recognized entities
    for ent in doc.ents:
        entities.append({
            "text": ent.text,
            "label": ent.label_
        })

    return entities