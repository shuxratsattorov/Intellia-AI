"""Application-level exceptions."""


class AppError(Exception):
    """Base exception for application errors."""

    def __init__(self, message: str, status_code: int = 500) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class NotFoundError(AppError):
    """Raised when a requested resource is not found."""

    def __init__(self, message: str) -> None:
        super().__init__(message, status_code=404)


class AuthError(AppError):
    """Base exception for authentication/authorization errors."""

    def __init__(self, message: str, status_code: int = 401) -> None:
        super().__init__(message, status_code)


class RegistrationError(AuthError):
    """Raised when user registration fails."""

    def __init__(self, message: str) -> None:
        super().__init__(message, status_code=400)


class AuthenticationError(AuthError):
    """Raised when authentication fails (invalid credentials)."""

    def __init__(self, message: str = "Invalid email or password") -> None:
        super().__init__(message, status_code=401)


class TokenError(AuthError):
    """Raised when token validation or refresh fails."""

    def __init__(self, message: str, status_code: int = 401) -> None:
        super().__init__(message, status_code)
