"""HERALD — Citizen Communication Agent. NVIDIA: Llama 3.1 8B"""
from typing import Dict, Any
from agents.base import Agent

class HeraldAgent(Agent):
    name = "HERALD"
    role = "Citizen Communication — Translates findings into Swahili/English accessible language"
    model_key = "lightweight"  # Llama 3.1 8B
    triggers = ["query_received", "report_ready", "alert_to_broadcast"]

    async def _execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        action = input_data.get("action", "answer")
        language = input_data.get("language", "en")

        if action == "answer":
            return await self._answer_query(input_data, language)
        elif action == "summarize_report":
            return await self._summarize_for_citizen(input_data, language)
        elif action == "ussd_response":
            return await self._ussd_response(input_data, language)
        return {"error": "Unknown action", "available": ["answer", "summarize_report", "ussd_response"]}

    async def _answer_query(self, data: Dict[str, Any], lang: str) -> Dict[str, Any]:
        prompt = f"""
        Answer this citizen's question about Kenyan government spending.
        Question: {data.get("question", "")}
        Available data: {data.get("data", {})}
        Language: {"Swahili" if lang == "sw" else "English"}
        
        Rules:
        1. Be clear and simple
        2. Cite sources
        3. NEVER make accusations
        4. Use "connection report" language
        5. Suggest follow-up questions
        """
        return {"answer": await self.call_nvidia([{"role": "user", "content": prompt}], temperature=0.3), "language": lang}

    async def _summarize_for_citizen(self, data: Dict[str, Any], lang: str) -> Dict[str, Any]:
        prompt = f"""
        Summarize this government data for a Kenyan citizen in simple {language} terms:
        {data.get("report", "")}
        Keep it under 150 words. Use bullet points.
        """
        return {"summary": await self.call_nvidia([{"role": "user", "content": prompt}], temperature=0.3), "language": lang}

    async def _ussd_response(self, data: Dict[str, Any], lang: str) -> Dict[str, Any]:
        # USSD has 160 char limit per screen
        prompt = f"""
        Create a USSD menu response (max 160 characters) in {language}:
        Data: {data.get("data", "")}
        Make it clear with numbered options.
        """
        response = await self.call_nvidia([{"role": "user", "content": prompt}], max_tokens=200)
        return {"ussd_text": response[:160], "language": lang}
