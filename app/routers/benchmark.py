import asyncio
from concurrent.futures import ThreadPoolExecutor

from fastapi import APIRouter

from app.models.schemas import BenchmarkRequest, BenchmarkResult
from app.services.benchmark_service import run_benchmarks

router = APIRouter(prefix="/api/benchmark", tags=["benchmark"])

_latest_results: list[BenchmarkResult] = []
_executor = ThreadPoolExecutor(max_workers=1)


@router.post("/run", response_model=list[BenchmarkResult])
async def run_benchmark_endpoint(req: BenchmarkRequest) -> list[BenchmarkResult]:
    global _latest_results
    loop = asyncio.get_event_loop()
    results = await loop.run_in_executor(
        _executor, run_benchmarks, req.model_ids, req.num_runs
    )
    _latest_results = results
    return results


@router.get("/results", response_model=list[BenchmarkResult])
async def get_results() -> list[BenchmarkResult]:
    return _latest_results
