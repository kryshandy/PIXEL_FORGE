"""Recommendation response endpoint and stable Flo/frontend integration contract."""

from fastapi import APIRouter

from app.api.schemas import RecommendationRequest, RecommendationResponse
from app.services.recommendations import build_preliminary_recommendation

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.post(
    "",
    response_model=RecommendationResponse,
    summary="Obtenir une réponse de recommandation avec sources",
)
def create_recommendation(request: RecommendationRequest) -> RecommendationResponse:
    """Expose a frontend-ready recommendation contract pending the RAG/LLM adapter."""
    return build_preliminary_recommendation(request)
