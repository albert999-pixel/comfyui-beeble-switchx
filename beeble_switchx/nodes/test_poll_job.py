"""Test node for polling a Beeble job once."""

from __future__ import annotations

import json
import logging

from ..polling import get_job_status

LOGGER = logging.getLogger(__name__)


class BeeblePollJobTestNode:
    CATEGORY = "Beeble/SwitchX/Test"
    FUNCTION = "run"
    OUTPUT_NODE = True
    RETURN_TYPES = ("STRING", "FLOAT", "STRING")
    RETURN_NAMES = ("status", "progress", "status_json")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "job_id": ("STRING", {"default": ""}),
            }
        }

    def run(self, job_id):
        payload = get_job_status(job_id)
        status = str(payload.get("status", ""))
        progress = float(payload.get("progress", 0) or 0)
        status_json = json.dumps(payload, indent=2, ensure_ascii=False)
        LOGGER.info("Beeble job status:\n%s", status_json)
        return (status, progress, status_json)
