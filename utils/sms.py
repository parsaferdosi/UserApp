# SMS helper using abstract base class so any provider can be swapped in.

from abc import ABC, abstractmethod

from django.conf import settings


class BaseSMSProvider(ABC):
    """
    Abstract base class for SMS providers.
    Implement this for each SMS provider (sms.ir, Kavenegar, etc.)
    """

    @abstractmethod
    def send_sms(self, number, message):
        pass

    @abstractmethod
    def get_credit(self):
        pass

    @abstractmethod
    def delete_scheduled(self, pack_id):
        pass

    @abstractmethod
    def report_today(self, page_size, page_number):
        pass


class SmsIrProvider(BaseSMSProvider):
    """SMS.ir implementation."""

    def __init__(self):
        from sms_ir import SmsIr

        self._client = SmsIr(
            settings.SMS_API_KEY,
            settings.SMS_LINE_NUMBER,
        )

    def send_sms(self, number, message):
        return self._client.send_sms(number, message)

    def get_credit(self):
        return self._client.get_credit()

    def delete_scheduled(self, pack_id):
        return self._client.delete_scheduled(pack_id)

    def report_today(self, page_size, page_number):
        return self._client.report_today(page_size, page_number)


class ConsoleSMSProvider(BaseSMSProvider):
    """Dev/test provider that prints to console instead of sending."""

    def send_sms(self, number, message):
        print(f"[SMS → {number}]: {message}")

    def get_credit(self):
        return {"credit": "unlimited (console)"}

    def delete_scheduled(self, pack_id):
        print(f"[SMS] Deleted scheduled pack: {pack_id}")

    def report_today(self, page_size, page_number):
        return []


def get_sms_provider():
    """
    Factory function: returns the SMS provider based on settings.

    Settings:
        SMS_PROVIDER (str): "sms_ir" or "console" (default: "console")
        SMS_API_KEY (str): API key (required for sms_ir)
        SMS_LINE_NUMBER (str): Line number (required for sms_ir)
    """
    provider = getattr(settings, "SMS_PROVIDER", "console")

    providers = {
        "sms_ir": SmsIrProvider,
        "console": ConsoleSMSProvider,
    }

    if provider not in providers:
        raise ValueError(
            f"Unknown SMS_PROVIDER '{provider}'. "
            f"Available: {list(providers.keys())}"
        )

    return providers[provider]()
