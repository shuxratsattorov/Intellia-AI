import datetime
from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.core.config import settings
from app.db import factory, base as db


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.async_engine = create_async_engine(
        settings.DATABASE_URL_asyncpg,
        pool_pre_ping=True,
        pool_size=20,
        pool_timeout=30
    )

    factory.async_session_factory = async_sessionmaker(
        db.async_engine,
        expire_on_commit=False,
        autoflush=True,
    )

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


@app.get('/now/datetime',)
async def datatime():
    return datetime.datetime.now(tz=settings.current_time)


for router, prefix, tags in routers_prefixs_tags():
    app.include_router(
        router=router,
        prefix=prefix,
        tags=tags
    )
