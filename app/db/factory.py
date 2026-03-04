from sqlalchemy.ext.asyncio import async_sessionmaker

async_session_factory: async_sessionmaker | None = None

def get_async_factory() -> async_sessionmaker:
    return async_session_factory
