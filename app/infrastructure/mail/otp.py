import secrets
from app.core.config import settings


class OTPGenerator:
 
    @staticmethod
    def generate() -> str:

        return ''.join([str(secrets.randbelow(10)) for _ in range(settings.OTP_LENGTH)])