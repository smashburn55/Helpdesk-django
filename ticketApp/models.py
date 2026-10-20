from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django import forms

class TicketStatus(models.TextChoices):
    TO_DO = 'TODO', 'To Do'
    IN_PROGRESS = 'PROG', 'In Progress'
    IN_REVIEW = 'REV', 'In Review'
    DONE = 'DONE', 'Done'

# 1. Mapped legacy CRM Companies Table
class CompanyCRM(models.Model):
    company_id = models.BigAutoField(primary_key=True)
    company_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=50, blank=True, null=True)
    website = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False  # <-- Tells Django to completely leave this table structure alone
        db_table = 'companies'  # <-- Explicitly matches your exact Postgres table name

    def __str__(self):
        return self.company_name

# 2. Mapped legacy CRM Contacts Table
class ContactCRM(models.Model):
    contact_id = models.BigAutoField(primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    company = models.ForeignKey(
        CompanyCRM,
        on_delete=models.DO_NOTHING,
        db_column='company_id',
        blank=True,
        null=True
    )

    class Meta:
        managed = False
        db_table = 'contacts'

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


# Replace your old Ticket class in ticketApp/models.py with this:
class Ticket(models.Model):
    ticket_id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(
        max_length=10,
        choices=[('TODO', 'To Do'), ('PROG', 'In Progress'), ('REV', 'In Review'), ('DONE', 'Done')],
        default='TODO'
    )
    # Links to the logged-in technician
    assignee = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        db_column='assigned_tech_id',
        null=True,
        blank=True,
        related_name='tickets'
    )
    # Links directly to the CRM Company layout
    company = models.ForeignKey(
        CompanyCRM,
        on_delete=models.CASCADE,
        db_column='company_id',
        null=True,
        blank=True
    )
    # Links directly to the CRM Caller Contact layout
    crm_contact = models.ForeignKey(
        ContactCRM,
        on_delete=models.CASCADE,
        db_column='contact_id',
        null=True,
        blank=True,
        related_name='tickets'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False  # <-- Crucial: Django treats this as part of your core CRM now!
        db_table = 'support_tickets'


    PRIORITY_CHOICES = [
        ('LOW', 'Low / Routine'),
        ('MED', 'Medium'),
        ('HIGH', 'High Impact'),
        ('CRIT', 'Critical Outage'),
    ]
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='MED')

    @property
    def hours_since_creation(self):
        """Calculates raw float hours that have elapsed since creation."""
        if not self.created_at:
            return 0.0
        elapsed_time = timezone.now() - self.created_at
        return elapsed_time.total_seconds() / 3600.0

    @property
    def sla_status_data(self):
        """
        COMMERCIAL SLA TRIAGE MATRIX
        Dynamically calculates contract breaches based on issue priority.
        """
        if self.status == 'DONE':
            return {'label': 'Compliant', 'class': 'badge bg-success-subtle text-success border border-success'}

        elapsed = self.hours_since_creation

        # Assign response windows based on triage selection rules
        if self.priority == 'CRIT':
            warning_h, breach_h = 0.5, 1.0  # Critical: 1 hour breach window
        elif self.priority == 'HIGH':
            warning_h, breach_h = 2.0, 4.0  # High: 4 hour breach window
        elif self.priority == 'MED':
            warning_h, breach_h = 12.0, 24.0  # Medium: 24 hour breach window
        else:
            warning_h, breach_h = 24.0, 48.0  # Low: 48 hour breach window

        if self.assignee is None and elapsed > breach_h:
            return {'label': f'BREACHED (+{int(elapsed - breach_h)}h Overdue)',
                    'class': 'badge bg-danger text-white p-1'}

        if self.assignee is None and elapsed > warning_h:
            return {'label': 'SLA Warning', 'class': 'badge bg-warning text-dark border border-warning'}

        return {'label': 'Active / Safe', 'class': 'badge bg-light text-dark border border-secondary'}

    def __str__(self):
        return self.title


class Comment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, db_column='ticket_id', related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    # 🕵️‍♂️ NEW SECURITY TOGGLE: True if this is a private technician note, False if it is client-facing
    is_internal = models.BooleanField(default=False)

    def __str__(self):
        note_type = "INTERNAL ONLY" if self.is_internal else "CLIENT FACING"
        return f"Comment by {self.author.username} ({note_type}) on ticket #{self.ticket_id}"

class TechProfile(models.Model):
    """Extends the default Django User record with custom technician phone data."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='tech_profile')
    phone_number = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"Profile for @{self.user.username}"



