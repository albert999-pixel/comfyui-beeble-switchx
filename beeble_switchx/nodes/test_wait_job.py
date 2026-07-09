"""Test node for waiting on a Beeble job."""

from __future__ import annotations

import json
import logging

from ..polling import wait_for_job

LOGGER = logging.getLogger(__name__)


class BeebleWaitJobTestNode:
    CATEGORY = "Beeble/SwitchX/Test"
    FUNCTION = "run"
    OUTPUT_NODE = True
    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("final_status_json", "render_uri_or_url", "alpha_uri_or_url")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "job_id": ("STRING", {"default": ""}),
                "timeout_seconds": ("INT", {"default": 600, "min": 1}),
                "poll_interval_seconds": ("FLOAT", {"default": 2.0, "min": 0.1, "step": 0.1}),
            }
        }

    def run(self, job_id, timeout_seconds, poll_interval_seconds):
        payload = wait_for_job(
            job_id,
            timeout=float(timeout_seconds),
            poll_interval=float(poll_interval_seconds),
        )
        status_json = json.dumps(payload, indent=2, ensure_ascii=False)
        output = payload.get("output")
        render_uri_or_url = ""
        alpha_uri_or_url = ""
        if isinstance(output, dict):
            render_uri_or_url = str(output.get("render") or "")
            alpha_uri_or_url = str(output.get("alpha") or "")
        LOGGER.info("Beeble job completed:\n%s", status_json)
        return (status_json, render_uri_or_url, alpha_uri_or_url)
