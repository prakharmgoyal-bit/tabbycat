import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend


class BrevoEmailBackend(BaseEmailBackend):
    def open(self):
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = settings.BREVO_API_KEY
        self.api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
            sib_api_v3_sdk.ApiClient(configuration)
        )
        return True

    def close(self):
        pass

    def send_messages(self, email_messages):
        num_sent = 0
        self.open()
        for message in email_messages:
            try:
                to=[]
                for recipient in message.to:
                    if recipient and "@" in recipient:
                        to.append({"email": recipient.strip()})
                    else:
                        print("INVALID EMAIL SKIPPED:", recipient)
                send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                    to=to,
                    sender={"email": message.from_email.split('<')[-1].replace('>', '').strip()},
                    subject=message.subject,
                    html_content=message.body,
                )
                self.api_instance.send_transac_email(send_smtp_email)
                num_sent += 1
            except ApiException as e:
                print("BREVO ERROR:", e)
                raise e
        return num_sent