from typing import Any


class AppException(Exception):
    pass
 

class NotFoundError(AppException):
    pass

 
class TokenNotFoundError(AppException):
    pass
 
class TokenExpiredError(AppException):
    pass


class InvalidIssuerError(AppException):
    pass

 
class InvalidTokenError(AppException):
    pass
 
class TokenRevokedError(AppException):
    pass


class InvalidID(AppException):
    pass


class UserAlreadyExists(AppException):
    pass


class UserNotExists(AppException):
    pass


class UserInactive(AppException):
    pass


class UserAlreadyVerified(AppException):
    pass


class InvalidVerifyToken(AppException):
    pass


class InvalidResetPasswordToken(AppException):
    pass


class DefaultRoleNotConfigured(AppException):
    pass


class TokenRevokedError(AppException):
    pass


class InvalidPasswordException(AppException):
    def __init__(self, reason: Any) -> None:
        self.reason = reason

