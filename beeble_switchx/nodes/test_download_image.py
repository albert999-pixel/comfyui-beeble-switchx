"""Test node for downloading a Beeble image result."""

from __future__ import annotations

import json
import logging
import tempfile
from pathlib import Path

from ..media import download_file, load_image_file_as_tensor

LOGGER = logging.getLogger(__name__)


class BeebleDownloadImageTestNode:
    CATEGORY = "Beeble/SwitchX/Test"
    FUNCTION = "run"
    OUTPUT_NODE = True
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("image", "debug_json")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "render_url": ("STRING", {"default": ""}),
            }
        }

    def run(self, render_url):
        temp_path = Path(
            tempfile.NamedTemporaryFile(
                prefix="beeble_download_image_",
                suffix=".png",
                delete=False,
            ).name
        )

        try:
            download_file(render_url, str(temp_path))
            image = load_image_file_as_tensor(str(temp_path))
            debug_payload = {
                "render_url": render_url,
                "file_path": str(temp_path),
            }
            debug_json = json.dumps(debug_payload, indent=2, ensure_ascii=False)
            LOGGER.info("Beeble image download test:\n%s", debug_json)
            return (image, debug_json)
        finally:
            temp_path.unlink(missing_ok=True)
