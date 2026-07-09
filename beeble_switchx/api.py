"""HTTP helpers for the Beeble API."""

from __future__ import annotations

import json
import logging
import time
from typing import Any
from urllib import error, request

from .config import resolve_api_key
from .errors import BeebleAuthError, BeebleError

BEEBLE_API_BASE_URL = "https://api.beeble.ai"
BEEBLE_API_TIMEOUT = 30.0
BEEBLE_NETWORK_RETRY_COUNT = 2
BEEBLE_NETWORK_RETRY_DELAY = 1.0

LOGGER = logging.getLogger(__name__)


def build_api_url(path: str) -> str:
    """Build a Beeble API URL from a relative path."""
    return f"{BEEBLE_API_BASE_URL}/{path.lstrip('/')}"


def build_api_headers(api_key: str | None = None) -> dict[str, str]:
    """Build headers for authenticated Beeble API requests."""
    return {
        "x-api-key": resolve_api_key(api_key),
        "Content-Type": "application/json",
    }


def parse_api_error(status_code: int, payload: Any) -> str:
    """Return a readable API error message from a Beeble response."""
    if isinstance(payload, bytes):
        try:
            payload = json.loads(payload.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            payload = None

    try:
        if isinstance(payload, dict):
            error_payload = payload.get("error")
            if isinstance(error_payload, dict):
                code = error_payload.get("code")
                message = error_payload.get("message")
                if code and message:
                    return f"Beeble API error {status_code}: {message} ({code})"
                if message:
                    return f"Beeble API error {status_code}: {message}"
    except AttributeError:
        pass

    return f"Beeble API error {status_code}"


def raise_for_api_error(status_code: int, payload: Any) -> None:
    """Raise a project error if the response status indicates failure."""
    if 200 <= status_code < 300:
        return

    message = parse_api_error(status_code, payload)
    if status_code == 401:
        raise BeebleAuthError(message)
    raise BeebleError(message)


def should_retry_url_error(exc: error.URLError) -> bool:
    """Return True for transient URL errors worth retrying."""
    return not isinstance(exc.reason, str)


def format_network_error_message(action: str, exc: error.URLError) -> str:
    """Build a short user-facing message for network and SSL failures."""
    detail = str(exc.reason or exc)
    if "SSL:" in detail:
        return (
            f"{action} failed because the secure connection to Beeble was interrupted. "
            f"This is usually a temporary network or SSL issue. Details: {detail}"
        )
    return (
        f"{action} failed because of a temporary network error while talking to Beeble. "
        f"Details: {detail}"
    )


def api_request(
    method: str,
    path: str,
    *,
    api_key: str | None = None,
    timeout: float = BEEBLE_API_TIMEOUT,
    **kwargs: Any,
) -> dict[str, Any]:
    """Perform an authenticated JSON request to the Beeble API."""
    headers = build_api_headers(api_key)
    extra_headers = kwargs.pop("headers", None)
    if extra_headers:
        headers.update(extra_headers)

    json_payload = kwargs.pop("json", None)
    data = kwargs.pop("data", None)
    if json_payload is not None:
        data = json.dumps(json_payload).encode("utf-8")
    elif isinstance(data, str):
        data = data.encode("utf-8")

    req = request.Request(
        url=build_api_url(path),
        data=data,
        headers=headers,
        method=method.upper(),
    )

    for attempt in range(BEEBLE_NETWORK_RETRY_COUNT + 1):
        try:
            with request.urlopen(req, timeout=timeout) as response:
                raw_payload = response.read()
                status_code = response.getcode()
            break
        except error.HTTPError as exc:
            raw_payload = exc.read()
            raise_for_api_error(exc.code, raw_payload)
            raise AssertionError("unreachable")
        except error.URLError as exc:
            if attempt >= BEEBLE_NETWORK_RETRY_COUNT or not should_retry_url_error(exc):
                raise BeebleError(format_network_error_message("Beeble API request", exc)) from exc
            LOGGER.warning(
                "Beeble API request failed with a temporary network error, retrying (%s/%s).",
                attempt + 1,
                BEEBLE_NETWORK_RETRY_COUNT,
            )
            time.sleep(BEEBLE_NETWORK_RETRY_DELAY)

    try:
        payload = json.loads(raw_payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise BeebleError("Beeble API returned a non-JSON response.") from exc

    raise_for_api_error(status_code, payload)

    if not isinstance(payload, dict):
        raise BeebleError("Beeble API returned an unexpected response shape.")

    return payload


def get_account_info(api_key: str | None = None) -> dict[str, Any]:
    """Fetch Beeble account metadata and current rate limit usage."""
    return api_request("GET", "/v1/account/info", api_key=api_key)


def sanitize_account_info(payload: dict[str, Any]) -> dict[str, Any]:
    """Keep only a short, readable subset of the account response."""
    sanitized: dict[str, Any] = {}
    for key in ("id", "email", "name", "plan", "tier", "status"):
        if key in payload:
            sanitized[key] = payload[key]

    for key in ("rate_limits", "rate_limit", "usage", "billing"):
        value = payload.get(key)
        if isinstance(value, (dict, list)):
            sanitized[key] = value

    if not sanitized:
        sanitized["keys"] = sorted(payload.keys())

    return sanitized


__all__ = [
    "BEEBLE_API_BASE_URL",
    "BEEBLE_API_TIMEOUT",
    "api_request",
    "build_api_headers",
    "build_api_url",
    "format_network_error_message",
    "get_account_info",
    "sanitize_account_info",
    "parse_api_error",
    "raise_for_api_error",
    "should_retry_url_error",
]
