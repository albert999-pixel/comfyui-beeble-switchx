"""Test node for downloading Beeble video results."""

from __future__ import annotations

import json
import logging

from ..media import download_file, load_video_file_as_input
from ..runtime import create_runtime_path


LOGGER = logging.getLogger(__name__)


class BeebleDownloadVideoTestNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "render_url": ("STRING", {"default": ""}),
            }
        }

    RETURN_TYPES = ("VIDEO", "STRING")
    RETURN_NAMES = ("video", "debug_json")
    FUNCTION = "run"
    CATEGORY = "Beeble/SwitchX/Test"

    def run(self, render_url: str):
        if not render_url.strip():
            raise ValueError("render_url is required")

        temp_path = create_runtime_path("beeble_download_", ".mp4")
        downloaded_path = download_file(render_url, str(temp_path))
        video = load_video_file_as_input(downloaded_path)

        payload = {
            "render_url": render_url,
            "file_path": str(downloaded_path),
        }
        debug_json = json.dumps(payload, ensure_ascii=False, indent=2)
        LOGGER.info("Beeble video download test:\n%s", debug_json)
        return (video, debug_json)
