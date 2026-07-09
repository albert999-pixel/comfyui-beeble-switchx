"""Generation helpers for SwitchX jobs."""

from __future__ import annotations

from typing import Any

from .api import api_request

VALID_GENERATION_TYPES = {"image", "video"}
VALID_ALPHA_MODES = {"auto", "fill", "select", "custom"}
VALID_MAX_RESOLUTIONS = {720, 1080}


def start_switchx_generation(
    source_uri: str,
    generation_type: str,
    alpha_mode: str,
    prompt: str | None = None,
    reference_image_uri: str | None = None,
    alpha_uri: str | None = None,
    alpha_keyframe_index: int | None = None,
    seed: int | None = None,
    max_resolution: int | None = None,
    api_key: str | None = None,
) -> dict[str, Any]:
    """Start a Beeble SwitchX generation job."""
    cleaned_source_uri = source_uri.strip()
    if not cleaned_source_uri:
        raise ValueError("source_uri is required")

    if generation_type not in VALID_GENERATION_TYPES:
        raise ValueError("generation_type must be 'image' or 'video'")

    if alpha_mode not in VALID_ALPHA_MODES:
        raise ValueError("alpha_mode must be auto, fill, select, or custom")

    if alpha_mode in {"select", "custom"} and not (alpha_uri and alpha_uri.strip()):
        raise ValueError("alpha_uri is required when alpha_mode is 'select' or 'custom'")

    if not ((prompt and prompt.strip()) or (reference_image_uri and reference_image_uri.strip())):
        raise ValueError("At least one of prompt or reference_image_uri must be provided")

    if max_resolution is not None and max_resolution not in VALID_MAX_RESOLUTIONS:
        raise ValueError("max_resolution must be 720 or 1080")

    if alpha_keyframe_index is not None and alpha_keyframe_index < 0:
        raise ValueError("alpha_keyframe_index must be >= 0")

    payload: dict[str, Any] = {
        "source_uri": cleaned_source_uri,
        "generation_type": generation_type,
        "alpha_mode": alpha_mode,
    }

    if prompt is not None and prompt.strip():
        payload["prompt"] = prompt.strip()
    if reference_image_uri is not None and reference_image_uri.strip():
        payload["reference_image_uri"] = reference_image_uri.strip()
    if alpha_uri is not None and alpha_uri.strip():
        payload["alpha_uri"] = alpha_uri.strip()
    if generation_type == "video" and alpha_mode == "select" and alpha_keyframe_index is not None:
        payload["alpha_keyframe_index"] = alpha_keyframe_index
    if seed is not None:
        payload["seed"] = seed
    if max_resolution is not None:
        payload["max_resolution"] = max_resolution

    return api_request(
        "POST",
        "/v1/switchx/generations",
        api_key=api_key,
        json=payload,
    )


__all__ = [
    "VALID_ALPHA_MODES",
    "VALID_GENERATION_TYPES",
    "VALID_MAX_RESOLUTIONS",
    "start_switchx_generation",
]
