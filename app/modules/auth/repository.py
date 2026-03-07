from sqlalchemy import select

from app.modules.users.models import User
from src.db.repositories import AsyncRepository


class RegisterRepository(AsyncRepository):
    table = User

    async def existing_user(self, email: str) -> bool:
        await self.session.scalar(select(User).where(User.email == email))
        return

    async def create_user(self, email: str, password: str) -> User:
        user = User(
            email=email,
            password=password,
            is_active=True,
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def default_role_assign(self, role: str):
        smpt = 



def get_auth_repo() -> AuthTableRepository:
    return AuthTableRepository()
