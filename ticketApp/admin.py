from django.contrib import admin
from .models import Ticket, Comment, CompanyCRM, ContactCRM

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'assignee', 'created_at')
    list_filter = ('status', 'assignee')
    search_fields = ('title', 'description')

@admin.register(ContactCRM)
class ContactCRMAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email')
    search_fields = ('first_name', 'last_name', 'email')