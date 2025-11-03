# In backend/src/summarizer.py

import re
import spacy
from typing import List, Dict
from . import config


# There should be a single instance of spacy class to maintain invariance.
model = "en_core_web_sm"

try:
    nlp = spacy.load(model)
except OSError:
    print(f"Downloading '{model}' model...")
    spacy.cli.download(model)
    nlp = spacy.load(model)

def get_n_tokens_summary(text: str) -> str:
    """
        Process text and returns summary composing of first n tokens
    
    """

    N = config.SUMMARY_PLACEHOLDER_TOKEN_LIMIT
    doc = nlp(text)
    
    if len(doc) <= N:
        return text
    
    summary_span = doc[:N]
    summary_text = summary_span.text

    return summary_text + "..."


def highlight_entities(summary_text: str, query_entities: List) -> str:
    """
        Highlight the occuranaces of query entities in summary_text
    
    """

    highlighted_text = summary_text
    entity_texts = list(set([ent['text'] for ent in query_entities if 'text' in ent]))

    entity_texts.sort(key=len, reverse=True)

    replacements = {}
    for i, entity_text in enumerate(entity_texts):
        placeholder = f"__HIGHLIGHT_{i}__"

        pattern = re.compile(f"({re.escape(entity_text)})", re.IGNORECASE)

        def get_replacement(match):
            original_text = match.group(1)
            replacements[placeholder] = f"**{original_text}**"
            return placeholder

        highlighted_text = pattern.sub(
            get_replacement,
            highlighted_text
        ) 
    
    for placeholder, value in replacements.items():
        highlighted_text = highlighted_text.replace(placeholder, value)

    return highlighted_text

