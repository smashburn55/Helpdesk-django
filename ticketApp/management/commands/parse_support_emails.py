# Blueprint code for: ticketApp/management/commands/parse_support_emails.py
import imaplib
import email
from email.header import decode_header
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from ticketApp.models import Ticket, ContactCRM


class Command(BaseCommand):
    help = 'Polls support inbox via IMAP and ingests new emails as tickets'

    def handle(self, *args, **options):
        # 1. Establish Secure Protocol Connection to Mail Server
        mail = imaplib.IMAP4_SSL("://gmail.com")
        mail.login("support@yourproductcompany.com", "your-secure-app-password")
        mail.select("inbox")

        # 2. Query for Unread Messages
        status, response = mail.search(None, 'UNSEEN')

        for num in response[0].split():
            status, data = mail.fetch(num, '(RFC822)')
            raw_email = data[0][1]
            msg = email.message_from_bytes(raw_email)

            # 3. Extract Meta Details
            subject = decode_header(msg["Subject"])[0][0]
            sender = email.utils.parseaddr(msg["From"])[1]  # E.g., "john@acme.com"
            body = ""

            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode()
            else:
                body = msg.get_payload(decode=True).decode()

            # 4. Query PostgreSQL CRM Contacts Table for Sender Matching
            matching_contact = ContactCRM.objects.filter(email__iexact=sender).first()

            if not matching_contact:
                # Fallback: Create a temporary unverified contact row if missing
                matching_contact = ContactCRM.objects.create(
                    first_name=sender.split('@')[0],
                    last_name="External Sender",
                    email=sender
                )

            # 5. Write Ticket Directly into Live Production Grid Row
            Ticket.objects.create(
                title=str(subject),
                description=body,
                status='TODO',
                crm_contact=matching_contact,
                company=matching_contact.company if matching_contact.company else None
            )

            self.stdout.write(self.style.SUCCESS(f"Successfully ingested Ticket from {sender}"))
