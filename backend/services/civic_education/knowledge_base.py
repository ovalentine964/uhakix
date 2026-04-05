"""
UHAKIX Civic Education Service
Provides citizens with:
- Constitutional rights education (Constitution of Kenya 2010)
- Political manipulation awareness (48 Laws adapted)
- Budget literacy education
- How to spot corruption patterns
"""
import os
import logging
from pathlib import Path

logger = logging.getLogger("uhakix.civic")


class UHAKIXCivicEducation:
    """Civic Education knowledge base for citizen empowerment"""
    
    # Constitutional articles mapped to citizen questions
    CONSTITUTION_KB = {
        "access_to_information": {
            "articles": ["Article 35"],
            "keywords": ["information", "access", "know", "records", "budget", "pesa", "records"],
            "summary": "Every citizen has the RIGHT to access information held by the State (Article 35). This includes county budgets, spending records, and tender awards.",
            "actionable_steps": [
                "Request information via your county assembly",
                "Check UHAKIX transparency dashboard",
                "File complaint with Commission on Administrative Justice if denied"
            ]
        },
        "accountability": {
            "articles": ["Article 201", "Article 226"],
            "keywords": ["accountability", "audit", "spending", "tender", "contract", "corruption"],
            "summary": "Public finance must be conducted with openness, accountability, and public participation (Art 201). The Auditor General audits ALL government accounts annually (Art 226).",
            "actionable_steps": [
                "Check Auditor General reports at auditor-general.go.ke",
                "Review county assembly budget approvals",
                "Report irregularities via UHAKIX anonymous reporting"
            ]
        },
        "leadership_integrity": {
            "articles": ["Article 73", "Article 76", "Article 77"],
            "keywords": ["corruption", "integrity", "declaration", "conflict", "asset"],
            "summary": "State officers must act with integrity. They cannot use their position for personal gain (Art 76). They must declare income, assets, and liabilities (Art 77).",
            "actionable_steps": [
                "Check EACC asset declarations",
                "If lifestyle doesn't match income — report via UHAKIX",
                "Demand accountability through your MCA"
            ]
        },
        "economic_rights": {
            "articles": ["Article 43"],
            "keywords": ["food", "housing", "health", "water", "education", "rights", "haki"],
            "summary": "Every person has the right to health care, education, accessible housing, clean water, and social security (Article 43).",
            "actionable_steps": [
                "If denied basic services — contact your county representative", 
                "Check county budget allocation for social services",
                "Document denial and file complaint with relevant authority"
            ]
        },
        "civic_participation": {
            "articles": ["Article 37", "Article 38", "Article 73"],
            "keywords": ["vote", "election", "politician", "campaign", "rally", "party"],
            "summary": "Every citizen has the right to make political choices, form/participate in political parties, and vote in free and fair elections (Article 38).",
            "actionable_steps": [
                "Verify candidacy status at IEBC",
                "Check candidate's educational credentials and criminal record",
                "Evaluate track record, not promises"
            ]
        }
    }
    
    # Political manipulation tactics (adapted from 48 Laws)
    MANIPULATION_TACTICS = {
        "vague_promises": {
            "law": "Law 3: Conceal Your Intentions",
            "example": "Candidate says 'I'll create jobs' but no specific plan, no timeline, no budget",
            "red_flag": "No specifics, no budget, no accountability mechanism",
            "what_to_do": "Ask: 'What is your specific plan with budget allocation? Who will implement it? What is the timeline?'"
        },
        "bribery_during_campaigns": {
            "law": "Law 8: Make Other People Come to You",
            "example": "Sudden 'developmental visit' with maize bags, cash, or food items during campaign season",
            "red_flag": "Items distributed only in areas that support them, not based on need",
            "what_to_do": "Understand this is YOUR tax money being redistributed to influence you. A real leader provides systems, not handouts."
        },
        "ethnic_division": {
            "law": "Law 27: Play on People's Need to Believe",
            "example": "'My tribe deserves to eat' or 'If they win, you will suffer'",
            "red_flag": "Divisions along tribal/ethnic lines, 'us vs them' rhetoric",
            "what_to_do": "Demand policies that benefit ALL Kenyans. Check Constitution Article 27 on equality and freedom from discrimination. A leader who divides cannot unite."
        },
        "emotional_manipulation": {
            "law": "Law 43: Work on the Hearts and Minds of Others",
            "example": "Emotional speeches without substance. Crying, anger, or fear to distract from facts",
            "red_flag": "Strong emotions but zero policy details",
            "what_to_do": "Separate feelings from facts. Ask: 'Show me your track record. Show me data.' Use UHAKIX to verify claims."
        },
        "false_promises": {
            "law": "Law 21: Play a Sucker to Catch a Sucker",
            "example": "Promising results that are impossible given budget constraints",
            "red_flag": "Promises require more money than the county/national budget",
            "what_to_do": "Check the actual budget allocation. If the county has KES 5B and they're promising KES 50B in projects — it's impossible."
        }
    }

    def search_constitution(self, question: str) -> dict:
        """Search Constitution knowledge base for matching article"""
        q = question.lower()
        
        # Check each knowledge base entry
        for key, entry in self.CONSTITUTION_KB.items():
            if any(kw in q for kw in entry["keywords"]):
                return {
                    "type": "constitution",
                    "title": key.replace("_", " ").title(),
                    "articles": entry["articles"],
                    "summary": entry["summary"],
                    "actionable_steps": entry["actionable_steps"]
                }
        
        return None

    def detect_manipulation(self, description: str) -> dict:
        """Detect if citizen description matches known manipulation tactics"""
        text = description.lower()
        
        for key, tactic in self.MANIPULATION_TACTICS.items():
            # Check for red flag keywords
            red_flags = tactic.get("example", "").lower()
            if any(flag in text for flag in red_flags.split()):
                return {
                    "type": "manipulation_warning",
                    "title": key.replace("_", " ").title(),
                    "law": tactic["law"],
                    "example": tactic["example"],
                    "red_flag": tactic["red_flag"],
                    "what_to_do": tactic["what_to_do"]
                }
        
        return None

    async def answer_question(self, question: str, language: str = "en") -> dict:
        """Main civic education Q&A endpoint"""
        # Check constitution first
        constitution_match = self.search_constitution(question)
        
        # Check manipulation tactics
        manipulation_match = self.detect_manipulation(question)
        
        if constitution_match and manipulation_match:
            # Both found — return combined response
            return {
                "status": "success",
                "constitution": constitution_match,
                "manipulation_warning": manipulation_match,
                "message": "⚠️ You may be experiencing political manipulation. Here are your Constitutional rights and what to do."
            }
        
        if constitution_match:
            return {
                "status": "success",
                "constitution": constitution_match,
                "message": "Here is your Constitutional right under: " + ", ".join(constitution_match["articles"])
            }
        
        if manipulation_match:
            return {
                "status": "success",
                "manipulation_warning": manipulation_match,
                "message": manipulation_match["what_to_do"]
            }
        
        return {
            "status": "general_info",
            "message": "UHAKIX helps Kenyans understand their Constitutional rights and spot political manipulation. Ask me about: constitutional rights, budget transparency, candidate track records, or manipulation tactics.",
            "topics": [
                "Article 35 — Access to Information",
                "Article 43 — Economic & Social Rights",
                "Article 201 — Public Finance Transparency",
                "Article 77 — Leadership Integrity",
                "How to spot vague promises",
                "How to detect ethnic division",
                "Budget literacy"
            ]
        }


# Singleton instance
civic_edu = UHAKIXCivicEducation()
