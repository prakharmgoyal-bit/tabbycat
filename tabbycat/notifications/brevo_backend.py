import re
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend


def parse_email_address(address):
    """Extract email (and optionally name) from formats like:
       'user@example.com' or 'Name <user@example.com>'
    """
    address = address.strip()
    match = re.match(r'^(.*?)\s*<([^>]+)>\s*$', address)
    if match:
        name = match.group(1).strip().strip('"')
        email = match.group(2).strip()
        return {"email": email, "name": name} if name else {"email": email}
    elif "@" in address:
        return {"email": address}
    return None


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
                to = []
                for recipient in message.to:
                    parsed = parse_email_address(recipient)
                    if parsed:
                        to.append(parsed)
                    else:
                        print("INVALID EMAIL SKIPPED:", recipient)

                if not to:
                    print("No valid recipients, skipping message.")
                    continue

                sender = parse_email_address(message.from_email)
                if not sender:
                    print("INVALID SENDER EMAIL SKIPPED:", message.from_email)
                    continue

                send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                    to=to,
                    sender=sender,
                    subject=message.subject,
                    html_content=message.body,
                    html_content=next(
                        (content for content, mimetype in getattr(message, 'alternatives', [])
                        if mimetype == 'text/html'),
                        None
                    ),
                )
                self.api_instance.send_transac_email(send_smtp_email)
                num_sent += 1
            except ApiException as e:
                print("BREVO ERROR:", e)
                raise e
        return num_sent