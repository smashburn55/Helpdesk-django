from django.db import models
from django.contrib.auth.models import User

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

    def __str__(self):
        return self.title



class Comment(models.Model):
    # REMOVED the old tracking key and updated to match your live custom Postgres key
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        db_column='ticket_id',     # <-- CRITICAL: Forces it to link to your live table column name
        related_name='comments'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author.username} on ticket #{self.ticket_id}"



