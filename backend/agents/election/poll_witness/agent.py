"""POLL WITNESS — Form 34A Extraction Agent. NVIDIA: Llama 3.2 Vision. OCR + extraction."""
from typing import Dict, Any
from agents.base import Agent

class PollWitnessAgent(Agent):
    name = "POLL_WITNESS"
    role = "Election — Extract data from citizen-uploaded Form 34A photos"
    model_key = "vision"  # Llama 3.2 Vision
    triggers = ["form_34a_submitted", "photo_upload"]

    async def _execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        image_data = input_data.get("image_base64", "") or input_data.get("image_url", "")
        if not image_data:
            return {"error": "No image provided", "status": "failed"}

        # OCR extraction prompt
        prompt = """
        This is a Kenyan IEBC Form 34A (Polling Station Results Form).
        Extract ALL data from this form:

        1. Polling Station Code
        2. Polling Station Name
        3. Constituency Name
        4. County Name
        5. Presidential Candidate Votes (candidate name AND their vote count)
        6. Total Registered Voters
        7. Total Votes Cast
        8. Rejected Votes
        9. Presiding Officer Name (if visible)
        10. Any serial number or form identifier

        Return ONLY valid JSON with these exact keys:
        {"station_code": "", "station_name": "", "constituency": "", "county": "",
         "presidential_votes": {"candidate1": votes, "candidate2": votes},
         "registered_voters": 0, "total_votes_cast": 0, "rejected_votes": 0,
         "presiding_officer": "", "form_serial": "", "image_quality": "clear|blurry|damaged"}
        """

        result = await self.call_vision(prompt, image_data)

        # Hash the image for integrity
        image_hash = self._hash_data(image_data)

        return {
            "extracted_data": result,
            "image_hash": image_hash,
            "extraction_agent": "POLL_WITNESS",
            "status": "extracted",
            "next_step": "VERIFY",
        }
