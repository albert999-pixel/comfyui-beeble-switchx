"""Project-specific errors for Beeble SwitchX."""


class BeebleError(Exception):
    """Base error for Beeble SwitchX integration."""


class BeebleAuthError(BeebleError):
    """Raised when Beeble API authentication fails."""


class BeebleUploadError(BeebleError):
    """Raised when an upload request or file upload fails."""


class BeebleGenerationError(BeebleError):
    """Raised when a generation request fails."""


class BeeblePollingError(BeebleError):
    """Raised when job polling fails."""


class BeebleTimeoutError(BeebleError):
    """Raised when waiting for a job exceeds the allowed timeout."""


class BeebleMediaError(BeebleError):
    """Raised when media conversion or download fails."""


__all__ = [
    "BeebleError",
    "BeebleAuthError",
    "BeebleUploadError",
    "BeebleGenerationError",
    "BeeblePollingError",
    "BeebleTimeoutError",
    "BeebleMediaError",
]
