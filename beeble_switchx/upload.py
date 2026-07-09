"""Upload helpers for the Beeble API."""

from __future__ import annotations

import logging
import mimetypes
import time
from pathlib import Path
from typing import Any
from urllib import error, request

from .api import (
    BEEBLE_NETWORK_RETRY_COUNT,
    BEEBLE_NETWORK_RETRY_DELAY,
    api_request,
    format_network_error_message,
    should_retry_url_error,
)
from .errors import BeebleUploadError

LOGGER = logging.getLogger(__name__)


def create_upload_url(filename: str, api_key: str | None = None) -> dict[str, Any]:
    """Create a presigned upload URL for a local media file."""
    cleaned_filename = filename.strip()
    if not cleaned_filename:
        raise ValueError("filename is required")

    payload = api_request(
        "POST",
        "/v1/uploads",
        api_key=api_key,
        json={"filename": cleaned_filename},
    )

    upload_url = payload.get("upload_url")
    beeble_uri = payload.get("beeble_uri")
    upload_id = payload.get("upload_id", payload.get("id"))

    if not isinstance(upload_url, str) or not upload_url:
        raise BeebleUploadError("Beeble upload response is missing upload_url.")
    if not isinstance(beeble_uri, str) or not beeble_uri:
        raise BeebleUploadError("Beeble upload response is missing beeble_uri.")

    result = {
        "upload_url": upload_url,
        "beeble_uri": beeble_uri,
    }
    if isinstance(upload_id, str) and upload_id:
        result["upload_id"] = upload_id

    return result


def upload_file_to_url(file_path: str, upload_url: str) -> None:
    """Upload a local file to a presigned Beeble upload URL."""
    local_path = Path(file_path)
    if not local_path.is_file():
        raise BeebleUploadError(f"Local file does not exist: {file_path}")
    if not upload_url.strip():
        raise ValueError("upload_url is required")

    content_type, _ = mimetypes.guess_type(local_path.name)
    if not content_type:
        content_type = "application/octet-stream"

    data = local_path.read_bytes()
    req = request.Request(
        upload_url,
        data=data,
        headers={"Content-Type": content_type},
        method="PUT",
    )

    for attempt in range(BEEBLE_NETWORK_RETRY_COUNT + 1):
        try:
            with request.urlopen(req, timeout=60.0) as response:
                status_code = response.getcode()
            break
        except error.HTTPError as exc:
            raise BeebleUploadError(
                f"Beeble upload failed with status {exc.code}."
            ) from exc
        except error.URLError as exc:
            if attempt >= BEEBLE_NETWORK_RETRY_COUNT or not should_retry_url_error(exc):
                raise BeebleUploadError(format_network_error_message("Beeble upload", exc)) from exc
            LOGGER.warning(
                "Beeble upload failed with a temporary network error, retrying (%s/%s).",
                attempt + 1,
                BEEBLE_NETWORK_RETRY_COUNT,
            )
            time.sleep(BEEBLE_NETWORK_RETRY_DELAY)

    if not 200 <= status_code < 300:
        raise BeebleUploadError(f"Beeble upload failed with status {status_code}.")


def upload_file(file_path: str, api_key: str | None = None) -> str:
    """Create an upload URL, upload the file, and return the beeble URI."""
    local_path = Path(file_path)
    upload_info = create_upload_url(local_path.name, api_key=api_key)
    upload_file_to_url(str(local_path), upload_info["upload_url"])
    return upload_info["beeble_uri"]


__all__ = ["create_upload_url", "upload_file", "upload_file_to_url"]
