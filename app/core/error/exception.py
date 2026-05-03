""" --- Excetions --- """


# BASE EXCEPTION

class AppException(Exception):
    pass

#  JWT 


class TokenExpiredError(AppException):
    pass

class TokenInvalidError(AppException):
    pass

class TokenRevokedError(AppException):
    pass

class TokenNotFoundError(AppException):
    pass

class InvalidIssuerError(AppException):
    pass

class ImmatureSignatureError(AppException):
    pass

class InvalidSignatureError(AppException):
    pass

class InvalidKeyError(AppException):
    pass

# USER

class UserNotFoundError(AppException):
    pass


class UserAlreadyExists(AppException):
    pass


class UserDisabledError(AppException):
    pass

# PERMISSION

class PermissionDeniedError(AppException):
    pass

# PASSWORD / RESET

class InvalidPasswordError(AppException):
    pass


class ResetPasswordBadTokenError(AppException):
    pass

# GENERAL

class InvalidRequestError(AppException):
    pass


class InternalServerError(AppException):
    pass


class DefaultRoleNotConfigured(AppException):
    pass

class InvalidTokenError(AppException):
    pass








# class AppException(Exception):
#     pass
 

class NotFoundError(AppException):
    pass

 
# class TokenNotFoundError(AppException):
#     pass
 
# class TokenExpiredError(AppException):
#     pass


# class InvalidIssuerError(AppException):
#     pass

 
# class InvalidTokenError(AppException):
#     pass
 
# class TokenRevokedError(AppException):
#     pass


# class InvalidID(AppException):
#     pass


# class UserAlreadyExists(AppException):
#     pass


# class UserNotExists(AppException):
#     pass


# class UserInactive(AppException):
#     pass


# class UserAlreadyVerified(AppException):
#     pass


# class InvalidVerifyToken(AppException):
#     pass


# class InvalidResetPasswordToken(AppException):
#     pass


class DefaultRoleNotConfigured(AppException):
    pass


# class TokenRevokedError(AppException):
#     pass


# class InvalidPasswordException(AppException):
#     pass