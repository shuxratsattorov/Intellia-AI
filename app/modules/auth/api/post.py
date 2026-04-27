from fastapi import Depends, HTTPException, status, Request, Response

from app.core.api_responses import responses
from app.modules.auth.api.v1.router import router
from app.modules.auth.service.auth import AuthService, JWTService
from app.modules.auth.deps import get_auth_service, get_jwt_service
from app.modules.auth.schemas.schemas import (
    MessegeResponse, RefreshRequest, RefreshResponse, RegisterRequest, RegisterResponse, 
    RevokeRequest)
from app.core.common import ErrorCode
from app.core.exception import (
    TokenNotFoundError, TokenRevokedError, UserAlreadyExists, DefaultRoleNotConfigured, 
    InvalidIssuerError, InvalidTokenError, TokenExpiredError)


@router.post(
    "/register", 
    response_model=RegisterResponse, 
    status_code=status.HTTP_201_CREATED,
    name="register:register",
    responses=responses([
        ErrorCode.REGISTER_USER_ALREADY_EXISTS, 
        ErrorCode.DEFAULT_ROLE_NOT_CONFIGURED]
    )
)

async def register(
    data: RegisterRequest,
    service: AuthService = Depends(get_auth_service)
) -> RegisterResponse:
    try:
        user = await service.register(
            email=data.email,
            password=data.password,
        )
    except UserAlreadyExists:
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.REGISTER_USER_ALREADY_EXISTS
        )
    except DefaultRoleNotConfigured:
        raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=ErrorCode.DEFAULT_ROLE_NOT_CONFIGURED
        )

    return RegisterResponse(email=user.email, is_verified=user.is_verified)


@router.post(
    "/logout",
    response_model=MessegeResponse, 
    status_code=status.HTTP_201_CREATED,
    name="logout:logout",
)

async def logut(
    request: Request,
    response: Response,
    service: AuthService = Depends(get_jwt_service)
) -> MessegeResponse:
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ErrorCode.NO_REFRESH_TOKEN)

    try:
        service.logout(refresh_token=refresh_token)

    except TokenNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ErrorCode.TOKEN_NOT_FOUND)    

    except TokenExpiredError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ErrorCode.ACCESS_TOKEN_ALREADY_EXPIRED)

    except TokenRevokedError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ErrorCode.TOKEN_REVOKED)

    except InvalidIssuerError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ErrorCode.TOKEN_INVALID_ISSUER)

    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ErrorCode.ACCESS_TOKEN_DECODE_ERROR)          

    response.delete_cookie(
        key="refresh_token",
        httponly=True,
        secure=True,
        samesite="strict",
        path="/auth/refresh"
    )

    return MessegeResponse


@router.post(
    "/refresh", 
    response_model=RegisterResponse, 
    status_code=status.HTTP_201_CREATED,
    name="refresh:refresh",
)   

async def refresh(
    data: RefreshRequest,
    service: JWTService = Depends(get_jwt_service)
) -> RefreshResponse:
    try:
        refresh_token = await service.refresh_access_token(refresh_token=data.token)

    except TokenExpiredError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ErrorCode.ACCESS_TOKEN_ALREADY_EXPIRED)

    except TokenRevokedError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ErrorCode.TOKEN_REVOKED)

    except InvalidIssuerError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ErrorCode.TOKEN_INVALID_ISSUER)

    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ErrorCode.ACCESS_TOKEN_DECODE_ERROR)

    return refresh_token   


@router.post(
    "/revoke", 
    response_model=MessegeResponse, 
    status_code=status.HTTP_201_CREATED,
    name="revoke:revoke",
) 

async def revoke(
    data: RevokeRequest,
    service: JWTService = Depends(get_jwt_service)
) -> MessegeResponse:
    try:
        service.revoke_token(refresh_token=data.token)

    except TokenExpiredError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ErrorCode.ACCESS_TOKEN_ALREADY_EXPIRED)

    except TokenRevokedError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ErrorCode.TOKEN_REVOKED)

    except InvalidIssuerError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ErrorCode.TOKEN_INVALID_ISSUER)

    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ErrorCode.ACCESS_TOKEN_DECODE_ERROR)    

    return MessegeResponse