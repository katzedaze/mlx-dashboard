from pydantic import BaseModel


class ModelInfo(BaseModel):
    id: str
    name: str
    description: str
    size: str
    downloaded: bool = False


class SystemMetrics(BaseModel):
    cpu_percent: float
    ram_used_gb: float
    ram_total_gb: float
    ram_percent: float


class BenchmarkRequest(BaseModel):
    model_ids: list[str]
    num_runs: int = 3


class BenchmarkResult(BaseModel):
    model_id: str
    model_name: str
    tokens_per_second: float
    avg_response_time_ms: float
    prompt_eval_time_ms: float
    total_tokens: int
    runs: list[dict]


class EvaluateRequest(BaseModel):
    prompt: str
    model_ids: list[str]
    category: str | None = None
    auto_score: bool = True


class EvaluateResponse(BaseModel):
    model_id: str
    model_name: str
    response_text: str
    tokens_per_second: float
    response_time_ms: float
    total_tokens: int
    auto_scores: dict[str, int] | None = None
    judge_failed: bool = False


class ScoreRequest(BaseModel):
    eval_id: str
    model_id: str
    scores: dict[str, int]


class LeaderboardEntry(BaseModel):
    model_id: str
    model_name: str
    overall_score: float
    criteria_scores: dict[str, float]
    eval_count: int
