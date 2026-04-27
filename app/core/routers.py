from app.modules.auth.api.v1.router import router as auth_router

api_v1 = '/api/v1'


def routers_prefixs_tags():
    return (
        (auth_router, f'{api_v1}', ['auth']),
)