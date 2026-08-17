"""Application exceptions exposed through the stable API error envelope."""


class ApiException(Exception):
    """A deliberate, client-safe API failure."""

    def __init__(self, *, status_code: int, code: str, message: str) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message
