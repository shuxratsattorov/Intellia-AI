"""Router registration – collects all API routers with prefix and tags."""

from app.modules.auth.api.auth.api import router as auth_router


def routers_prefixs_tags():
    """Yield (router, prefix, tags) for each API module."""
    yield auth_router, "/api/v1/auth", ["Auth"]
