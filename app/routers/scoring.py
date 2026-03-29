from fastapi import APIRouter

from app.config import SCORING_CRITERIA
from app.models.schemas import LeaderboardEntry, ScoreRequest
from app.services.scoring_service import get_leaderboard, save_score

router = APIRouter(prefix="/api/scoring", tags=["scoring"])


@router.post("/rate")
async def rate_response(req: ScoreRequest) -> dict:
    save_score(req.eval_id, req.model_id, req.scores)
    return {"status": "ok"}


@router.get("/leaderboard", response_model=list[LeaderboardEntry])
async def leaderboard() -> list[LeaderboardEntry]:
    return get_leaderboard()


@router.get("/criteria")
async def get_criteria() -> dict:
    return SCORING_CRITERIA
