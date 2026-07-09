"""Polling helpers for SwitchX jobs."""

from __future__ import annotations

import logging
import time
from typing import Any

from .api import api_request
from .errors import BeeblePollingError, BeebleTimeoutError

TERMINAL_JOB_STATUSES = {"completed", "failed", "cancelled"}
LOGGER = logging.getLogger(__name__)


def get_job_status(job_id: str, api_key: str | None = None) -> dict[str, Any]:
    """Fetch the current status for a Beeble SwitchX job."""
    cleaned_job_id = job_id.strip()
    if not cleaned_job_id:
        raise ValueError("job_id is required")

    return api_request(
        "GET",
        f"/v1/switchx/generations/{cleaned_job_id}",
        api_key=api_key,
    )


def wait_for_job(
    job_id: str,
    poll_interval: float = 2.0,
    timeout: float = 600.0,
    api_key: str | None = None,
) -> dict[str, Any]:
    """Poll a Beeble job until it reaches a terminal state or times out."""
    if poll_interval <= 0:
        raise ValueError("poll_interval must be > 0")
    if timeout <= 0:
        raise ValueError("timeout must be > 0")

    start_time = time.monotonic()
    attempt = 0

    LOGGER.info(
        "Waiting for Beeble job %s (poll_interval=%.1fs, timeout=%.1fs)",
        job_id,
        poll_interval,
        timeout,
    )

    while True:
        attempt += 1
        payload = get_job_status(job_id, api_key=api_key)
        status = payload.get("status")
        progress = payload.get("progress", 0) or 0

        if not isinstance(status, str) or not status:
            raise BeeblePollingError("Beeble job status response is missing status.")

        LOGGER.info(
            "Beeble job %s poll #%d: status=%s progress=%s",
            job_id,
            attempt,
            status,
            progress,
        )

        if status == "completed":
            LOGGER.info("Beeble job %s finished successfully.", job_id)
            return payload
        if status == "failed":
            raise BeeblePollingError(f"Beeble generation failed: {payload.get('error')}")
        if status == "cancelled":
            raise BeeblePollingError("Beeble generation was cancelled.")

        if time.monotonic() - start_time >= timeout:
            LOGGER.error("Timed out waiting for Beeble job %s.", job_id)
            raise BeebleTimeoutError(
                f"Timed out waiting for Beeble job {job_id} to finish."
            )

        time.sleep(poll_interval)


__all__ = [
    "TERMINAL_JOB_STATUSES",
    "get_job_status",
    "wait_for_job",
]
