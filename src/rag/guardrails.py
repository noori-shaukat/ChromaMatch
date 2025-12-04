import re
from typing import Dict, Any


class ChromaGuardrails:
    def __init__(self, max_query_length=300):
        self.max_query_length = max_query_length
        self.forbidden_patterns = [
            r"\b\d{3}-\d{2}-\d{4}\b",  # SSN
            r"\b\d{16}\b",  # Credit card numbers
            r"password|secret|api[_-]?key",  # Sensitive keywords
        ]

    # ---- INPUT VALIDATION ----
    def validate_input(self, ml_output: Dict[str, Any]):
        errors = []
        query = " ".join(str(v) for v in ml_output.values())
        if len(query) > self.max_query_length:
            errors.append("Query too long.")
        for pattern in self.forbidden_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                errors.append(f"Forbidden content detected: {pattern}")
        return errors

    # ---- OUTPUT MODERATION ----
    def moderate_output(self, rag_response: str):
        # Basic example: detect toxicity or offensive words
        forbidden_words = ["hate", "kill", "stupid", "idiot"]
        violations = []
        for word in forbidden_words:
            if word.lower() in rag_response.lower():
                violations.append(f"Forbidden word detected: {word}")
        # Simple hallucination detection (placeholder)
        if "alien planet" in rag_response.lower():
            violations.append("Potential hallucination detected")
        return violations
