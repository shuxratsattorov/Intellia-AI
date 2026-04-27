import aiosmtplib
from dataclasses import dataclass
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from .sender import AbstractEmailSender
from .models import EmailMessage


@dataclass(frozen=True)
class EmailMessage:
    to: str
    subject: str
    html: str
    text: str


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
        mime["From"] = f"{self._config.from_name} <{self._config.from_address}>"
        mime["To"] = message.to

        mime.attach(MIMEText(message.text, "plain", "utf-8"))
        mime.attach(MIMEText(message.html, "html", "utf-8"))

        await aiosmtplib.send(
            mime,
            hostname=self._config.host,
            port=self._config.port,
            username=self._config.username,
            password=self._config.password,
            use_tls=self._config.use_tls,
        )
