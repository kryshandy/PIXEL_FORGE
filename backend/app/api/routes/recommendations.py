"""Recommendation response endpoint and stable Flo/frontend integration contract."""

from fastapi import APIRouter

from app.api.schemas import RecommendationRequest, RecommendationResponse
from app.services.recommendation_generator import generate_recommendation

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.post(
    "",
    response_model=RecommendationResponse,
    summary="Obtenir une reponse de recommandation avec sources",
)
def create_recommendation(request: RecommendationRequest) -> RecommendationResponse:
    """Generate a RAG+LLM-backed recommendation for the given well parameters."""
    return generate_recommendation(request)