from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.routers import benchmark, evaluate, models, scoring
from app.services import mlx_client, system_monitor

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"

app = FastAPI(title="MLX Dashboard", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(models.router)
app.include_router(benchmark.router)
app.include_router(evaluate.router)
app.include_router(scoring.router)


@app.get("/api/system/metrics")
async def system_metrics():
    return system_monitor.get_metrics()


@app.get("/api/system/health")
async def health():
    healthy = mlx_client.is_healthy()
    return {"mlx": healthy}


app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")
