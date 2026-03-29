import gc
import time
from pathlib import Path

import mlx.core as mx
from mlx_lm import generate, load
from mlx_lm.tokenizer_utils import TokenizerWrapper

from app.config import MODELS

_loaded_model: tuple[str, object, TokenizerWrapper] | None = None


def _model_name(model_id: str) -> str:
    return next((m.name for m in MODELS if m.id == model_id), model_id)


def _is_downloaded(model_id: str) -> bool:
    """Check if model is cached locally in HuggingFace cache."""
    hf_cache = Path.home() / ".cache" / "huggingface" / "hub"
    model_dir_name = "models--" + model_id.replace("/", "--")
    model_path = hf_cache / model_dir_name
    if not model_path.exists():
        return False
    snapshots = model_path / "snapshots"
    return snapshots.exists() and any(snapshots.iterdir())


def list_models() -> list[dict]:
    result: list[dict] = []
    for m in MODELS:
        result.append({
            "id": m.id,
            "name": m.name,
            "description": m.description,
            "size": m.size,
            "downloaded": _is_downloaded(m.id),
        })
    return result


def _load_model(model_id: str) -> tuple[object, TokenizerWrapper]:
    global _loaded_model
    if _loaded_model is not None and _loaded_model[0] == model_id:
        return _loaded_model[1], _loaded_model[2]
    unload_model()
    model, tokenizer = load(model_id)
    _loaded_model = (model_id, model, tokenizer)
    return model, tokenizer


def unload_model() -> None:
    global _loaded_model
    if _loaded_model is not None:
        _loaded_model = None
        gc.collect()
        mx.metal.clear_cache()


def generate_response(model_id: str, prompt: str, max_tokens: int = 1024) -> dict:
    model, tokenizer = _load_model(model_id)

    if hasattr(tokenizer, "apply_chat_template"):
        messages = [{"role": "user", "content": prompt}]
        formatted = tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
    else:
        formatted = prompt

    start_time = time.perf_counter()
    response_text = generate(
        model,
        tokenizer,
        prompt=formatted,
        max_tokens=max_tokens,
        verbose=False,
    )
    end_time = time.perf_counter()

    total_duration_ms = (end_time - start_time) * 1000
    token_ids = tokenizer.encode(response_text)
    eval_count = len(token_ids)
    tps = eval_count / (total_duration_ms / 1000) if total_duration_ms > 0 else 0.0

    return {
        "response": response_text,
        "eval_count": eval_count,
        "tokens_per_second": round(tps, 2),
        "total_duration_ms": round(total_duration_ms, 1),
        "prompt_eval_duration_ms": 0.0,
    }


def is_healthy() -> bool:
    try:
        import mlx.core as mx
        _ = mx.array([1.0])
        return True
    except Exception:
        return False
