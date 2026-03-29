import psutil

from app.models.schemas import SystemMetrics


def get_metrics() -> SystemMetrics:
    mem = psutil.virtual_memory()
    return SystemMetrics(
        cpu_percent=psutil.cpu_percent(interval=0.1),
        ram_used_gb=round(mem.used / (1024**3), 2),
        ram_total_gb=round(mem.total / (1024**3), 2),
        ram_percent=mem.percent,
    )
