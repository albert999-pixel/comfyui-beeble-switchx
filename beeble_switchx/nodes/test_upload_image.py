"""Test node for uploading an IMAGE to Beeble."""

from __future__ import annotations

import json
import logging
import tempfile
from pathlib import Path

from ..media import save_image_tensor_as_png
from ..upload import create_upload_url, upload_file_to_url

LOGGER = logging.getLogger(__name__)


class BeebleUploadImageTestNode:
    CATEGORY = "Beeble/SwitchX/Test"
    FUNCTION = "run"
    OUTPUT_NODE = True
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("beeble_uri", "debug_json")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "filename_prefix": ("STRING", {"default": "beeble_upload"}),
            }
        }

    def run(self, image, filename_prefix):
        cleaned_prefix = filename_prefix.strip() or "beeble_upload"
        temp_path = Path(
            tempfile.NamedTemporaryFile(
                prefix=f"{cleaned_prefix}_",
                suffix=".png",
                delete=False,
            ).name
        )

        try:
            save_image_tensor_as_png(image, str(temp_path))
            upload_info = create_upload_url(temp_path.name)
            upload_file_to_url(str(temp_path), upload_info["upload_url"])

            debug_payload = {
                "file_path": str(temp_path),
                "upload_id": upload_info.get("upload_id"),
                "beeble_uri": upload_info["beeble_uri"],
            }
            debug_json = json.dumps(debug_payload, indent=2, ensure_ascii=False)
            LOGGER.info("Beeble image upload test:\n%s", debug_json)
            return (upload_info["beeble_uri"], debug_json)
        finally:
            temp_path.unlink(missing_ok=True)
