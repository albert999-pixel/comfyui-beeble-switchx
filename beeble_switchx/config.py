"""Configuration helpers for Beeble SwitchX."""

import os
from pathlib import Path

from .errors import BeebleAuthError

BEEBLE_API_KEY_ENV = "BEEBLE_API_KEY"
DOTENV_PATH = Path(__file__).resolve().parent.parent / ".env"


def _read_api_key_from_dotenv(dotenv_path: Path = DOTENV_PATH) -> str | None:
    if not dotenv_path.is_file():
        return None

    for raw_line in dotenv_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        if key.strip() != BEEBLE_API_KEY_ENV:
            continue
        value = value.strip().strip("'").strip('"')
        if value:
            return value

    return None


def resolve_api_key(api_key: str | None = None) -> str:
    """Return the explicit API key or load it from .env/environment."""
    if api_key is not None:
        api_key = api_key.strip()
        if api_key:
            return api_key

    dotenv_api_key = _read_api_key_from_dotenv()
    if dotenv_api_key:
        return dotenv_api_key

    env_api_key = os.environ.get(BEEBLE_API_KEY_ENV, "").strip()
    if env_api_key:
        return env_api_key

    raise BeebleAuthError(
        f"Beeble API key is not set. Add {BEEBLE_API_KEY_ENV} to .env or the environment."
    )


__all__ = ["BEEBLE_API_KEY_ENV", "DOTENV_PATH", "resolve_api_key"]
