from abc import ABC, abstractmethod
from .models import EmailMessage
from .templates import OTP_HTML, OTP_TEXT


class AbstractEmailSender(ABC):
 
    @abstractmethod
    async def send(self, message: EmailMessage) -> None: ...
 
    # ── Factory metodlar ─────────────────────────────────────────────────────
 
    async def send_verification_otp(
        self, to: str, username: str, otp: str,
        app_name: str, expires_minutes: int = 10,
    ) -> None:
        subs = dict(
            title="Email manzilingizni tasdiqlang",
            username=username,
            otp_code=otp,
            intro_text="Ro'yxatdan o'tganingiz uchun rahmat! "
                       "Quyidagi kodni ilovaga kiriting:",
            expires_text=f"{expires_minutes} daqiqa",
            note="Agar siz ro'yxatdan o'tmagan bo'lsangiz, "
                 "bu xatni e'tiborsiz qoldiring.",
            app_name=app_name,
        )
        await self.send(EmailMessage(
            to=to,
            subject=f"[{app_name}] Tasdiqlash kodi: {otp}",
            html=_OTP_HTML.substitute(subs),
            text=_OTP_TEXT.substitute(subs),
        ))
 
    async def send_email_change_otp(
        self, to: str, username: str, new_email: str, otp: str,
        app_name: str, expires_minutes: int = 10,
    ) -> None:
        subs = dict(
            title="Yangi email manzilingizni tasdiqlang",
            username=username,
            otp_code=otp,
            intro_text=f"<strong>{new_email}</strong> manziliga o'zgartirish uchun "
                       "quyidagi kodni kiriting:",
            expires_text=f"{expires_minutes} daqiqa",
            note="Agar siz so'rov yubormagan bo'lsangiz, "
                 "parolingizni darhol o'zgartiring.",
            app_name=app_name,
        )
        await self.send(EmailMessage(
            to=to,
            subject=f"[{app_name}] Email o'zgartirish kodi: {otp}",
            html=_OTP_HTML.substitute(subs),
            text=_OTP_TEXT.substitute(subs),
        ))
 
    async def send_password_reset_otp(
        self, to: str, username: str, otp: str,
        app_name: str, expires_minutes: int = 10,
    ) -> None:
        subs = dict(
            title="Parolni tiklash",
            username=username,
            otp_code=otp,
            intro_text="Parolni tiklash uchun quyidagi kodni kiriting:",
            expires_text=f"{expires_minutes} daqiqa",
            note="Agar siz so'rov yubormagan bo'lsangiz, "
                 "bu xatni e'tiborsiz qoldiring.",
            app_name=app_name,
        )
        await self.send(EmailMessage(
            to=to,
            subject=f"[{app_name}] Parol tiklash kodi: {otp}",
            html=_OTP_HTML.substitute(subs),
            text=_OTP_TEXT.substitute(subs),
        ))