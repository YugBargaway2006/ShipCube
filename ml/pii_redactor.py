# ml/pii_redactor.py
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

# --- 1. Set up the tools (runs once when the file is imported) ---
print("Loading PII redaction engines...")
analyzer = AnalyzerEngine()        # Finds PII
anonymizer = AnonymizerEngine()    # Replaces PII
print("PII engines loaded successfully.")


def redact_prompt(text: str) -> str:
    """
    Takes a raw text prompt and returns an anonymized version
    with PII (like names, phones, emails) replaced.
    """
    try:
        # 2. Find all PII entities in the text
        analyzer_results = analyzer.analyze(text=text, language="en", entities=["PHONE_NUMBER", "EMAIL_ADDRESS"])

        # Ensure analyzer_results is always a list
        if not isinstance(analyzer_results, list):
            analyzer_results = [analyzer_results]

        # 3. Replace (anonymize) the entities we found
        anonymized_result = anonymizer.anonymize(
            text=text,
            analyzer_results=analyzer_results,
            operators={
                "PHONE_NUMBER": OperatorConfig("replace", {"new_value": "<PHONE>"}),
                "EMAIL_ADDRESS": OperatorConfig("replace", {"new_value": "<EMAIL>"})
            }
        )

        return anonymized_result.text

    except Exception as e:
        print(f"Error in PII redaction: {e}")
        return ""


# --- 4. Test the file directly ---
if __name__ == "__main__":
    raw_prompt = (
        "Hi, this is John Doe, my order SC12345 is late. "
        "Call me at 212-555-5555 or email me at john.doe@example.com."
    )

    print(f"\nOriginal: {raw_prompt}")
    safe_prompt = redact_prompt(raw_prompt)
    print(f"Redacted: {safe_prompt}")
