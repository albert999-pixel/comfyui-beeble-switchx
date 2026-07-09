"""High-level Beeble SwitchX flows built from reusable helpers."""

from __future__ import annotations

import logging
import tempfile
from pathlib import Path
from typing import Any

from .errors import BeebleGenerationError
from .generation import start_switchx_generation
from .masks import empty_mask_like_image, load_mask_file_as_tensor, save_mask_as_grayscale_png
from .media import (
    download_file,
    load_image_file_as_tensor,
    load_video_file_as_input,
    save_image_tensor_as_png,
    save_video_input_to_file,
)
from .polling import wait_for_job
from .runtime import create_runtime_path
from .upload import upload_file


LOGGER = logging.getLogger(__name__)


def _create_temp_path(prefix: str, suffix: str) -> Path:
    return Path(
        tempfile.NamedTemporaryFile(
            prefix=prefix,
            suffix=suffix,
            delete=False,
        ).name
    )


def _extract_render_url(payload: dict[str, Any]) -> str:
    output = payload.get("output")
    if not isinstance(output, dict):
        raise BeebleGenerationError("Beeble generation completed without output data.")

    render_url = output.get("render")
    if not isinstance(render_url, str) or not render_url.strip():
        raise BeebleGenerationError("Beeble generation completed without a render URL.")

    return render_url.strip()


def _extract_alpha_url(payload: dict[str, Any]) -> str:
    output = payload.get("output")
    if not isinstance(output, dict):
        return ""

    alpha_url = output.get("alpha")
    if not isinstance(alpha_url, str) or not alpha_url.strip():
        return ""

    return alpha_url.strip()


def run_switchx_image(
    image,
    alpha_mode: str,
    prompt: str,
    seed: int,
    max_resolution: int,
    reference_image=None,
    mask=None,
    poll_interval: float = 2.0,
    timeout: float = 600.0,
    api_key: str | None = None,
    ) -> dict[str, Any]:
    """Run the full Beeble SwitchX image flow and return the rendered IMAGE."""
    if alpha_mode not in {"auto", "fill", "select", "custom"}:
        raise ValueError("alpha_mode must be auto, fill, select, or custom")
    if alpha_mode in {"select", "custom"} and mask is None:
        raise ValueError("mask is required when alpha_mode is select or custom")
    if alpha_mode in {"auto", "fill"} and mask is not None:
        LOGGER.warning(
            "Beeble image: mask is connected but will be ignored because alpha_mode=%r.",
            alpha_mode,
        )

    source_path = _create_temp_path("beeble_switchx_image_source_", ".png")
    reference_path = None
    alpha_path = None
    render_path = _create_temp_path("beeble_switchx_image_render_", ".png")
    alpha_render_path = None

    try:
        LOGGER.info("Beeble image: preparing source image.")
        save_image_tensor_as_png(image, str(source_path))
        source_uri = upload_file(str(source_path), api_key=api_key)
        LOGGER.info("Beeble image: source uploaded.")

        reference_image_uri = ""
        if reference_image is not None:
            reference_path = _create_temp_path("beeble_switchx_image_reference_", ".png")
            save_image_tensor_as_png(reference_image, str(reference_path))
            reference_image_uri = upload_file(str(reference_path), api_key=api_key)
            LOGGER.info("Beeble image: reference uploaded.")

        alpha_uri = ""
        if alpha_mode in {"select", "custom"} and mask is not None:
            alpha_path = _create_temp_path("beeble_switchx_image_alpha_", ".png")
            save_mask_as_grayscale_png(mask, str(alpha_path))
            alpha_uri = upload_file(str(alpha_path), api_key=api_key)
            LOGGER.info("Beeble image: alpha mask uploaded.")

        payload = start_switchx_generation(
            source_uri=source_uri,
            generation_type="image",
            alpha_mode=alpha_mode,
            prompt=prompt,
            reference_image_uri=reference_image_uri,
            alpha_uri=alpha_uri,
            seed=seed,
            max_resolution=max_resolution,
            api_key=api_key,
        )
        job_id = str(payload.get("id") or "")
        if job_id:
            LOGGER.info("Beeble image: job %s started.", job_id)
        else:
            LOGGER.info("Beeble image: generation started.")

        final_payload = wait_for_job(
            job_id,
            poll_interval=poll_interval,
            timeout=timeout,
            api_key=api_key,
        )
        render_url = _extract_render_url(final_payload)
        alpha_url = _extract_alpha_url(final_payload)

        LOGGER.info("Beeble image: downloading render.")
        download_file(render_url, str(render_path))
        result_image = load_image_file_as_tensor(str(render_path))
        result_alpha = empty_mask_like_image(result_image)

        if alpha_url:
            alpha_render_path = _create_temp_path("beeble_switchx_image_alpha_render_", ".png")
            LOGGER.info("Beeble image: downloading alpha.")
            download_file(alpha_url, str(alpha_render_path))
            result_alpha = load_mask_file_as_tensor(str(alpha_render_path))
        LOGGER.info("Beeble image: render is ready.")

        return {
            "image": result_image,
            "alpha": result_alpha,
            "job_id": job_id,
            "render_url": render_url,
            "alpha_url": alpha_url,
            "status_payload": final_payload,
        }
    finally:
        source_path.unlink(missing_ok=True)
        render_path.unlink(missing_ok=True)
        if reference_path is not None:
            reference_path.unlink(missing_ok=True)
        if alpha_path is not None:
            alpha_path.unlink(missing_ok=True)
        if alpha_render_path is not None:
            alpha_render_path.unlink(missing_ok=True)


def run_switchx_video(
    video,
    alpha_mode: str,
    prompt: str,
    seed: int,
    max_resolution: int,
    reference_image=None,
    alpha_keyframe_mask=None,
    alpha_video=None,
    alpha_keyframe_index: int = 0,
    poll_interval: float = 2.0,
    timeout: float = 600.0,
    api_key: str | None = None,
) -> dict[str, Any]:
    """Run the full Beeble SwitchX video flow and return the rendered VIDEO."""
    if alpha_mode not in {"auto", "fill", "select", "custom"}:
        raise ValueError("alpha_mode must be auto, fill, select, or custom")
    if alpha_mode == "select" and alpha_keyframe_mask is None:
        raise ValueError("alpha_keyframe_mask is required when alpha_mode is select")
    if alpha_mode == "custom" and alpha_video is None:
        raise ValueError("alpha_video is required when alpha_mode is custom")
    if alpha_keyframe_index < 0:
        raise ValueError("alpha_keyframe_index must be >= 0")

    source_path = _create_temp_path("beeble_switchx_video_source_", ".mp4")
    reference_path = None
    alpha_path = None
    render_path = create_runtime_path("beeble_switchx_video_render_", ".mp4")
    alpha_render_path = None

    try:
        LOGGER.info("Beeble video: preparing source video.")
        save_video_input_to_file(video, str(source_path))
        source_uri = upload_file(str(source_path), api_key=api_key)
        LOGGER.info("Beeble video: source uploaded.")

        reference_image_uri = ""
        if reference_image is not None:
            reference_path = _create_temp_path("beeble_switchx_video_reference_", ".png")
            save_image_tensor_as_png(reference_image, str(reference_path))
            reference_image_uri = upload_file(str(reference_path), api_key=api_key)
            LOGGER.info("Beeble video: reference uploaded.")

        alpha_uri = ""
        if alpha_mode == "select" and alpha_keyframe_mask is not None:
            alpha_path = _create_temp_path("beeble_switchx_video_alpha_", ".png")
            save_mask_as_grayscale_png(alpha_keyframe_mask, str(alpha_path))
            alpha_uri = upload_file(str(alpha_path), api_key=api_key)
            LOGGER.info("Beeble video: alpha keyframe mask uploaded.")
        elif alpha_mode == "custom" and alpha_video is not None:
            alpha_path = _create_temp_path("beeble_switchx_video_alpha_", ".mp4")
            save_video_input_to_file(alpha_video, str(alpha_path))
            alpha_uri = upload_file(str(alpha_path), api_key=api_key)
            LOGGER.info("Beeble video: custom alpha video uploaded.")

        payload = start_switchx_generation(
            source_uri=source_uri,
            generation_type="video",
            alpha_mode=alpha_mode,
            prompt=prompt,
            reference_image_uri=reference_image_uri,
            alpha_uri=alpha_uri,
            alpha_keyframe_index=alpha_keyframe_index,
            seed=seed,
            max_resolution=max_resolution,
            api_key=api_key,
        )
        job_id = str(payload.get("id") or "")
        if job_id:
            LOGGER.info("Beeble video: job %s started.", job_id)
        else:
            LOGGER.info("Beeble video: generation started.")

        final_payload = wait_for_job(
            job_id,
            poll_interval=poll_interval,
            timeout=timeout,
            api_key=api_key,
        )
        render_url = _extract_render_url(final_payload)
        alpha_url = _extract_alpha_url(final_payload)

        LOGGER.info("Beeble video: downloading render.")
        download_file(render_url, str(render_path))
        result_video = load_video_file_as_input(str(render_path))
        result_alpha_video = result_video
        if alpha_url:
            alpha_render_path = create_runtime_path("beeble_switchx_video_alpha_render_", ".mp4")
            LOGGER.info("Beeble video: downloading alpha.")
            download_file(alpha_url, str(alpha_render_path))
            result_alpha_video = load_video_file_as_input(str(alpha_render_path))
        else:
            LOGGER.warning(
                "Beeble video: alpha output is missing, using render video as fallback."
            )
        LOGGER.info("Beeble video: render is ready.")

        return {
            "video": result_video,
            "alpha_video": result_alpha_video,
            "job_id": job_id,
            "render_url": render_url,
            "alpha_url": alpha_url,
            "status_payload": final_payload,
        }
    finally:
        source_path.unlink(missing_ok=True)
        if reference_path is not None:
            reference_path.unlink(missing_ok=True)
        if alpha_path is not None:
            alpha_path.unlink(missing_ok=True)


__all__ = ["run_switchx_image", "run_switchx_video"]
