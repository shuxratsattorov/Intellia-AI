import sys
import asyncio
from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.core.security import (
    Argon2Config, 
    PasswordHasher, 
    TokenConfig, 
    RSAKeyPair, 
    JWTManager
)
from app.core.config import settings
from app.db import factory, base as db
from app.db.session import AsyncSessionLocal
from app.api.router import routers_prefixs_tags
from app.modules.auth.seed_rbac import RBACManager


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.async_engine = create_async_engine(
        settings.DATABASE_URL_asyncpg,
        pool_pre_ping=True,
        pool_size=20,
        pool_timeout=30
    )

    factory.async_session_factory = async_sessionmaker[AsyncSession](
        db.async_engine,
        expire_on_commit=False,
        autoflush=True,
    )

    app.state.key_pair = RSAKeyPair.generate(key_size=2048)
    app.state.jwt = JWTManager(TokenConfig(
        key_pair=app.state.key_pair,
        algorithm="RS256",
        access_token_expire_minutes=15,
        refresh_token_expire_days=7,
        issuer="myapp",
        audience="myapp-users",
    ))
    app.state.hasher = PasswordHasher(Argon2Config())

    yield

    await db.async_engine.dispose()


app = FastAPI(
    debug=settings.DEBUG,
    description="""Intellia API""",
    version='1.0.0',
    lifespan=lifespan,
    docs_url='/docs',
    redoc_url='/reduc',
    swagger_ui_parameters={
        "docExpansion": "none",
        "defaultModelsExpandDepth": -1, 
        "displayRequestDuration": True,
        "tryItOutEnabled": True,
    },
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)


# @app.middleware('http')
# async def before_request(request: Request, call_next):
#     user = request.headers.get('X-Forwarded-For')
#     key = f'{user}:{datetime.datetime.now().minute}'
#     result = await RequestLimit(limit=1000, duration=30).is_over_limit(user=user, key=key)
#     if result:
#         return ORJSONResponse(
#             status_code=status.HTTP_429_TOO_MANY_REQUESTS,
#             content={'detail': 'Too many requests'}
#         )
#     return await call_next(request)


for router, prefix, tags in routers_prefixs_tags():
    app.include_router(
        router=router,
        prefix=prefix,
        tags=tags
    )


async def seed_rbac():
    async with AsyncSessionLocal() as session:
        async with session.begin():
            manager = RBACManager(session)
            result = await manager.seed_all()
            print(result)


if __name__ == "__main__":
    if "--rbac" in sys.argv:
        asyncio.run(seed_rbac())


@app.get("/health", tags=["infra"])
async def health():
    return {"status": "ok", "version": app.version}         