"""Runtime file helpers for Beeble SwitchX."""

from __future__ import annotations

import logging
import tempfile
from pathlib import Path


LOGGER = logging.getLogger(__name__)
RUNTIME_DIR = Path(__file__).resolve().parent.parent / "runtime"
_RUNTIME_READY = False


def initialize_runtime_dir() -> Path:
    """Create a clean runtime directory for the current ComfyUI session."""
    global _RUNTIME_READY

    if _RUNTIME_READY:
        return RUNTIME_DIR

    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    for path in RUNTIME_DIR.iterdir():
        if not path.is_file():
            continue
        try:
            path.unlink()
        except OSError as exc:
            LOGGER.warning("Beeble runtime: failed to remove %s: %s", path.name, exc)

    _RUNTIME_READY = True
    LOGGER.info("Beeble runtime: ready at %s", RUNTIME_DIR)
    return RUNTIME_DIR


def create_runtime_path(prefix: str, suffix: str) -> Path:
    """Reserve a unique file path inside the runtime directory."""
    runtime_dir = initialize_runtime_dir()
    return Path(
        tempfile.NamedTemporaryFile(
            dir=runtime_dir,
            prefix=prefix,
            suffix=suffix,
            delete=False,
        ).name
    )


__all__ = ["create_runtime_path", "initialize_runtime_dir"]
