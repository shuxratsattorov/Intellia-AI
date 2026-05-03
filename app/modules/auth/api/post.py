from fastapi import Depends, status, Request, Response

from app.modules.auth.api.router import router
from app.shared.responses import responses  
from app.core.error.error_code import ErrorCode
from app.core.error.exception import (
    InvalidIssuerError, 
    InvalidTokenError, 
    TokenExpiredError, 
    TokenRevokedError, 
    DefaultRoleNotConfigured, 
    TokenNotFoundError,
    UserAlreadyExists,
)
from app.core.error.http_exceptions import (
    default_role_not_configured, 
    no_refresh_token, 
    register_user_already_exists, 
    token_not_foud
)

from app.modules.auth.service.auth import AuthService, JWTService
from app.modules.auth.deps import get_auth_service, get_jwt_service
from app.modules.auth.schemas.auth import (
    MessegeResponse, 
    RefreshRequest, 
    RefreshResponse, 
    RegisterRequest, 
    RegisterResponse, 
    RevokeRequest,
    SetPasswordRequest,
    VerifiyOtpRequest,
    VerifiyOtpResponse
)  


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
            email=data.email
        )
    except UserAlreadyExists:
        raise register_user_already_exists
    except DefaultRoleNotConfigured:
        raise default_role_not_configured

    return user


@router.post(
    "/verify-otp", 
    response_model=VerifiyOtpResponse, 
    status_code=status.HTTP_201_CREATED,
    name="verify_otp:verify_otp",
    responses=responses([
        ErrorCode.REGISTER_USER_ALREADY_EXISTS, 
        ErrorCode.DEFAULT_ROLE_NOT_CONFIGURED]
    )
)

async def verify_otp(
    data: VerifiyOtpRequest,
    service: AuthService = Depends(get_auth_service)
) -> RegisterResponse:
    try:
        user = await service.verify_otp(
            email=data.email,
            otp=data.otp
        )
    except INVALID_OTP:
        raise 
    except OTP_EXPIRED:
        raise 
    except USER_NOT_FOUND:
        raise    
    except ALREADY_VERIFIED:
        raise

    return user


@router.post(
    "/set-password", 
    response_model=JWTREsponse, 
    status_code=status.HTTP_201_CREATED,
    name="get_password:get_password",
    responses=responses([
        ErrorCode.REGISTER_USER_ALREADY_EXISTS, 
        ErrorCode.DEFAULT_ROLE_NOT_CONFIGURED]
    )
)

async def set_password(
    data: SetPasswordRequest,
    service: AuthService = Depends(get_auth_service)
) -> JWTREsponse:
    try:
        user = await service.set_password(
            email=data.email, 
            password=data.password
        )
    except UserAlreadyExists:
        raise register_user_already_exists
    except DefaultRoleNotConfigured:
        raise default_role_not_configured

    return user


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
        raise no_refresh_token

    try:
        await service.logout(
            refresh_token=refresh_token
        )

    except TokenNotFoundError:
        raise token_not_foud

    except TokenExpiredError:
        raise 

    except TokenRevokedError:
        raise 

    except InvalidIssuerError:
        raise 

    except InvalidTokenError:
        raise           

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
        token = await service.refresh_access_token(
            refresh_token=data.token
        )

    except TokenExpiredError:
        raise 

    except TokenRevokedError:
        raise 

    except InvalidIssuerError:
        raise 

    except InvalidTokenError:
        raise 

    return token   


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
        await service.revoke_token(
            refresh_token=data.token
        )

    except TokenExpiredError:
        raise 

    except TokenRevokedError:
        raise 

    except InvalidIssuerError:
        raise 

    except InvalidTokenError:
        raise   

    return MessegeResponse