from __future__ import annotations

from unittest.mock import patch

import pytest

from app.api.schemas import RecommendationRequest
from app.rag.retrieve import RetrievedChunk
from app.services import recommendation_generator


def _build_request(**overrides: object) -> RecommendationRequest:
    defaults: dict[str, object] = {
        "well_name": "Puits-Test-1",
        "rock_type": "gres",
        "porosity_fraction": 0.18,
        "permeability_md": 45.0,
        "reservoir_pressure_psi": 3200.0,
        "true_vertical_depth_ft": 8500.0,
    }
    defaults.update(overrides)
    return RecommendationRequest(**defaults)  # type: ignore[arg-type]


def _fake_chunks() -> list[RetrievedChunk]:
    return [
        RetrievedChunk(
            text="Extrait technique sur la pression de fracturation en reservoir conventionnel.",
            source="09_fracturing_pressure_lei_2024.pdf",
            chunk_index=3,
            distance=0.42,
        ),
        RetrievedChunk(
            text="Extrait sur l'indice de productivite en ecoulement radial.",
            source="06_intro_petroleum_engineering.pdf",
            chunk_index=12,
            distance=0.47,
        ),
    ]


def test_generate_recommendation_calls_retrieve_and_claude() -> None:
    request = _build_request()

    with (
        patch(
            "app.services.recommendation_generator.retrieve",
            return_value=_fake_chunks(),
        ) as mock_retrieve,
        patch(
            "app.services.recommendation_generator.generate_text",
            return_value="Recommandation generee par Claude.",
        ) as mock_generate_text,
    ):
        response = recommendation_generator.generate_recommendation(request)

    mock_retrieve.assert_called_once()
    mock_generate_text.assert_called_once()
    assert response.recommendation == "Recommandation generee par Claude."


def test_generate_recommendation_includes_rag_sources() -> None:
    request = _build_request()

    with (
        patch(
            "app.services.recommendation_generator.retrieve",
            return_value=_fake_chunks(),
        ),
        patch(
            "app.services.recommendation_generator.generate_text",
            return_value="Recommandation.",
        ),
    ):
        response = recommendation_generator.generate_recommendation(request)

    rag_sources = [source for source in response.sources if source.source_type == "rag"]
    assert len(rag_sources) == 2
    assert {source.title for source in rag_sources} == {
        "09_fracturing_pressure_lei_2024.pdf",
        "06_intro_petroleum_engineering.pdf",
    }

def test_generate_recommendation_dedupes_sources_from_same_document() -> None:
    """Regression test: retrieve() can return several chunks from the same
    PDF (small/skewed corpus), which used to list that file multiple times
    in the UI's Sources section."""
    request = _build_request()
    repeated_source_chunks = [
        RetrievedChunk(
            text=f"Extrait {index} sur le controle des sables.",
            source="06_intro_petroleum_engineering.pdf",
            chunk_index=index,
            distance=0.30 + index * 0.01,
        )
        for index in range(6)
    ]

    with (
        patch(
            "app.services.recommendation_generator.retrieve",
            return_value=repeated_source_chunks,
        ) as mock_retrieve,
        patch(
            "app.services.recommendation_generator.generate_text",
            return_value="Recommandation.",
        ) as mock_generate_text,
    ):
        response = recommendation_generator.generate_recommendation(request)

    rag_sources = [source for source in response.sources if source.source_type == "rag"]
    assert len(rag_sources) == 1
    assert rag_sources[0].title == "06_intro_petroleum_engineering.pdf"
    # The most relevant excerpt (lowest distance = first chunk) is kept.
    assert "Extrait 0" in rag_sources[0].excerpt

    # The LLM prompt still receives every retrieved chunk, deduped or not:
    # repeated source files can still hold distinct, useful passages.
    mock_retrieve.assert_called_once()
    user_prompt = mock_generate_text.call_args.args[1]
    assert "Extrait 5" in user_prompt

def test_generate_recommendation_preserves_caller_supplied_sources() -> None:
    from app.api.schemas import SourceCitation

    request = _build_request(
        sources=[
            SourceCitation(
                source_type="calculation",
                title="Calcul indice de productivite",
                excerpt="Resultat du module d'ingenierie.",
            )
        ]
    )

    with (
        patch(
            "app.services.recommendation_generator.retrieve",
            return_value=[],
        ),
        patch(
            "app.services.recommendation_generator.generate_text",
            return_value="Recommandation.",
        ),
    ):
        response = recommendation_generator.generate_recommendation(request)

    calculation_sources = [
        source for source in response.sources if source.source_type == "calculation"
    ]
    assert len(calculation_sources) == 1
    assert calculation_sources[0].title == "Calcul indice de productivite"


def test_generate_recommendation_handles_empty_rag_results() -> None:
    request = _build_request()

    with (
        patch(
            "app.services.recommendation_generator.retrieve",
            return_value=[],
        ),
        patch(
            "app.services.recommendation_generator.generate_text",
            return_value="Recommandation sans contexte documentaire.",
        ) as mock_generate_text,
    ):
        response = recommendation_generator.generate_recommendation(request)

    user_prompt = mock_generate_text.call_args.args[1]
    assert "Aucun extrait documentaire pertinent" in user_prompt
    assert response.recommendation == "Recommandation sans contexte documentaire."


def test_generate_recommendation_response_status_is_rag_backed() -> None:
    request = _build_request()

    with (
        patch("app.services.recommendation_generator.retrieve", return_value=[]),
        patch(
            "app.services.recommendation_generator.generate_text",
            return_value="Recommandation.",
        ),
    ):
        response = recommendation_generator.generate_recommendation(request)

    assert response.status == "ragBacked"


@pytest.mark.parametrize(
    ("field_name", "value", "expected_fragment"),
    [
        ("productivity_index_stb_day_psi", 12.5, "Indice de productivite"),
        ("fracture_pressure_psi", 5200.0, "Pression de fracturation estimee"),
    ],
)
def test_calculation_context_includes_optional_fields_when_present(
    field_name: str, value: float, expected_fragment: str
) -> None:
    request = _build_request(**{field_name: value})

    context = recommendation_generator._format_calculation_context(request)

    assert expected_fragment in context