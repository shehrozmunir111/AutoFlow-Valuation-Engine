import pytest
from datetime import datetime

from app.schemas.quote import QuoteRequest
from app.services.auto_spec_fetcher import AutoSpecFetcher
from app.services.smart_assessor import SmartAssessor
from app.services.valuation_logic import ValuationLogic


def build_quote_request(**overrides):
    data = {
        "year": 2010,
        "make": "Toyota",
        "model": "Camry",
        "mileage": 220000,
        "title_status": "clean",
        "condition_rating": "good",
        "drivable": True,
        "zip_code": "12345",
    }
    data.update(overrides)
    return QuoteRequest(**data)


def test_valuation_fallback_uses_current_year(db):
    request = build_quote_request(year=datetime.now().year - 10)

    result = ValuationLogic(db).calculate_optimal_price(request)

    expected = max(500, 5000 - (10 * 300))
    assert float(result["final_offer"]) == expected
    assert result["calculation_method"] == "fallback_estimate"


def test_smart_assessor_uses_rules_when_groq_not_configured(monkeypatch):
    monkeypatch.setattr("app.services.smart_assessor.settings.GROQ_API_KEY", "")
    monkeypatch.setattr("app.services.smart_assessor.settings.MOCK_MODE", False)

    request = build_quote_request(
        year=datetime.now().year - 20,
        mileage=250000,
        title_status="junk",
        condition_rating="junk",
        drivable=False,
    )

    result = SmartAssessor()._rules_fallback(request)

    assert result["classification"] == "junk"
    assert float(result["confidence"]) == 0.70


@pytest.mark.asyncio
async def test_auto_spec_fetcher_returns_mock_data(monkeypatch):
    monkeypatch.setattr("app.services.auto_spec_fetcher.settings.MOCK_MODE", True)

    result = await AutoSpecFetcher().fetch_specs_by_vin("1HGCM82633A000000")

    assert result is not None
    assert result["make"] == "Toyota"
    assert result["model"] == "Camry"
