"""Test node for uploading a VIDEO to Beeble."""

from __future__ import annotations

import json
import logging
import tempfile
from pathlib import Path

from ..media import save_video_input_to_file
from ..upload import create_upload_url, upload_file_to_url

LOGGER = logging.getLogger(__name__)


class BeebleUploadVideoTestNode:
    CATEGORY = "Beeble/SwitchX/Test"
    FUNCTION = "run"
    OUTPUT_NODE = True
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("beeble_uri", "debug_json")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "video": ("VIDEO",),
                "filename_prefix": ("STRING", {"default": "beeble_video_upload"}),
            }
        }

    def run(self, video, filename_prefix):
        cleaned_prefix = filename_prefix.strip() or "beeble_video_upload"
        temp_path = Path(
            tempfile.NamedTemporaryFile(
                prefix=f"{cleaned_prefix}_",
                suffix=".mp4",
                delete=False,
            ).name
        )

        try:
            save_video_input_to_file(video, str(temp_path))
            upload_info = create_upload_url(temp_path.name)
            upload_file_to_url(str(temp_path), upload_info["upload_url"])

            debug_payload = {
                "file_path": str(temp_path),
                "upload_id": upload_info.get("upload_id"),
                "beeble_uri": upload_info["beeble_uri"],
            }
            debug_json = json.dumps(debug_payload, indent=2, ensure_ascii=False)
            LOGGER.info("Beeble video upload test:\n%s", debug_json)
            return (upload_info["beeble_uri"], debug_json)
        finally:
            temp_path.unlink(missing_ok=True)
