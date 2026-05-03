from app.api.v1 import api_v1
from app.modules.auth.api.router import router as auth_router


def routers_prefixs_tags():
    return (
        (auth_router, f'{api_v1}', ['auth']),
)