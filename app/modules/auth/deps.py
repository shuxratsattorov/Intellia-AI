from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import create_async_session
from app.modules.auth.service.auth import AuthService, JWTService


async def get_auth_service(
    session: AsyncSession = Depends(create_async_session)
    ) -> AuthService:
    return AuthService(session)


async def get_jwt_service(
    session: AsyncSession = Depends(create_async_session)
    ) -> JWTService:
    return JWTService(session)
