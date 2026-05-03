import aiosmtplib


class SMTPErrorClassifier:

    RETRYABLE_EXCEPTIONS = (
        aiosmtplib.SMTPServerDisconnected,
        aiosmtplib.SMTPConnectError,
        aiosmtplib.SMTPConnectTimeoutError,
        aiosmtplib.SMTPReadTimeoutError,
        aiosmtplib.SMTPResponseException,
    )

    NON_RETRYABLE_EXCEPTIONS = (
        aiosmtplib.SMTPAuthenticationError,
        aiosmtplib.SMTPSenderRefused,
        aiosmtplib.SMTPRecipientsRefused,
        aiosmtplib.SMTPRecipientRefused,
        aiosmtplib.SMTPDataError,
        aiosmtplib.SMTPNotSupported,
    )

    @staticmethod
    def is_retryable(exc: Exception) -> bool:
        if isinstance(exc, SMTPErrorClassifier.RETRYABLE_EXCEPTIONS):
            return True

        if isinstance(exc, aiosmtplib.SMTPResponseException):
            # 4xx = retry, 5xx = no retry
            return 400 <= getattr(exc, "smtp_code", 500) < 500

        return False

    @staticmethod
    def is_permanent(exc: Exception) -> bool:
        return isinstance(exc, SMTPErrorClassifier.NON_RETRYABLE_EXCEPTIONS)