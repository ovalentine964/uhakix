"""
UHAKIX Civic Education Knowledge Base
Based on Constitution of Kenya 2010 and civic protection frameworks.
Answers citizen questions about rights, identifies political manipulation tactics,
and provides actionable guidance.
"""

from typing import Dict, List, Optional
import structlog
import re

logger = structlog.get_logger()


class UHAKIXCivicEducation:
    """
    Civic education engine that maps citizen questions to:
    1. Constitutional articles (rights and duties)
    2. Political manipulation detection (48 Laws of Power framework)
    3. Actionable steps for citizens
    """

    # ── Constitution of Kenya 2010 — Key Articles ──────────
    CONSTITUTION: Dict[str, Dict] = {
        "article_35": {
            "title": "Access to Information",
            "number": "Article 35",
            "summary": "Every citizen has the right to access information held by the State and information held by another person that is required for the exercise or protection of any right or fundamental freedom.",
            "citizen_language": "You have the RIGHT to know how government spends public money. County budgets, tender awards, and spending records are public information.",
            "actionable_steps": [
                "Use UHAKIX 'Ask County' feature to search spending data",
                "File a formal request via UHAKIX citizen portal if data is missing",
                "Your right to information cannot be denied — no reasons required",
                "If denied, UHAKIX will escalate to the Commission on Administrative Justice"
            ],
            "keywords": ["right to information", "access to information", "haki ya kujua",
                         "access info", "katiba haki", "transparency", "open government",
                         "public records", "government data", "information request"],
        },
        "article_43": {
            "title": "Economic and Social Rights",
            "number": "Article 43",
            "summary": "Every person has the right to the highest attainable standard of health, education, clean and safe water, adequate food and housing, and social security.",
            "citizen_language": "You have a constitutional right to healthcare, education, clean water, food, housing, and social security. Government must provide these services.",
            "actionable_steps": [
                "Check if your county budget allocates funds for health, education, water",
                "Use UHAKIX to track if health/education funds actually reach your facility",
                "If services are not delivered, this is a constitutional violation"
            ],
            "keywords": ["health", "healthcare", "hospital", "education", "school",
                         "water", "food", "housing", "social security", "afya", "elimu",
                         "mada", "social rights", "economic rights"],
        },
        "article_47": {
            "title": "Fair Administrative Action",
            "number": "Article 47",
            "summary": "Every person has the right to administrative action that is expeditious, efficient, lawful, reasonable and procedurally fair.",
            "citizen_language": "Government must treat you fairly. Any administrative action (licenses, permits, services) must be done quickly, lawfully, and fairly.",
            "actionable_steps": [
                "If a government office delays unreasonably, that violates Article 47",
                "If you're denied a service without reason, you can file a complaint",
                "UHAKIX tracks administrative delays across county offices"
            ],
            "keywords": ["fair treatment", "administrative action", "government delay",
                         "denied service", "haki ya usimamizi", "fair", "efficient",
                         "procedurally fair"],
        },
        "article_77": {
            "title": "Leadership and Integrity",
            "number": "Article 77",
            "summary": "A state officer must declare income, assets, and liabilities. Must not use position to enrich themselves. Must conduct themselves in a manner that avoids conflict between personal interests and public duties.",
            "citizen_language": "Leaders MUST declare their wealth. They cannot use their position for personal gain. They must declare income, assets, and liabilities annually.",
            "actionable_steps": [
                "Check if a leader has filed their wealth declaration (public record)",
                "UHAKIX tracks spending patterns that may conflict with declared income",
                "Report suspicious enrichment to EACC (Ethics and Anti-Corruption Commission)"
            ],
            "keywords": ["integrity", "wealth declaration", "leadership", "conflict of interest",
                         "personal gain", "state officer", "enrichment", "uaminifu",
                         "declaration of assets", "leadership and integrity"],
        },
        "article_201": {
            "title": "Public Finance Transparency",
            "number": "Article 201",
            "summary": "Public finance must be conducted with openness, accountability, and public participation. Burdens and benefits must be shared equitably. Expenditure must promote equitable development.",
            "citizen_language": "All government money management MUST be open and accountable. There must be public participation in budget decisions. Money must be shared fairly across all areas.",
            "actionable_steps": [
                "Check UHAKIX transparency dashboard for your county's spending",
                "Attend county public participation forums (they are legally required)",
                "If budget decisions were made without public input, that violates Art 201"
            ],
            "keywords": ["public finance", "budget transparency", "public participation",
                         "budget", "spending", "pesa za serikali", "openness",
                         "accountability", "equitable development", "fair sharing"],
        },
        "article_226": {
            "title": "Audit of Public Accounts",
            "number": "Article 226",
            "summary": "The Auditor General must audit all government accounts annually. County government accounts must also be audited. Reports go to Parliament and county assemblies.",
            "citizen_language": "The Auditor General checks ALL government spending every year. These reports are public. They show how money was actually spent.",
            "actionable_steps": [
                "Check UHAKIX for Auditor General findings in your county",
                "Query disallowed expenditures in county assembly records",
                "Audit reports reveal which spending was not properly accounted for"
            ],
            "keywords": ["audit", "auditor general", "public accounts", "accounting",
                         "audit report", "ukaguzi", "disallowance", "audit findings"],
        },
        "article_27": {
            "title": "Freedom from Discrimination",
            "number": "Article 27",
            "summary": "Every person is equal before the law. No person shall be discriminated against directly or indirectly on any ground including race, sex, pregnancy, marital status, ethnic or social origin, colour, age, disability, religion, conscience, belief, culture, dress, language or birth.",
            "citizen_language": "NO discrimination is constitutional. Ethnic division in politics is illegal. Every Kenyan has equal rights regardless of tribe, gender, or background.",
            "actionable_steps": [
                "If a politician divides by tribe, they violate Art 27 and Art 91",
                "Report ethnic-based exclusion to the National Cohesion and Integration Commission",
                "Vote based on policies and track record, not ethnicity"
            ],
            "keywords": ["discrimination", "equality", "tribe", "ethnic", "kabila",
                         "equal rights", "no discrimination", "gender", "equal"],
        },
        "article_91": {
            "title": "Political Party Requirements",
            "number": "Article 91",
            "summary": "Every political party must have a national character, promote national unity, encourage democratic principles, respect diverse communities. Must not be founded on ethnic, racial, or religious basis.",
            "citizen_language": "Political parties MUST represent ALL Kenyans. They cannot be based on tribe, race, or religion. This is not just a guideline — it is the LAW.",
            "actionable_steps": [
                "If a party appeals primarily to one ethnic group, it violates Art 91",
                "Demand parties present national development plans",
                "Check UHAKIX for party track records across different regions"
            ],
            "keywords": ["political party", "national character", "party requirements",
                         "chama", "party law", "chama siasa", "party rules"],
        },
        "article_174": {
            "title": "Objects of Devolution",
            "number": "Article 174",
            "summary": "Devolution promotes democratic and accountable exercise of power, fosters national unity, gives local power to communities, recognizes diversity, gives communities power to manage their own affairs and to further their development.",
            "citizen_language": "County governments exist to give YOU power over local decisions. Services like health, water, roads, and markets are managed by your county, not the national government.",
            "actionable_steps": [
                "Your county manages health facilities, water, county roads, markets, pre-primary education",
                "If county services fail, the governor and county assembly are responsible",
                "UHAKIX tracks county spending on these devolved functions"
            ],
            "keywords": ["devolution", "county government", "county", "kaunti",
                         "local government", "devolved functions", "county services"],
        },
        "article_10": {
            "title": "National Values and Principles of Governance",
            "number": "Article 10",
            "summary": "National values include patriotism, national unity, democracy, participation, human dignity, equity, social justice, protection of the marginalized, good governance, integrity, transparency, and accountability.",
            "citizen_language": "These are the VALUES that all government must follow: transparency, accountability, good governance, protecting the marginalized. These are NOT optional — they are constitutional requirements.",
            "actionable_steps": [
                "When evaluating any government action, check against these values",
                "If any value is violated, there is a constitutional problem",
                "UHAKIX uses these values as a framework for all analysis"
            ],
            "keywords": ["national values", "governance", "values", "transparency",
                         "accountability", "good governance", "maadili", "democracy"],
        },
    }

    # ── Political Manipulation Detection (48 Laws Framework) ──
    MANIPULATION_TACTICS: Dict[str, Dict] = {
        "vague_promises": {
            "law": "Law 3: Conceal Your Intentions",
            "name": "Vague Promises Without Commitment",
            "description": "Politician makes big promises ('I'll create jobs', 'I'll build roads') but provides no plan, no budget, no timeline, and no accountability mechanism.",
            "example": "'I will create 1 million jobs' — without explaining how, where, or when, and without committing to measurable targets.",
            "what_to_do": "Ask for specific commitments with deadlines and budget allocations. Use UHAKIX to track whether past promises were delivered.",
            "red_flags": ["no budget mentioned", "no timeline", "no specific numbers",
                          "uses 'will' without 'how'", "vague superlatives like 'tremendous'"],
            "keywords": ["promised", "promises", "will do", "I will", "ataleta",
                         "promised us", "said he will", "campaign promises", "promised to build",
                         "promised jobs", "promised money"],
        },
        "bribery_during_campaigns": {
            "law": "Law 8: Make Other People Come to You — Use Bait If Necessary",
            "name": "Bribing with Your Own Money",
            "description": "Sudden 'developmental visit' with maize bags, cash handouts, or free items during campaign season. This is YOUR tax money being redistributed to influence your vote.",
            "example": "A minister visits your area with bags of maize and announces a 'development project' just before elections. The money was already in the county budget.",
            "what_to_do": "Understand this is YOUR tax money being redistributed to influence you. Real leaders provide systems, not handouts. Use UHAKIX to check the budget source.",
            "red_flags": ["sudden generosity near elections", "maize bags", "cash handouts",
                          "developmental visits during campaign season", "free items"],
            "keywords": ["gave us", "brought items", "brought maize", "cash handout",
                         "gave money", "brought food", "distributed", "free", "gift",
                         "kugawa", "handout", "developmental visit"],
        },
        "ethnic_division": {
            "law": "Law 27: Play on People's Need to Believe — Create a Cult-like Following",
            "name": "Ethnic Division Tactics",
            "description": "Politician uses tribal identity to create an 'us vs. them' dynamic. 'My tribe deserves to eat' or 'If they win, you will suffer.' This violates Article 27 and Article 91.",
            "example": "'We must follow our own' or 'They don't want us to eat' or 'This is our time.'",
            "what_to_do": "Demand policies that benefit ALL Kenyans. Check Constitution Art 27 on equality and Art 91 on political party national character. Don't vote on emotion — vote on accountability.",
            "red_flags": ["tribal language", "us vs. them rhetoric", "ethnic appeals",
                          "fear-mongering about opponents", "'our time to eat'"],
            "keywords": ["only my tribe", "if they win", "we must", "follow me",
                         "our people", "our tribe", "their tribe", "kabila",
                         "wale hawataki", "tuna haki", "our time to eat",
                         "our turn", "muda wetu", "following leader"],
        },
        "fear_mongering": {
            "law": "Law 10: Infection — Avoid the Unhappy and Unlucky",
            "name": "Fear and Threat Tactics",
            "description": "Politician creates fear about the opposite side winning to drive emotional voting. Implies violence, economic collapse, or tribal targeting.",
            "example": "'If that community wins, your land will be taken' or 'You will lose everything if they get power.'",
            "what_to_do": "The Constitution protects everyone equally regardless of election outcome. No one can legally take your property or discriminate after an election. Verify claims through UHAKIX data.",
            "red_flags": ["threats", "fear", "you will lose", "they will take",
                          "collapse", "insecurity", "danger"],
            "keywords": ["fear", "scared", "danger", "they will take", "you will lose",
                         "they will kill", "insecurity", "attack", "violence",
                         "land grab", "property will be taken", "watakunyaka"],
        },
        "past_glory_clinging": {
            "law": "Law 33: Discover Each Man's Thumbscrew — Find the Weakness",
            "name": "Living on Past Achievements",
            "description": "Politician runs on what they did 10+ years ago while current service delivery has collapsed. Uses nostalgia instead of current performance.",
            "example": "'I built this hospital 15 years ago' — but hasn't maintained it, staff it, or build any new facility since.",
            "what_to_do": "Ask: What have you done in the LAST 12 months? UHAKIX shows current spending, not past promises. Check if that hospital still has equipment and staff.",
            "red_flags": ["distant past achievements", "no recent delivery", "nostalgia campaigning",
                          "resting on laurels", "old projects as current achievements"],
            "keywords": ["built years ago", "long ago", "past achievements",
                         "remember when i", "I did this before", "my legacy",
                         "what I built", "I built that hospital", "my track record"],
        },
        "charity_as_policy": {
            "law": "Law 7: Get Others to Do the Work for You, But Always Take the Credit",
            "name": "Personal Charity Disguised as Policy",
            "description": "Politician claims personal credit for public spending. Uses government-funded projects as personal achievements.",
            "example": "'I built this road in your area' — when the road was funded by the county budget (your money) and executed by a government tender.",
            "what_to_do": "Check UHAKIX records: Who approved the funding? Is it from county budget or personal funds? If it's public money, the politician should NOT be taking personal credit.",
            "red_flags": ["personal credit for public projects", "'I brought this to you'",
                          "attribution of government work to individual"],
            "keywords": ["I built this", "I brought this", "I provided", "I gave",
                         "my project", "my achievement", "my gift", "I did this for you",
                         "nilileta", "nilijenga"],
        },
    }

    async def answer_civic_question(
        self,
        question: str,
        language: str = "english",
    ) -> dict:
        """
        Answer a citizen's civic education question.

        Routes the question to the appropriate knowledge base:
        1. Constitutional rights lookup
        2. Political manipulation detection
        3. General citizen guidance

        Args:
            question: Citizen's question in any language (EN, SW, Sheng)
            language: Preferred response language

        Returns:
            Dict with answer type, article/tactic reference, and actionable steps
        """
        # Normalize question for matching
        q = question.lower().strip()

        # Step 1: Check for manipulation tactics (high-priority — protects citizens)
        manipulation = self._detect_manipulation(q)
        if manipulation:
            return {
                "type": "manipulation_warning",
                "answer": manipulation["answer"],
                "tactic_name": manipulation["name"],
                "law_reference": manipulation["law"],
                "what_to_do": manipulation["what_to_do"],
                "red_flags": manipulation.get("red_flags", []),
                "matched_pattern": manipulation["matched"],
            }

        # Step 2: Check constitutional knowledge base
        constitution_match = self._search_constitution(q)
        if constitution_match:
            return {
                "type": "constitution",
                "answer": constitution_match["answer"],
                "article": constitution_match["article_number"],
                "title": constitution_match["title"],
                "actionable_steps": constitution_match.get("steps", []),
                "matched_keywords": constitution_match.get("matched_keywords", []),
            }

        # Step 3: Check spending/governance queries
        spending_match = self._detect_spending_query(q)
        if spending_match:
            return {
                "type": "spending_query",
                "answer": "UHAKIX can help you track government spending, tenders, and county budgets. Use the transparency dashboard to search transactions, or ask a specific question about ministry, county, or contractor spending.",
                "suggested_queries": [
                    "How much did {Ministry} spend on roads?",
                    "Show me tenders from {County}",
                    "Which company won the most government contracts?",
                    "What is my county's budget absorption rate?"
                ],
            }

        # Step 4: General citizen guidance
        return {
            "type": "general",
            "answer": self._get_general_guidance(language),
            "suggested_topics": [
                "Ask about your Constitutional rights (e.g., 'What are my rights to information?')",
                "Check for political manipulation (e.g., 'A politician promised us X')",
                "Track government spending (e.g., 'How much did Health Ministry spend?')",
                "Understand devolution (e.g., 'What services should my county provide?')"
            ],
        }

    def _search_constitution(self, question: str) -> Optional[Dict]:
        """Search the Constitution knowledge base for relevant articles."""
        best_match = None
        best_score = 0

        for article_key, article_data in self.CONSTITUTION.items():
            keywords = article_data.get("keywords", [])
            score = sum(1 for kw in keywords if kw.lower() in question)
            if score > best_score:
                best_score = score
                best_match = article_data

        if best_score > 0:
            return {
                "article_number": best_match["number"],
                "title": best_match["title"],
                "answer": best_match["citizen_language"],
                "steps": best_match["actionable_steps"],
                "matched_keywords": [
                    kw for kw in best_match.get("keywords", [])
                    if kw.lower() in question
                ],
            }
        return None

    def _detect_manipulation(self, question: str) -> Optional[Dict]:
        """Detect if a citizen is describing a political manipulation tactic."""
        best_match = None
        best_score = 0

        for tactic_key, tactic_data in self.MANIPULATION_TACTICS.items():
            keywords = tactic_data.get("keywords", [])
            score = sum(1 for kw in keywords if kw.lower() in question)
            if score > best_score:
                best_score = score
                best_match = tactic_data

        if best_score >= 1:
            return {
                "answer": best_match["description"],
                "name": best_match["name"],
                "law": best_match["law"],
                "what_to_do": best_match["what_to_do"],
                "red_flags": best_match.get("red_flags", []),
                "matched": [
                    kw for kw in best_match.get("keywords", [])
                    if kw.lower() in question
                ],
            }
        return None

    def _detect_spending_query(self, question: str) -> bool:
        """Detect if the question is about government spending."""
        spending_terms = [
            "spend", "spent", "spending", "budget", "tender", "contract",
            "money", "pesa", "payment", "cost", "price", "billion", "million",
            "matumizi", "shilingi", "kaunti", "county",
        ]
        return any(term in question.lower() for term in spending_terms)

    def _get_general_guidance(self, language: str) -> str:
        """Provide general citizen guidance."""
        if language.startswith("sw"):
            return (
                "UHAKIX inakusaidia kuelewa haki zako za Kikatiba na kutambua udanganyifu wa siasa. "
                "Niulize kuhusu:\n"
                "• Haki zako za Kikatiba\n"
                "• Matumizi ya serikali kaunti yako\n"
                "• Ahadi za wagombea dhidi ya utendaji wao halisi\n"
                "• Mbinu za udanganyifu wa kisiasa\n"
                "• Jinsi ya kubaki habari kuhusu serikali yako"
            )
        return (
            "UHAKIX helps you understand your Constitutional rights and spot political manipulation. "
            "Ask me about:\n"
            "• Your Constitutional rights (access to information, health, education)\n"
            "• County and national government spending\n"
            "• Candidate promises vs. actual delivery\n"
            "• Political manipulation tactics and how to spot them\n"
            "• How to stay informed about your government"
        )


# Singleton
_civic_edu_instance = None


def get_civic_education() -> UHAKIXCivicEducation:
    """Get or create the civic education singleton."""
    global _civic_edu_instance
    if _civic_edu_instance is None:
        _civic_edu_instance = UHAKIXCivicEducation()
    return _civic_edu_instance
