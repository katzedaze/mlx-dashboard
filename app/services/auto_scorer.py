import json
import re

from app.config import JUDGE_MODEL, JUDGE_PROMPT_TEMPLATE
from app.services import mlx_client

_VALID_CRITERIA = frozenset({"accuracy", "completeness", "clarity", "creativity", "code_quality"})


def _parse_scores(text: str) -> dict[str, int] | None:
    match = re.search(r"\{[^}]+\}", text)
    if not match:
        return None
    try:
        data = json.loads(match.group())
    except json.JSONDecodeError:
        return None
    scores: dict[str, int] = {}
    for key in _VALID_CRITERIA:
        val = data.get(key)
        if isinstance(val, (int, float)) and 1 <= val <= 5:
            scores[key] = int(round(val))
        else:
            return None
    return scores


def compute_speed_scores(responses: list[dict]) -> dict[str, int]:
    tps_values = [r.get("tokens_per_second", 0) for r in responses]
    min_tps = min(tps_values) if tps_values else 0
    max_tps = max(tps_values) if tps_values else 0
    result: dict[str, int] = {}
    for r in responses:
        tps = r.get("tokens_per_second", 0)
        if max_tps > min_tps:
            score = 1 + 4 * (tps - min_tps) / (max_tps - min_tps)
        else:
            score = 3.0
        result[r["model_id"]] = int(round(score))
    return result


def auto_score_response(prompt: str, response_text: str, max_retries: int = 2) -> dict[str, int] | None:
    judge_prompt = JUDGE_PROMPT_TEMPLATE.format(
        prompt=prompt,
        response=response_text,
    )
    for _ in range(max_retries + 1):
        result = mlx_client.generate_response(JUDGE_MODEL, judge_prompt, max_tokens=256)
        scores = _parse_scores(result["response"])
        if scores is not None:
            return scores
    return None


def auto_score_all(prompt: str, responses: list[dict]) -> list[dict]:
    speed_scores = compute_speed_scores(responses)
    results: list[dict] = []

    for r in responses:
        model_id = r["model_id"]
        scores = auto_score_response(prompt, r["response_text"])
        judge_failed = scores is None
        if judge_failed:
            scores = {k: 3 for k in _VALID_CRITERIA}
        scores["speed"] = speed_scores.get(model_id, 3)
        results.append({
            "model_id": model_id,
            "scores": scores,
            "judge_failed": judge_failed,
        })

    mlx_client.unload_model()
    return results
