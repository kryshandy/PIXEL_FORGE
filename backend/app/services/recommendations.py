"""Deterministic recommendation adapter, replaceable by Flo's RAG/LLM provider."""

from app.api.schemas import (
    RecommendationRequest,
    RecommendationResponse,
    SourceCitation,
)

_DISCLAIMER = (
    "Pré-analyse destinée au prototype Pixel Forge. Toute décision de complétion ou "
    "de traitement doit être validée par un ingénieur qualifié et le moteur RAG/LLM."
)


def build_preliminary_recommendation(request: RecommendationRequest) -> RecommendationResponse:
    """Create a safe deterministic handoff until the RAG/LLM provider is connected.

    Flo can replace this function with an adapter that preserves the public response
    contract while sourcing the text and citations from the retrieval pipeline.
    """
    metrics = [
        f"roche : {request.rock_type}",
        f"porosité : {request.porosity_fraction:.1%}",
        f"perméabilité : {request.permeability_md:.2f} md",
        f"pression réservoir : {request.reservoir_pressure_psi:.0f} psi",
        f"profondeur TVD : {request.true_vertical_depth_ft:.0f} ft",
    ]
    if request.productivity_index_stb_day_psi is not None:
        metrics.append(
            "indice de productivité : "
            f"{request.productivity_index_stb_day_psi:.3f} STB/jour/psi"
        )
    if request.fracture_pressure_psi is not None:
        metrics.append(
            "pression de fracturation estimée : "
            f"{request.fracture_pressure_psi:.0f} psi"
        )

    sources = request.sources or [
        SourceCitation(
            source_type="calculation",
            title="Calculs d'ingénierie Pixel Forge",
            excerpt=(
                "Résultats calculés par les modules d'indice de productivité "
                "et de pression de fracturation."
            ),
        )
    ]
    recommendation = (
        f"Pré-analyse pour le puits {request.well_name} : "
        + "; ".join(metrics)
        + ". Les données sont prêtes pour une recommandation finale fondée sur le corpus RAG. "
        "Avant toute décision, confronter cette pré-analyse aux sources récupérées et aux "
        "contraintes opérationnelles du puits."
    )
    return RecommendationResponse(
        status="preliminary",
        recommendation=recommendation,
        sources=sources,
        disclaimer=_DISCLAIMER,
    )
