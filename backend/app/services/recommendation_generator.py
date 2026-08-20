"""LLM-backed recommendation generation: RAG context + engineering results + Claude.

Replaces `app.services.recommendations.build_preliminary_recommendation` as the
production path once `ANTHROPIC_API_KEY` is configured (see `app.services.llm_config`).
"""

from __future__ import annotations

from app.api.schemas import RecommendationRequest, RecommendationResponse, SourceCitation
from app.rag.retrieve import RetrievedChunk, retrieve
from app.services.gemini_client import generate_text

_SYSTEM_PROMPT = (
    "Tu es PetroSage, un copilote d'ingenierie pour la completion et la "
    "production de puits petroliers conventionnels. Tu formules une "
    "recommandation de strategie de completion/production en te fondant "
    "strictement sur : (1) les resultats de calcul d'ingenierie fournis, et "
    "(2) les extraits documentaires fournis. Ne jamais inventer de chiffre "
    "absent des donnees fournies. Reponds en francais, de maniere concise et "
    "actionnable pour un ingenieur de reservoir. Termine toujours en rappelant "
    "que cette recommandation doit etre validee par un ingenieur qualifie."
)

_EXCERPT_MAX_LENGTH = 400


def _build_retrieval_query(request: RecommendationRequest) -> str:
    """Turn the well's reservoir parameters into a natural-language RAG query."""
    return (
        f"completion production puits petrolier conventionnel {request.rock_type} "
        f"porosite permeabilite pression reservoir profondeur "
        f"indice de productivite pression de fracturation"
    )


def _format_calculation_context(request: RecommendationRequest) -> str:
    """Render the engineering inputs/results as plain text for the prompt."""
    lines = [
        f"Puits : {request.well_name}",
        f"Type de roche : {request.rock_type}",
        f"Porosite : {request.porosity_fraction:.1%}",
        f"Permeabilite : {request.permeability_md:.2f} md",
        f"Pression reservoir : {request.reservoir_pressure_psi:.0f} psi",
        f"Profondeur TVD : {request.true_vertical_depth_ft:.0f} ft",
    ]
    if request.productivity_index_stb_day_psi is not None:
        lines.append(
            f"Indice de productivite : {request.productivity_index_stb_day_psi:.3f} STB/jour/psi"
        )
    if request.fracture_pressure_psi is not None:
        lines.append(f"Pression de fracturation estimee : {request.fracture_pressure_psi:.0f} psi")
    return "\n".join(lines)


def _format_rag_context(chunks: list[RetrievedChunk]) -> str:
    """Render retrieved chunks as a numbered, citable context block."""
    if not chunks:
        return "Aucun extrait documentaire pertinent trouve dans le corpus."
    blocks = [
        f"[{index}] (source : {chunk.source})\n{chunk.text.strip()}"
        for index, chunk in enumerate(chunks, start=1)
    ]
    return "\n\n".join(blocks)


def _build_user_prompt(request: RecommendationRequest, chunks: list[RetrievedChunk]) -> str:
    return (
        "## Resultats de calcul d'ingenierie\n"
        f"{_format_calculation_context(request)}\n\n"
        "## Extraits documentaires (corpus technique)\n"
        f"{_format_rag_context(chunks)}\n\n"
        "## Tache\n"
        "Redige une recommandation de strategie de completion et de production "
        "pour ce puits, en t'appuyant sur les calculs et les extraits ci-dessus."
    )


def _chunk_to_source_citation(chunk: RetrievedChunk) -> SourceCitation:
    excerpt = chunk.text.strip()[:_EXCERPT_MAX_LENGTH]
    return SourceCitation(
        source_type="rag",
        title=chunk.source,
        excerpt=excerpt,
    )


def generate_recommendation(request: RecommendationRequest) -> RecommendationResponse:
    """Generate a Claude-backed recommendation grounded in RAG + engineering results.

    Args:
        request: Well/reservoir parameters, including any pre-computed
            engineering results (productivity index, fracture pressure).

    Returns:
        A `RecommendationResponse` whose `sources` combine the RAG chunks that
        grounded the answer with any calculation sources already supplied by
        the caller.

    Raises:
        RuntimeError: If `ANTHROPIC_API_KEY` is not configured (see
            `app.services.llm_config.LlmSettings.from_environment`).
    """
    query = _build_retrieval_query(request)
    chunks = retrieve(query)

    user_prompt = _build_user_prompt(request, chunks)
    recommendation_text = generate_text(_SYSTEM_PROMPT, user_prompt)

    sources = list(request.sources) + [_chunk_to_source_citation(chunk) for chunk in chunks]

    return RecommendationResponse(
        status="preliminary",
        recommendation=recommendation_text,
        sources=sources,
        disclaimer=(
            "Recommandation generee par le copilote IA PetroSage (RAG + LLM + "
            "calculs d'ingenierie). Toute decision de completion ou de "
            "traitement doit etre validee par un ingenieur qualifie."
        ),
    )