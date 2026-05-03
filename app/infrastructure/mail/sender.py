from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.core.config import settings
from app.infrastructure.mail.client import SMTPClient
from app.infrastructure.mail.error import SMTPErrorClassifier


class SMTPEmailSender:
 
    def __init__(self):
        self._client = SMTPClient()
 
    async def send(
        self, 
        to: str or list, 
        subject: str, 
        html_content: str, 
        text_content: str | None = None
        ) -> dict:

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{settings.SMTP_FROM} <{settings.SMTP_FROM}>"
        msg["To"] = to
 
        if text_content:
            msg.attach(MIMEText(text_content, "plain"))
        msg.attach(MIMEText(html_content, "html"))

        if text_content:
            msg.attach(MIMEText(text_content, "plain"))
        msg.attach(MIMEText(html_content, "html"))

        try:

            await self._client.send_message(msg)

            return {
                "status": "success",
                "message_id": msg.get("Message-ID"),
            }

        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "retryable": SMTPErrorClassifier.is_retryable(e),
                "permanent": SMTPErrorClassifier.is_permanent(e),
            }