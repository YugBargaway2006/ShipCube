# nlp/build_pipeline.py
import spacy
from spacy.language import Language
from spacy.pipeline import EntityRuler
from ml.pii_redactor import redact_prompt


@Language.factory("pii_redactor")
def create_pii_redactor(nlp, name):
    """
    Factory that creates a PII redactor component.
    Gives the inner function access to the 'nlp' object safely.
    """
    def pii_redactor_component(doc):
        redacted_text = redact_prompt(doc.text)
        return nlp.make_doc(redacted_text)
    return pii_redactor_component



def create_nlp_pipeline():
    """
    Creates the full hybrid spaCy pipeline.
    Combines rule-based ORDER_ID detection with transformer NER.
    """
    # transformer model
    nlp = spacy.load("en_core_web_trf")
    nlp.add_pipe("pii_redactor", first=True)
    
    # Added an EntityRuler to catch ORDER_ID patterns before the NER
    ruler = nlp.add_pipe("entity_ruler", before="ner", config={"overwrite_ents": True})
    
    # Define regex patterns for order IDs
    patterns = [
        {
            "label": "ORDER_ID",
            "pattern": [
                {"TEXT": {"REGEX": r"^(SC|EU)\d{5}$"}}
            ],
            "id": "order_id_pattern"
        }
    ]
    
    ruler.add_patterns(patterns)
    return nlp


if __name__ == "__main__":
    nlp = create_nlp_pipeline()
    text = "Where is my order SC12345 going? I also track EU54321."
    doc = nlp(text)
    for ent in doc.ents:
        print(ent.text, ent.label_)

    nlp.to_disk("./ml/ner_entity/models/final_hybrid_pipeline")
