import uuid

from app.config import MODELS
from app.models.schemas import EvaluateResponse
from app.services import mlx_client


def _model_name(model_id: str) -> str:
    return next((m.name for m in MODELS if m.id == model_id), model_id)


def _evaluate_single(model_id: str, prompt: str) -> EvaluateResponse:
    result = mlx_client.generate_response(model_id, prompt)
    return EvaluateResponse(
        model_id=model_id,
        model_name=_model_name(model_id),
        response_text=result["response"],
        tokens_per_second=result["tokens_per_second"],
        response_time_ms=result["total_duration_ms"],
        total_tokens=result["eval_count"],
    )


def evaluate_models(
    prompt: str, model_ids: list[str]
) -> tuple[str, list[EvaluateResponse]]:
    eval_id = str(uuid.uuid4())[:8]
    responses: list[EvaluateResponse] = []
    for model_id in model_ids:
        resp = _evaluate_single(model_id, prompt)
        responses.append(resp)
        mlx_client.unload_model()
    return eval_id, responses
