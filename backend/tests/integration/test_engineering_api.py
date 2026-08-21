from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_productivity_index_well_test_endpoint_returns_camel_case_contract() -> None:
    response = client.post(
        "/api/v1/engineering-calculations/productivity-index",
        json={
            "calculationType": "well_test",
            "oilRateStbDay": 1_000.0,
            "reservoirPressurePsi": 3_000.0,
            "flowingBottomholePressurePsi": 2_500.0,
        },
    )

    assert response.status_code == 200
    assert response.json()["calculationType"] == "well_test"
    assert response.json()["value"] == 2.0
    assert response.json()["unit"] == "STB/day/psi"


def test_productivity_index_endpoint_returns_standard_validation_error() -> None:
    response = client.post(
        "/api/v1/engineering-calculations/productivity-index",
        json={"calculationType": "well_test", "oilRateStbDay": 100.0},
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"
    assert response.json()["error"]["requestId"]
    assert response.headers["X-Request-ID"] == response.json()["error"]["requestId"]


def test_productivity_index_radial_flow_endpoint_returns_estimate() -> None:
    response = client.post(
        "/api/v1/engineering-calculations/productivity-index",
        json={
            "calculationType": "radial_flow",
            "permeabilityMd": 50.0,
            "netPayFt": 40.0,
            "oilViscosityCp": 2.0,
            "oilFvfRbStb": 1.2,
            "drainageRadiusFt": 1_000.0,
            "wellboreRadiusFt": 0.33,
            "flowRegime": "steady_state",
        },
    )

    assert response.status_code == 200
    assert response.json()["calculationType"] == "radial_flow"
    assert response.json()["method"] == "radial_flow:steady_state"


def test_productivity_index_endpoint_returns_engineering_error_for_invalid_radii() -> None:
    response = client.post(
        "/api/v1/engineering-calculations/productivity-index",
        json={
            "calculationType": "radial_flow",
            "permeabilityMd": 50.0,
            "netPayFt": 40.0,
            "oilViscosityCp": 2.0,
            "oilFvfRbStb": 1.2,
            "drainageRadiusFt": 0.33,
            "wellboreRadiusFt": 0.33,
        },
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "ENGINEERING_INPUT_INVALID"


def test_fracture_pressure_endpoint_returns_screening_estimate() -> None:
    response = client.post(
        "/api/v1/engineering-calculations/fracture-pressure",
        json={
            "trueVerticalDepthFt": 10_000.0,
            "fractureGradientPsiPerFt": 0.75,
            "safetyMarginPsi": 500.0,
        },
    )

    assert response.status_code == 200
    assert response.json()["fracturePressurePsi"] == 7_500.0
    assert response.json()["recommendedMaximumTreatingPressurePsi"] == 7_000.0


def test_fracture_pressure_endpoint_returns_engineering_error_contract() -> None:
    response = client.post(
        "/api/v1/engineering-calculations/fracture-pressure",
        json={
            "trueVerticalDepthFt": 1_000.0,
            "fractureGradientPsiPerFt": 0.75,
            "safetyMarginPsi": 750.0,
        },
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "ENGINEERING_INPUT_INVALID"
    assert response.json()["error"]["requestId"]


def test_recommendations_endpoint_exposes_text_and_sources() -> None:
    with (
        patch("app.services.recommendation_generator.retrieve", return_value=[]),
        patch(
            "app.services.recommendation_generator.generate_text",
            return_value="Recommandation pour le puits PF-01.",
        ),
    ):
        response = client.post(
            "/api/v1/recommendations",
            json={
                "wellName": "PF-01",
                "rockType": "sandstone",
                "porosityFraction": 0.18,
                "permeabilityMd": 50.0,
                "reservoirPressurePsi": 3_000.0,
                "trueVerticalDepthFt": 10_000.0,
                "productivityIndexStbDayPsi": 2.0,
                "fracturePressurePsi": 7_500.0,
            },
        )

        assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ragBacked"
    assert "PF-01" in payload["recommendation"]


def test_recommendations_endpoint_preserves_rag_sources() -> None:
    with (
        patch("app.services.recommendation_generator.retrieve", return_value=[]),
        patch(
            "app.services.recommendation_generator.generate_text",
            return_value="Recommandation pour le puits PF-02.",
        ),
    ):
        response = client.post(
            "/api/v1/recommendations",
            json={
                "wellName": "PF-02",
                "rockType": "limestone",
                "porosityFraction": 0.12,
                "permeabilityMd": 15.0,
                "reservoirPressurePsi": 2_500.0,
                "trueVerticalDepthFt": 8_000.0,
                "sources": [
                    {
                        "sourceType": "rag",
                        "title": "SPE reference",
                        "excerpt": "Relevant completion guidance.",
                        "url": "https://example.com/spe-reference",
                    }
                ],
            },
        )

    assert response.status_code == 200
    assert response.json()["sources"][0]["sourceType"] == "rag"


def test_openapi_exposes_day_three_and_four_routes() -> None:
    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert "/api/v1/engineering-calculations/productivity-index" in response.json()["paths"]
    assert "/api/v1/engineering-calculations/fracture-pressure" in response.json()["paths"]
    assert "/api/v1/recommendations" in response.json()["paths"]


def test_unknown_route_returns_standard_error_envelope() -> None:
    response = client.get("/api/v1/unknown")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "HTTP_ERROR"
    assert response.json()["error"]["requestId"]