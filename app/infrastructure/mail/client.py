import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from string import Template
 
import aiosmtplib
 
logger = logging.getLogger(__name__)
 
 
@dataclass(frozen=True)
class EmailMessage:
    to: str
    subject: str
    html: str
    text: str
 
 
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
 
 
# ─── SMTP ─────────────────────────────────────────────────────────────────────
 
@dataclass(frozen=True)
class SMTPConfig:
    host: str
    port: int
    username: str
    password: str
    from_address: str
    from_name: str = "Auth Service"
    use_tls: bool = True
 
 
class SMTPEmailSender(AbstractEmailSender):
 
    def __init__(self, config: SMTPConfig):
        self._config = config
 
    async def send(self, message: EmailMessage) -> None:
        mime = MIMEMultipart("alternative")
        mime["Subject"] = message.subject
        mime["From"]    = f"{self._config.from_name} <{self._config.from_address}>"
        mime["To"]      = message.to
        mime.attach(MIMEText(message.text, "plain", "utf-8"))
        mime.attach(MIMEText(message.html, "html",  "utf-8"))
        try:
            await aiosmtplib.send(
                mime,
                hostname=self._config.host,
                port=self._config.port,
                username=self._config.username,
                password=self._config.password,
                use_tls=self._config.use_tls,
            )
            logger.info(f"Email yuborildi → {message.to}")
        except aiosmtplib.SMTPException as e:
            logger.error(f"SMTP xato: {e}")
            raise
 
 
# ─── Console (dev) ────────────────────────────────────────────────────────────
 
class ConsoleEmailSender(AbstractEmailSender):
 
    async def send(self, message: EmailMessage) -> None:
        border = "═" * 55
        print(f"\n{border}")
        print(f"  📧  {message.to}")
        print(f"  {message.subject}")
        print(border)
        print(message.text)
        print(f"{border}\n")