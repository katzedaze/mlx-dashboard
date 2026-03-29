import asyncio
from concurrent.futures import ThreadPoolExecutor

from fastapi import APIRouter

from app.config import EVAL_CATEGORIES, JUDGE_MODEL
from app.models.schemas import EvaluateRequest
from app.services.auto_scorer import auto_score_all
from app.services.evaluation_service import evaluate_models
from app.services.scoring_service import save_evaluation, save_score

router = APIRouter(prefix="/api/evaluate", tags=["evaluate"])

_executor = ThreadPoolExecutor(max_workers=1)


@router.get("/categories")
async def get_categories() -> dict:
    return EVAL_CATEGORIES


@router.get("/judge")
async def get_judge_info() -> dict:
    return {"judge_model": JUDGE_MODEL}


def _run_evaluation_sync(prompt: str, model_ids: list[str], category: str | None, do_auto_score: bool) -> dict:
    eval_id, responses = evaluate_models(prompt, model_ids)
    response_dicts = [r.model_dump() for r in responses]

    if do_auto_score:
        auto_results = auto_score_all(prompt, response_dicts)
        enriched: list[dict] = []
        for resp, auto in zip(response_dicts, auto_results):
            resp["auto_scores"] = auto["scores"]
            resp["judge_failed"] = auto["judge_failed"]
            enriched.append(resp)
            save_score(eval_id, resp["model_id"], auto["scores"])
        save_evaluation(eval_id, prompt, category, enriched)
        return {"eval_id": eval_id, "responses": enriched}

    save_evaluation(eval_id, prompt, category, response_dicts)
    return {"eval_id": eval_id, "responses": response_dicts}


@router.post("/run")
async def run_evaluation(req: EvaluateRequest) -> dict:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        _executor, _run_evaluation_sync, req.prompt, req.model_ids, req.category, req.auto_score
    )


@router.get("/history")
async def get_history() -> list[dict]:
    from app.services.scoring_service import get_evaluation_history
    return get_evaluation_history()
