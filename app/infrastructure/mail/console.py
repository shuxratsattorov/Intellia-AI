from .sender import AbstractEmailSender
from .models import EmailMessage


class ConsoleEmailSender(AbstractEmailSender):

    async def send(self, message: EmailMessage) -> None:
        border = "═" * 55
        print(f"\n{border}")
        print(f"📧 {message.to}")
        print(message.subject)
        print(border)
        print(message.text)
        print(border)