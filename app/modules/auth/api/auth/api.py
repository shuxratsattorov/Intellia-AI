"""Auth API – request/response handling only."""

from fastapi import APIRouter, Depends, Request, HTTPException

from app.modules.auth.deps import get_auth_service
from app.modules.auth.service.auth import AuthService
from app.modules.auth.schemas.schemas import (
    RegisterRequest,
    RegisterResponse,
    LoginRequest,
    LoginResponse,
    RefreshRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    TokenPair,
    UserOut,
    MessageResponse,
)
from app.core.errors import (
    RegistrationError,
    AuthenticationError,
    TokenError,
)


router = APIRouter()


def _user_to_out(user) -> UserOut:
    """Map User model to UserOut DTO."""
    roles = [r.name for r in user.roles] if user.roles else []
    return UserOut(id=user.id, email=user.email, is_active=user.is_active, roles=roles)


@router.post("/register", response_model=RegisterResponse)
async def register(
    body: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> RegisterResponse:
    """Register a new user."""
    try:
        user, tokens = await auth_service.register(
            email=body.email,
            password=body.password,
        )
    except RegistrationError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


    return RegisterResponse(
        user=_user_to_out(user),
        tokens=tokens,
    )


# @router.post("/login", response_model=LoginResponse)
# async def login(
#     body: LoginRequest,
#     request: Request,
#     auth_service: AuthService = Depends(get_auth_service),
# ) -> LoginResponse:
#     """Authenticate user and return tokens."""
#     try:
#         tokens = await auth_service.login(
#             email=body.email,
#             password=body.password,
#             ip=request.client.host if request.client else "",
#             user_agent=request.headers.get("user-agent", ""),
#         )
#     except AuthenticationError as e:
#         raise HTTPException(status_code=e.status_code, detail=e.message)

#     return LoginResponse(tokens=tokens)


# @router.post("/refresh", response_model=TokenPair)
# async def refresh(
#     body: RefreshRequest,
#     auth_service: AuthService = Depends(get_auth_service),
# ) -> TokenPair:
#     """Refresh access token using refresh token."""
#     try:
#         tokens = await auth_service.refresh_tokens(refresh_token=body.refresh_token)
#     except TokenError as e:
#         raise HTTPException(status_code=e.status_code, detail=e.message)

#     return tokens


# @router.post("/logout", response_model=MessageResponse)
# async def logout(
#     body: RefreshRequest,
#     auth_service: AuthService = Depends(get_auth_service),
# ) -> MessageResponse:
#     """Revoke refresh token."""
#     await auth_service.logout(refresh_token=body.refresh_token)
#     return MessageResponse(message="Logged out successfully")


# @router.post("/forgot-password", response_model=MessageResponse)
# async def forgot_password(
#     body: ForgotPasswordRequest,
#     auth_service: AuthService = Depends(get_auth_service),
# ) -> MessageResponse:
#     """Request password reset (sends email if user exists)."""
#     await auth_service.forgot_password(email=body.email)
#     return MessageResponse(
#         message="If an account exists with this email, a reset link has been sent."
#     )


# @router.post("/reset-password", response_model=MessageResponse)
# async def reset_password(
#     body: ResetPasswordRequest,
#     auth_service: AuthService = Depends(get_auth_service),
# ) -> MessageResponse:
#     """Reset password using token from email."""
#     try:
#         await auth_service.reset_password(
#             token=body.token,
#             new_password=body.new_password,
#         )
#     except TokenError as e:
#         raise HTTPException(status_code=e.status_code, detail=e.message)

#     return MessageResponse(message="Password has been reset successfully")
