"""WAQI API exceptions"""


class APIError(Exception):
    """Base class for exceptions from the WAQI API."""


class ConnectionFailed(APIError):
    """Raised when connecting to the API fails."""


class InvalidToken(APIError):
    """Raised when the provided API token is invalid."""


class OverQuota(APIError):
    """Raised when the API token used reached its quota."""


class TimeoutError(APIError):
    """Raised when connecting to the API times out."""


class UnknownCity(APIError):
    """Raised when the provided city could not be found."""


class UnknownID(APIError):
    """Raised when the provided ID could not be found."""
