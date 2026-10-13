from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Ticket, TicketStatus, Comment, ContactCRM
from .forms import TicketForm, CommentForm, StatusUpdateForm, QuickContactForm


def index(request):
    tickets = Ticket.objects.all().order_by('-created_at')

    # Extract filter tokens from the URL string parameters
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    sla_filter = request.GET.get('sla', '')

    # Dynamically filter database rows based on match keys
    if search_query:
        tickets = tickets.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    if status_filter:
        tickets = tickets.filter(status=status_filter)
    if sla_filter:
        pass

    context = {
        'tickets': tickets,
        'search_query': search_query,
        'status_filter': status_filter,
        'sla_filter': sla_filter,
    }
    return render(request, 'ticketApp/index.html', context)


@login_required
@login_required
def create_ticket(request):
    preselected_contact_id = request.GET.get('contact_id', '')

    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.status = 'TODO'

            # AUTOMATIC PARENT LOOKUP:
            if ticket.crm_contact:
                # If a contact is selected, automatically pull their parent company ID
                ticket.company = ticket.crm_contact.company

            ticket.save()
            messages.success(request, 'Support ticket written directly to CRM database!')
            return redirect('index')
    else:
        initial_data = {}
        if preselected_contact_id:
            initial_data['crm_contact'] = preselected_contact_id
        form = TicketForm(initial=initial_data)

    return render(request, 'ticketApp/create_ticket.html', {'form': form})


#from .forms import TicketForm, CommentForm, StatusUpdateForm

def ticket_by_id(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    comments = ticket.comments.all().order_by('created_at')

    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, "Authentication required.")
            return redirect('ticket_by_id', pk=pk)

        # Check which form was submitted using a hidden HTML input name
        if 'update_status' in request.POST:
            status_form = StatusUpdateForm(request.POST, instance=ticket)
            if status_form.is_valid():
                status_form.save()
                messages.success(request, "Ticket updated successfully!")
                return redirect('ticket_by_id', pk=pk)
        elif 'add_comment' in request.POST:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.ticket = ticket
                comment.author = request.user
                comment.save()
                messages.success(request, "Comment added!")
                return redirect('ticket_by_id', pk=pk)

    # Provide blank/prefilled forms on GET request
    status_form = StatusUpdateForm(instance=ticket)
    comment_form = CommentForm()

    context = {
        'ticket': ticket,
        'comments': comments,
        'status_form': status_form,
        'comment_form': comment_form
    }
    return render(request, 'ticketApp/ticket_by_id.html', context)

from django.shortcuts import render, get_object_or_404, redirect
from .models import CompanyCRM, ContactCRM, Ticket

def caller_intake(request):
    search_query = request.GET.get('q', '').strip()
    companies = CompanyCRM.objects.none()
    contacts = ContactCRM.objects.none()

    if search_query:
        # Tech can search companies by name
        companies = CompanyCRM.objects.filter(company_name__icontains=search_query)[:15]
        # Tech can search contacts by first or last name
        contacts = ContactCRM.objects.filter(
            Q(first_name__icontains=search_query) | Q(last_name__icontains=search_query)
        ).select_related('company')[:15]

    context = {
        'companies': companies,
        'contacts': contacts,
        'search_query': search_query,
    }
    return render(request, 'ticketApp/caller_intake.html', context)

def company_contacts_partial(request, company_id):
    # This partial endpoint returns only the HTML snippet for contacts inside a clicked company
    company = get_object_or_404(CompanyCRM, pk=company_id)
    contacts = ContactCRM.objects.filter(company=company).order_by('last_name')
    return render(request, 'ticketApp/partials/company_contacts.html', {'contacts': contacts, 'company': company})

@login_required
def quick_add_contact(request):
    if request.method == 'POST':
        form = QuickContactForm(request.POST)
        if form.is_valid():
            # Manually inject the validated data row straight into your Postgres table
            new_contact = ContactCRM.objects.create(
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                email=form.cleaned_data['email'],
                phone=form.cleaned_data['phone'],
                company=form.cleaned_data['company']
            )
            messages.success(request, f"Contact '{new_contact.first_name} {new_contact.last_name}' added to CRM successfully!")
            # Drop the technician straight into the ticket form with their new contact selected!
            return redirect(f"/ticket/new/?contact_id={new_contact.contact_id}")
    else:
        form = QuickContactForm()
    return render(request, 'ticketApp/quick_add_contact.html', {'form': form})
