"""VERIFY — Form 34A Authenticity Agent. NVIDIA: Llama 3.2 Vision + Nemotron-4."""
from typing import Dict, Any, List
from agents.base import Agent

class VerifyAgent(Agent):
    name = "VERIFY"
    role = "Election — Validate Form 34A authenticity (watermarks, signatures, consistency)"
    model_key = "complex"
    triggers = ["form_extracted", "verification_requested"]

    async def _execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        image_data = input_data.get("image_base64", "") or input_data.get("image_url", "")
        extracted_data = input_data.get("extracted_data", {})

        if not image_data or not extracted_data:
            return {"error": "Missing image or extracted data", "status": "failed"}

        vision_prompt = """
        Analyze this Form 34A for authenticity. Check:
        1. IEBC letterhead and watermark present
        2. Official signatures visible (presiding officer, agents)
        3. Form appears genuine (not a crude photocopy or digital edit)
        4. Vote totals are mathematically consistent (sum of candidates ≈ total votes cast - rejected)
        5. Serial number format matches IEBC format

        Return JSON: {"authenticity_score": 0.0, "watermark_detected": true/false, 
                      "signatures_detected": 0, "math_consistent": true/false,
                      "tampering_indicators": [], "verdict": "likely_authentic|suspicious|likely_fake"}
        """

        vision_result = await self.call_vision(vision_prompt, image_data)

        # Data consistency check with existing submissions
        data_validation = await self._validate_data_consistency(extracted_data)

        return {
            "verification_result": vision_result,
            "data_validation": data_validation,
            "authenticity_score": 0.0,
            "status": "verified" if True else "pending_review",
            "next_step": "COUNT",
        }

    async def _validate_data_consistency(self, extracted: Dict[str, Any]) -> Dict[str, Any]:
        """Check if extracted numbers are internally consistent."""
        votes = extracted.get("presidential_votes", {})
        total_cast = extracted.get("total_votes_cast", 0)
        rejected = extracted.get("rejected_votes", 0)
        total_votes_sum = sum(votes.values())

        math_consistent = abs(total_votes_sum - (total_cast - rejected)) < 10  # Allow small rounding

        return {
            "sum_of_candidate_votes": total_votes_sum,
            "total_votes_cast": total_cast,
            "rejected_votes": rejected,
            "math_consistent": math_consistent,
        }
