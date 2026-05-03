from fastapi import HTTPException, status

from app.core.error.error_code import ErrorCode


access_token_alredy_expired = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail=ErrorCode.ACCESS_TOKEN_ALREADY_EXPIRED
)

token_revoked = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail=ErrorCode.TOKEN_REVOKED
)

token_invalid_issuer = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail=ErrorCode.TOKEN_INVALID_ISSUER
)

access_token_decode_error = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail=ErrorCode.ACCESS_TOKEN_DECODE_ERROR
)

register_user_already_exists = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail=ErrorCode.REGISTER_USER_ALREADY_EXISTS
)

default_role_not_configured = HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    detail=ErrorCode.DEFAULT_ROLE_NOT_CONFIGURED
)

token_not_foud = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail=ErrorCode.TOKEN_NOT_FOUND
)    

no_refresh_token = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail=ErrorCode.NO_REFRESH_TOKEN
)