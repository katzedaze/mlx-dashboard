import json
from pathlib import Path

from app.config import MODELS, SCORING_CRITERIA
from app.models.schemas import LeaderboardEntry

_DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "results.json"


def _load_data() -> dict:
    if _DATA_PATH.exists():
        return json.loads(_DATA_PATH.read_text())
    return {"scores": [], "evaluations": []}


def _save_data(data: dict) -> None:
    _DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    _DATA_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2))


def _model_name(model_id: str) -> str:
    return next((m.name for m in MODELS if m.id == model_id), model_id)


def save_score(eval_id: str, model_id: str, scores: dict[str, int]) -> None:
    data = _load_data()
    data["scores"].append({
        "eval_id": eval_id,
        "model_id": model_id,
        "scores": scores,
    })
    _save_data(data)


def save_evaluation(eval_id: str, prompt: str, category: str | None, responses: list[dict]) -> None:
    data = _load_data()
    data["evaluations"].append({
        "eval_id": eval_id,
        "prompt": prompt,
        "category": category,
        "responses": responses,
    })
    _save_data(data)


def get_leaderboard() -> list[LeaderboardEntry]:
    data = _load_data()
    scores_by_model: dict[str, list[dict[str, int]]] = {}
    for entry in data["scores"]:
        mid = entry["model_id"]
        scores_by_model.setdefault(mid, []).append(entry["scores"])

    leaderboard: list[LeaderboardEntry] = []
    for model_id, score_list in scores_by_model.items():
        criteria_avgs: dict[str, float] = {}
        for criterion in SCORING_CRITERIA:
            vals = [s.get(criterion, 0) for s in score_list if criterion in s]
            criteria_avgs[criterion] = round(sum(vals) / len(vals), 2) if vals else 0.0

        overall = sum(
            criteria_avgs.get(k, 0) * v["weight"]
            for k, v in SCORING_CRITERIA.items()
        )

        leaderboard.append(LeaderboardEntry(
            model_id=model_id,
            model_name=_model_name(model_id),
            overall_score=round(overall, 2),
            criteria_scores=criteria_avgs,
            eval_count=len(score_list),
        ))

    return sorted(leaderboard, key=lambda x: x.overall_score, reverse=True)


def get_evaluation_history() -> list[dict]:
    data = _load_data()
    return data.get("evaluations", [])
