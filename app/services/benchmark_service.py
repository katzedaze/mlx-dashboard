import statistics

from app.config import BENCHMARK_PROMPT, MODELS, WARMUP_PROMPT
from app.models.schemas import BenchmarkResult
from app.services import mlx_client


def _model_name(model_id: str) -> str:
    return next((m.name for m in MODELS if m.id == model_id), model_id)


def run_benchmark(model_id: str, num_runs: int = 3) -> BenchmarkResult:
    # Warmup: load model into memory
    mlx_client.generate_response(model_id, WARMUP_PROMPT, max_tokens=32)

    runs: list[dict] = []
    for i in range(num_runs):
        result = mlx_client.generate_response(model_id, BENCHMARK_PROMPT)
        runs.append({
            "run": i + 1,
            "tokens_per_second": result["tokens_per_second"],
            "total_duration_ms": result["total_duration_ms"],
            "prompt_eval_duration_ms": result["prompt_eval_duration_ms"],
            "eval_count": result["eval_count"],
        })

    # Unload model to free memory for next
    mlx_client.unload_model()

    tps_values = [r["tokens_per_second"] for r in runs]
    time_values = [r["total_duration_ms"] for r in runs]
    prompt_eval_values = [r["prompt_eval_duration_ms"] for r in runs]
    total_tokens = sum(r["eval_count"] for r in runs)

    return BenchmarkResult(
        model_id=model_id,
        model_name=_model_name(model_id),
        tokens_per_second=round(statistics.mean(tps_values), 2),
        avg_response_time_ms=round(statistics.mean(time_values), 1),
        prompt_eval_time_ms=round(statistics.mean(prompt_eval_values), 1),
        total_tokens=total_tokens,
        runs=runs,
    )


def run_benchmarks(model_ids: list[str], num_runs: int = 3) -> list[BenchmarkResult]:
    results: list[BenchmarkResult] = []
    for model_id in model_ids:
        result = run_benchmark(model_id, num_runs)
        results.append(result)
    return results
