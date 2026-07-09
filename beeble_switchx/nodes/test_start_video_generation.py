"""Test node for starting a Beeble video generation job."""

from __future__ import annotations

import json
import logging

from ..generation import start_switchx_generation

LOGGER = logging.getLogger(__name__)


class BeebleStartVideoGenerationTestNode:
    CATEGORY = "Beeble/SwitchX/Test"
    FUNCTION = "run"
    OUTPUT_NODE = True
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("job_id", "status_json")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "source_uri": ("STRING", {"default": ""}),
                "alpha_mode": (["auto", "fill", "select"], {"default": "auto"}),
                "prompt": ("STRING", {"default": ""}),
                "seed": ("INT", {"default": 0}),
                "max_resolution": ([720, 1080], {"default": 720}),
                "alpha_keyframe_index": ("INT", {"default": 0, "min": 0}),
            },
            "optional": {
                "reference_image_uri": ("STRING", {"default": ""}),
                "alpha_uri": ("STRING", {"default": ""}),
            },
        }

    def run(
        self,
        source_uri,
        alpha_mode,
        prompt,
        seed,
        max_resolution,
        alpha_keyframe_index,
        reference_image_uri="",
        alpha_uri="",
    ):
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
        )
        job_id = str(payload.get("id", ""))
        status_json = json.dumps(payload, indent=2, ensure_ascii=False)
        LOGGER.info("Beeble video generation started:\n%s", status_json)
        return (job_id, status_json)
