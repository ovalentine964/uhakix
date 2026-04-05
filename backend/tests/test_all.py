"""
UHAKIX Backend Tests — Production Test Suite
Tests core agents, API routes, compliance, scrapers, and voice services.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# ============================================================
# Agent Tests
# ============================================================

class TestJasiriAgent:
    """JASIRI — Budget Intelligence Agent tests."""

    @pytest.mark.asyncio
    async def test_analyze_variance_calculates_correctly(self):
        from agents.jasiri.agent import JasiriAgent
        agent = JasiriAgent()
        agent.call_nvidia = AsyncMock(return_value='{"risk_level": "high"}')

        result = await agent._execute({
            "action": "analyze_variance",
            "ministry": "Ministry of Health",
            "allocated_kes": 100000000,
            "spent_kes": 130000000,
            "fiscal_year": "2024/25",
        })

        assert result["variance_pct"] == pytest.approx(30.0)
        assert result["anomaly_detected"] is True
        assert "connection_report" in result
        assert result["connection_report"]["entity_name"] == "Ministry of Health"

    @pytest.mark.asyncio
    async def test_normal_variance_not_flagged(self):
        from agents.jasiri.agent import JasiriAgent
        agent = JasiriAgent()
        agent.call_nvidia = AsyncMock(return_value='{"risk_level": "low"}')

        result = await agent._execute({
            "action": "analyze_variance",
            "ministry": "Ministry of Education",
            "allocated_kes": 100000000,
            "spent_kes": 105000000,
            "fiscal_year": "2024/25",
        })

        assert result["anomaly_detected"] is False
        assert result["variance_pct"] == pytest.approx(5.0)

    @pytest.mark.asyncio
    async def test_zero_allocation_handled(self):
        from agents.jasiri.agent import JasiriAgent
        agent = JasiriAgent()

        result = await agent._execute({
            "action": "analyze_variance",
            "ministry": "Ministry of Sports",
            "allocated_kes": 0,
            "spent_kes": 50000,
            "fiscal_year": "2024/25",
        })

        assert result["anomaly_detected"] is False
        assert result["variance_pct"] == 0

    @pytest.mark.asyncio
    async def test_shield_applied(self):
        from agents.jasiri.agent import JasiriAgent
        agent = JasiriAgent()
        agent.call_nvidia = AsyncMock(return_value='{"risk_level": "medium"}')

        result = await agent.process({
            "action": "analyze_variance",
            "ministry": "Ministry of Roads",
            "allocated_kes": 500000000,
            "spent_kes": 700000000,
            "fiscal_year": "2024/25",
        })

        assert result.get("compliance_status") == "shield-vetted"
        assert result["agent"] == "JASIRI"
        assert result["processing_time_ms"] >= 0


class TestSphinxAgent:
    """SPHINX — Anomaly Detection Agent tests."""

    def test_zscore_anomaly_detection(self):
        from agents.sphinx.agent import SphinxAgent
        agent = SphinxAgent()

        # Normal values with one outlier
        values = [100, 105, 98, 102, 101, 99, 103, 500]
        anomalies = agent._zscore_anomaly(values, "test_metric")

        assert len(anomalies) > 0
        assert any(a["value"] == 500 for a in anomalies)

    def test_zscore_no_anomaly_uniform_data(self):
        from agents.sphinx.agent import SphinxAgent
        agent = SphinxAgent()

        values = [100, 100, 100, 100, 100]
        anomalies = agent._zscore_anomaly(values, "test_metric")
        assert len(anomalies) == 0

    def test_zscore_too_few_data_points(self):
        from agents.sphinx.agent import SphinxAgent
        agent = SphinxAgent()

        anomalies = agent._zscore_anomaly([100, 101], "test_metric")
        assert len(anomalies) == 0

    def test_trend_anomaly_detection(self):
        from agents.sphinx.agent import SphinxAgent
        agent = SphinxAgent()

        data = [
            {"value": 100}, {"value": 105}, {"value": 102},
            {"value": 98}, {"value": 101},
            {"value": 300},  # 300% increase — anomaly
        ]
        anomalies = agent._trend_anomaly(data, "test_metric")
        assert len(anomalies) > 0
        assert anomalies[-1]["change_pct"] > 50


class TestCountAgent:
    """COUNT — Vote Aggregation Agent tests."""

    @pytest.mark.asyncio
    async def test_aggregate_station_median(self):
        from agents.election.count.agent import CountAgent
        agent = CountAgent()

        result = await agent._aggregate_station({
            "action": "aggregate_station",
            "submissions": [
                {"station_code": "071/042", "presidential_votes": {"A": 100, "B": 90}},
                {"station_code": "071/042", "presidential_votes": {"A": 105, "B": 88}},
                {"station_code": "071/042", "presidential_votes": {"A": 102, "B": 91}},
            ],
        })

        assert result["station_code"] == "071/042"
        assert result["final_votes"]["A"] == 102  # Median of [100, 102, 105]
        assert result["final_votes"]["B"] == 90   # Median of [88, 90, 91]
        assert result["submission_count"] == 3
        assert "data_hash" in result


class TestAlertAgent:
    """ALERT — Election Anomaly Detection tests."""

    @pytest.mark.asyncio
    async def test_turnout_anomaly_high(self):
        from agents.election.alert.agent import AlertAgent
        agent = AlertAgent()

        result = await agent._check_turnout_anomaly({
            "station_code": "042",
            "votes_cast": 990,
            "registered_voters": 1000,
        })

        assert result["anomaly"] is True
        assert result["severity"] in ("medium", "high")
        assert result["turnout_pct"] == 99.0

    @pytest.mark.asyncio
    async def test_turnout_anomaly_low(self):
        from agents.election.alert.agent import AlertAgent
        agent = AlertAgent()

        result = await agent._check_turnout_anomaly({
            "station_code": "043",
            "votes_cast": 100,
            "registered_voters": 1000,
        })

        assert result["anomaly"] is True
        assert result["turnout_pct"] == 10.0

    @pytest.mark.asyncio
    async def test_normal_turnout(self):
        from agents.election.alert.agent import AlertAgent
        agent = AlertAgent()

        result = await agent._check_turnout_anomaly({
            "station_code": "044",
            "votes_cast": 650,
            "registered_voters": 1000,
        })

        assert result["anomaly"] is False
        assert result["turnout_pct"] == 65.0

    @pytest.mark.asyncio
    async def test_duplicate_detection(self):
        from agents.election.alert.agent import AlertAgent
        agent = AlertAgent()

        result = await agent._check_duplicate_submission({
            "station_code": "042",
            "submissions": [
                {"image_hash": "abc123"},
                {"image_hash": "abc123"},
                {"image_hash": "def456"},
            ],
        })

        assert result["exact_duplicates"] == 1
        assert result["suspicious"] is True


class TestShieldAgent:
    """SHIELD — Legal Compliance Agent tests."""

    @pytest.mark.asyncio
    async def test_redacts_kenyan_id(self):
        from agents.shield.agent import ShieldAgent, REDACTION_RULES
        import re
        text = "Citizen ID 12345678 was involved."
        result = REDACTION_RULES["kenyan_id"].sub("[ID_REDACTED]", text)
        assert "12345678" not in result
        assert "[ID_REDACTED]" in result

    @pytest.mark.asyncio
    async def test_redacts_phone(self):
        from agents.shield.agent import ShieldAgent, REDACTION_RULES
        import re
        text = "Call me at 0712345678"
        result = REDACTION_RULES["kenyan_phone"].sub("[PHONE_REDACTED]", text)
        assert "0712345678" not in result
        assert "[PHONE_REDACTED]" in result

    def test_accusatory_term_replacement(self):
        from agents.shield.agent import ACCUSATORY_TERMS
        text = "The minister stole public funds through corruption."
        for term, replacement in ACCUSATORY_TERMS.items():
            if term in text.lower():
                text = text.replace(term, replacement)
        assert "stole" not in text
        assert "corruption" not in text


# ============================================================
# Scraper Tests
# ============================================================

class TestIFMISScraper:
    """IFMIS scraper tests."""

    def test_normalize_transaction(self):
        from services.scraper.ifmis_scraper import IFMISScraper
        scraper = IFMISScraper()

        raw = {
            "id": "TXN-001",
            "ministry": "Ministry of Health",
            "department": "Hospitals",
            "amount_kes": "1,500,000.00",
            "purpose": "Medical Equipment",
            "vendor": "MedSupply Kenya Ltd",
            "date": "2024-01-15",
        }
        normalized = scraper._normalize_transaction(raw)

        assert normalized["ministry"] == "Ministry of Health"
        assert normalized["amount_kes"] == 1500000.0
        assert normalized["source"] == "ifmis"

    def test_validate_record(self):
        from services.scraper.ifmis_scraper import IFMISScraper
        scraper = IFMISScraper()

        valid = {
            "ministry": "Health",
            "amount_kes": 100000,
            "date": "2024-01-01",
        }
        assert scraper.validate_record(valid) is True

        invalid = {
            "ministry": "",
            "amount_kes": 100000,
            "date": "2024-01-01",
        }
        assert scraper.validate_record(invalid) is False


class TestTendersScraper:
    """Tenders scraper tests."""

    def test_normalize_tender(self):
        from services.scraper.tenders_scraper import TendersScraper
        scraper = TendersScraper()

        raw = {
            "id": "T-2024-001",
            "title": "Supply of Office Furniture",
            "entity": "Ministry of Education",
            "estimated_cost": "5,000,000",
            "awarded_amount": "4,800,000",
            "contractor": "FurniturePlus Ltd",
            "status": "awarded",
        }
        normalized = scraper._normalize_tender(raw)

        assert normalized["id"] == "T-2024-001"
        assert normalized["estimated_cost_kes"] == 5000000.0
        assert normalized["awarded_amount_kes"] == 4800000.0
        assert normalized["contractor"] == "FurniturePlus Ltd"

    def test_validate_record(self):
        from services.scraper.tenders_scraper import TendersScraper
        scraper = TendersScraper()

        assert scraper.validate_record({"id": "1", "title": "Test"}) is True
        assert scraper.validate_record({"id": "", "title": "Test"}) is False
        assert scraper.validate_record({"id": "1", "title": ""}) is False


class TestCOBScraper:
    """Controller of Budget scraper tests."""

    def test_parse_amount(self):
        from services.scraper.cob_scraper import COBScraper
        scraper = COBScraper()

        raw = {
            "entity": "Nairobi County",
            "allocation": "KES 2,500,000,000",
            "absorption": "KES 1,875,000,000",
        }
        normalized = scraper._normalize_budget_line(raw)
        assert normalized["allocated_kes"] == 2500000000.0
        assert normalized["absorbed_kes"] == 1875000000.0
        assert normalized["absorption_rate"] == 75.0
        assert normalized["variance_pct"] == pytest.approx(-25.0)


# ============================================================
# Compliance Middleware Tests
# ============================================================

class TestCompliance:
    """SHIELD compliance middleware tests."""

    def test_redact_personal_info_phone(self):
        from api.middleware.compliance import redact_personal_info
        text = "Contact 0712345678 for details."
        result = redact_personal_info(text)
        assert "[PHONE_REDACTED]" in result

    def test_redact_personal_info_email(self):
        from api.middleware.compliance import redact_personal_info
        text = "Email admin@example.com for more."
        result = redact_personal_info(text)
        assert "[EMAIL_REDACTED]" in result

    def test_validate_connection_report(self):
        from api.middleware.compliance import validate_connection_report
        report = {
            "narrative": "The minister was corrupt and stole funds.",
            "sources": ["IFMIS", "Treasury", "COB"],
        }
        result = validate_connection_report(report)
        assert "corrupt" not in result["narrative"].lower()
        assert result["min_source_threshold_met"] is True
        assert result["compliance_status"] == "shield-vetted"

    def test_insufficient_sources(self):
        from api.middleware.compliance import validate_connection_report
        report = {
            "narrative": "Some finding.",
            "sources": ["IFMIS"],
        }
        result = validate_connection_report(report)
        assert result["min_source_threshold_met"] is False


# ============================================================
# Voice Service Tests
# ============================================================

class TestSpeechToText:
    """STT service unit tests (no model required)."""

    def test_sheng_detection(self):
        from services.voice.stt_service import UHAKIXSpeechToText
        stt = UHAKIXSpeechToText()
        assert stt._detect_sheng("Sana pesa ni form") is True
        assert stt._detect_sheng("The government spent money") is False

    def test_sheng_normalization(self):
        from services.voice.stt_service import UHAKIXSpeechToText
        stt = UHAKIXSpeechToText()
        result = stt._normalize_sheng("Sana pesa form")
        assert "sana" not in result.lower()


class TestCivicEducation:
    """Civic Education knowledge base tests."""

    @pytest.mark.asyncio
    async def test_constitution_match_right_to_info(self):
        from services.civic_education.knowledge_base import UHAKIXCivicEducation
        edu = UHAKIXCivicEducation()
        result = await edu.answer_civic_question("What is my right to access information?")
        assert result["type"] == "constitution"
        assert "Article 35" in result["article"]

    @pytest.mark.asyncio
    async def test_constitution_match_budget_transparency(self):
        from services.civic_education.knowledge_base import UHAKIXCivicEducation
        edu = UHAKIXCivicEducation()
        result = await edu.answer_civic_question("How should public budgets be managed?")
        assert result["type"] == "constitution"
        assert "Article 201" in result["article"]

    @pytest.mark.asyncio
    async def test_manipulation_detection_vague_promises(self):
        from services.civic_education.knowledge_base import UHAKIXCivicEducation
        edu = UHAKIXCivicEducation()
        result = await edu.answer_civic_question("The candidate promised to build roads but no plan")
        assert result["type"] == "manipulation_warning"
        assert "Vague" in result.get("tactic_name", "")

    @pytest.mark.asyncio
    async def test_manipulation_detection_ethnic_division(self):
        from services.civic_education.knowledge_base import UHAKIXCivicEducation
        edu = UHAKIXCivicEducation()
        result = await edu.answer_civic_question("We must follow our tribe, if they win we will suffer")
        assert result["type"] == "manipulation_warning"
        assert "Ethnic" in result.get("tactic_name", "")

    @pytest.mark.asyncio
    async def test_manipulation_detection_charity_as_policy(self):
        from services.civic_education.knowledge_base import UHAKIXCivicEducation
        edu = UHAKIXCivicEducation()
        result = await edu.answer_civic_question("I brought this road to your area and it is my gift")
        assert result["type"] == "manipulation_warning"

    @pytest.mark.asyncio
    async def test_general_response(self):
        from services.civic_education.knowledge_base import UHAKIXCivicEducation
        edu = UHAKIXCivicEducation()
        result = await edu.answer_civic_question("Hello, how are you?")
        assert result["type"] == "general"

    @pytest.mark.asyncio
    async def test_swahili_response(self):
        from services.civic_education.knowledge_base import UHAKIXCivicEducation
        edu = UHAKIXCivicEducation()
        result = await edu.answer_civic_question("Habari yako", language="sw")
        assert result["type"] == "general" or result["type"] == "constitution"


# ============================================================
# Citizen API Route Tests
# ============================================================

class TestCitizenAPIRouter:
    """Tests for API routing logic."""

    def test_route_transparency_query_spending(self):
        from api.routes.citizen import _route_transparency_query
        result = _route_transparency_query("How much did health ministry spend?")
        assert result["found"] is True
        assert result["category"] == "spending"

    def test_route_transparency_query_tender(self):
        from api.routes.citizen import _route_transparency_query
        result = _route_transparency_query("Show me tenders from ministry of roads")
        assert result["found"] is True
        assert result["category"] == "procurement"

    def test_route_transparency_query_election(self):
        from api.routes.citizen import _route_transparency_query
        result = _route_transparency_query("What are the election results?")
        assert result["found"] is True
        assert result["category"] == "election"

    def test_route_transparency_query_unknown(self):
        from api.routes.citizen import _route_transparency_query
        result = _route_transparency_query("What is the weather today?")
        assert result["found"] is False


# ============================================================
# Config Tests
# ============================================================

class TestConfig:
    """Configuration loading tests."""

    def test_settings_default_values(self):
        from core.config import Settings
        settings = Settings()
        assert settings.app_name == "UHAKIX"
        assert settings.api_v1_prefix == "/api/v1"
        assert settings.election_verification_min_sources == 3
        assert settings.form_34a_max_file_size_mb == 10

    def test_cors_origins_list(self):
        from core.config import Settings
        settings = Settings(cors_origins="http://localhost:3000, https://uhakix.ke")
        origins = settings.cors_origins_list
        assert len(origins) == 2
        assert "https://uhakix.ke" in origins
