import aiosmtplib

from app.core.config import settings


class SMTPClient:
    def __init__(self):
        self.client: aiosmtplib.SMTP | None = None

    async def get_client(self) -> aiosmtplib.SMTP:
        if self.client and self.client.is_connected:
            return self.client

        self.client = aiosmtplib.SMTP(
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
        )

        await self.client.connect()

        await self.client.login(
            username=settings.SMTP_USER,
            password=settings.SMTP_PASS
        )

        return self.client

    async def close(self):
        if self.client and self.client.is_connected:
            await self.client.quit()