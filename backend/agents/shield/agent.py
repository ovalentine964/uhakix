"""
SHIELD — Legal Compliance Agent
NVIDIA Model: Nemotron-4-340B
Triggers: ALL outputs before publication
Role: Review every output for legal compliance before it reaches citizens.
"""

from typing import Dict, Any, List
from agents.base import Agent
import re

# Redaction patterns for Kenyan IDs and phone numbers
REDACTION_RULES = {
    "kenyan_id": re.compile(r"\b\d{8}\b"),
    "kenyan_phone": re.compile(r"\b(\+254|0)[17]\d{8}\b"),
    "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
}

ACCUSATORY_TERMS = {
    "corrupt": "identified as part of a connected network",
    "stole": "funds were unaccounted for",
    "crime": "anomalous activity",
    "criminal": "subject of investigation",
    "theft": "unaccounted funds",
    "fraud": "irregular transaction pattern",
    "embezzlement": "discrepancy in financial records",
    "bribe": "irregular payment",
    "corruption": "transparency concern",
}


class ShieldAgent(Agent):
    name = "SHIELD"
    role = "Legal Compliance — ALL outputs must pass through SHIELD"
    model_key = "complex"  # Nemotron-4-340B
    triggers = ["output_ready"]
    requires_shield = False  # SHIELD is the reviewer, not self-reviewed

    async def _execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run full compliance check on output data."""
        output = input_data.get("output", "")
        source_count = input_data.get("source_count", 0)

        result = {
            "compliance_passed": True,
            "modifications_made": [],
            "redactions_applied": [],
            "source_threshold_met": source_count >= 3,
        }

        # Rule 1: Redact personal information
        if isinstance(output, str):
            for rule_name, pattern in REDACTION_RULES.items():
                if pattern.search(output):
                    result["redactions_applied"].append(rule_name)
                    output = pattern.sub(f"[{rule_name.upper()}_REDACTED]", output)

        # Rule 2: Replace accusatory language
        if isinstance(output, str):
            for term, replacement in ACCUSATORY_TERMS.items():
                if term.lower() in output.lower():
                    output = re.sub(term, replacement, output, flags=re.IGNORECASE)
                    result["modifications_made"].append(f"Replaced '{term}' with safe language")

        # Rule 3: Verify minimum sources (3+)
        if source_count < 3:
            result["compliance_passed"] = False
            result["modifications_made"].append(
                f"Insufficient sources: {source_count}/3 required. "
                "This content cannot be published without 3+ independent sources."
            )

        # Rule 4: AI legal review for nuanced judgment
        if isinstance(output, str):
            review_prompt = f"""
            Review this output for legal compliance under Kenya's Data Protection Act, 2019.
            Text: {output}

            Check:
            1. Does it accuse or allege criminal activity? (Should flag)
            2. Is it framed as a connection report? (Should not accuse)
            3. Is personal information properly handled?
            4. Could this be considered defamatory under Kenyan law?

            JSON: {{"compliant": true/false, "issues": [], "suggestions": [], "legal_risk": "low|medium|high"}}
            """
            legal_review = await self.call_nvidia(
                [{"role": "user", "content": review_prompt}],
                json_response=True,
            )
            result["legal_review"] = legal_review

        result["output"] = output
        return result
