import spacy
from spacy.tokens import DocBin
import json
from sklearn.model_selection import train_test_split
from pathlib import Path

# Input/output paths
input_file = "../data/shipcube_final.json"
train_output = "train.spacy"
dev_output = "dev.spacy"

# 1️⃣ Load your JSONL data
with open(input_file, "r", encoding="utf-8") as f:
    data = [json.loads(line) for line in f]

# 2️⃣ Split into train and dev (80/20)
train_data, dev_data = train_test_split(data, test_size=0.2, random_state=42)

# 3️⃣ Create a blank English NLP object
nlp = spacy.blank("en")

def create_docbin(dataset):
    """Converts text + entity annotations into spaCy DocBin safely (no overlaps)."""
    doc_bin = DocBin()
    for item in dataset:
        text = item["text"]
        entities = item.get("entities", [])
        doc = nlp.make_doc(text)
        valid_spans = []
        used_tokens = set()

        for ent in entities:
            span = doc.char_span(ent["start"], ent["end"], label=ent["label"], alignment_mode="contract")

            # Validate: skip overlapping or invalid spans
            if span is None:
                print(f"⚠️ Skipping invalid span in text: {text[ent['start']:ent['end']]} ({ent['label']})")
                continue

            # Ensure no overlapping tokens
            token_indexes = set(range(span.start, span.end))
            if used_tokens & token_indexes:
                print(f"⚠️ Overlapping span skipped: {span.text} in '{text}'")
                continue

            used_tokens.update(token_indexes)
            valid_spans.append(span)

        doc.ents = valid_spans
        doc_bin.add(doc)
    return doc_bin


# 4️⃣ Convert and save .spacy files
Path("corpus").mkdir(exist_ok=True)
create_docbin(train_data).to_disk(train_output)
create_docbin(dev_data).to_disk(dev_output)

print("✅ Done! Saved:")
print(f" - {train_output}")
print(f" - {dev_output}")
