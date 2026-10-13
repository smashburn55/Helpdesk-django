# Blueprint code for: ticketApp/management/commands/parse_support_emails.py
import imaplib
import email
from email.header import decode_header
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from ticketApp.models import Ticket, ContactCRM


# Inside ticketApp/management/commands/parse_support_emails.py

class Command(BaseCommand):
    help = 'Polls support inbox via IMAP and ingests new emails as tickets with spam filters'

    def handle(self, *args, **options):
        # 1. Establish Secure Connection (Your verified settings)
        mail = imaplib.IMAP4_SSL("mail.mashburndatasystems.com")
        mail.login("support@mashburndatasystems.com", "Tinman55!")
        mail.select("inbox")

        # 2. Define Commercial Filtering Rules
        SUBJECT_BLACKLIST = [
            "undeliverable:", "delivery status notification", "auto-reply",
            "out of office", "newsletter", "spam", "marketing", "promotion",
            "verify your account", "password reset", "your invoice is ready"
        ]

        SENDER_BLACKLIST = [
            "mailer-daemon@", "noreply@", "no-reply@", "donotreply@",
            "alert@", "notifications@", "spammer@", "marketing@"
        ]

        status, response = mail.search(None, 'UNSEEN')

        for num in response[0].split():
            status, data = mail.fetch(num, '(RFC822)')
            raw_email = data[0][1]
            msg = email.message_from_bytes(raw_email)

            # 3. Extract Subject and Sender Names cleanly
            raw_subject = msg.get("Subject", "")
            # Decode subject if encoded by email client
            decoded_subject = decode_header(raw_subject)
            subject_str = ""
            for sub, encoding in decoded_subject:
                if isinstance(sub, bytes):
                    subject_str += sub.decode(encoding or 'utf-8', errors='ignore')
                else:
                    subject_str += str(sub)

            sender_raw = msg.get("From", "")
            sender_name, sender_email = email.utils.parseaddr(sender_raw)
            sender_email_lower = sender_email.lower().strip()
            subject_lower = subject_str.lower().strip()

            # 4. RUN CRITICAL FILTERING CHECKS BEFORE INGESTION

            # Check A: Is the sender address explicitly blocked?
            is_blocked_sender = any(blocked in sender_email_lower for blocked in SENDER_BLACKLIST)

            # Check B: Does the subject contain junk keywords or bounce-back flags?
            is_blocked_subject = any(keyword in subject_lower for keyword in SUBJECT_BLACKLIST)

            if is_blocked_sender or is_blocked_subject:
                self.stdout.write(self.style.WARNING(
                    f"SKIPPED JUNK MAIL: From: {sender_email_lower} | Subject: '{subject_str}'"
                ))
                # CRITICAL: We still flag it as SEEN (read) on the mail server
                # so the engine skips it on the next loop iteration and doesn't get stuck!
                continue

                # 5. Extract Email Body (Your existing layout processing)
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode(errors='ignore')
                        break
            else:
                body = msg.get_payload(decode=True).decode(errors='ignore')

            # 6. Database Match & Ingest Row (Proceeds safely with clean data)
            matching_contact = ContactCRM.objects.filter(email__iexact=sender_email_lower).first()

            if not matching_contact:
                parsed_name = sender_email_lower.split('@')[0]
                matching_contact = ContactCRM.objects.create(
                    first_name=parsed_name,
                    last_name="External Sender",
                    email=sender_email_lower
                )

            Ticket.objects.create(
                title=subject_str[:200],
                description=body,
                status='TODO',
                crm_contact=matching_contact,
                company=matching_contact.company if matching_contact.company else None
            )
            # Inside your parse_support_emails.py loop near the bottom:
            new_ticket = Ticket.objects.create(
                title=subject_str[:200],
                description=body,
                status='TODO',
                crm_contact=matching_contact,
                company=matching_contact.company if matching_contact.company else None
            )

            # Import the email function from views and trigger it dynamically
            from ticketApp.views import send_ticket_confirmation_email
            send_ticket_confirmation_email(new_ticket)

            self.stdout.write(self.style.SUCCESS(f"Successfully Ingested Clean Ticket: '{subject_str}'"))

            self.stdout.write(
                self.style.SUCCESS(f"Successfully Ingested Clean Ticket: '{subject_str}' from {sender_email_lower}"))
