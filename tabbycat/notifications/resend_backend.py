import resend
from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend


class ResendEmailBackend(BaseEmailBackend):
    def open(self):
        resend.api_key = settings.RESEND_API_KEY
        return True

    def close(self):
        pass

    def send_messages(self, email_messages):
        num_sent = 0
        resend.api_key = settings.RESEND_API_KEY
        for message in email_messages:
            try:
                params = {
                    "from": message.from_email,
                    "to": message.to,
                    "subject": message.subject,
                    "html": message.body,
                }
                resend.Emails.send(params)
                num_sent += 1
            except Exception as e:
                if not self.fail_silently:
                    raise e
        return num_sent