import json

from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db.models import Q, Count
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.db import transaction

from .models import (
    Ticket,
    TicketStatus,
    Comment,
    ContactCRM,
    CompanyCRM,
    TechProfile,
)

from .forms import (
    TicketForm,
    CommentForm,
    StatusUpdateForm,
    QuickContactForm,
    TechnicianCreationForm,
    TechPasswordResetForm,
    TechProfileForm,
)

@login_required
@ensure_csrf_cookie
def index(request):
    # Start with all tickets pulling down from Postgres
    tickets = Ticket.objects.all().order_by('-created_at').select_related('crm_contact', 'crm_contact__company', 'assignee')

    # Extract filter tokens from request parameters
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    view_scope = request.GET.get('scope', 'all')  # Options: 'all' or 'mine'

    # Filter by Keyword
    if search_query:
        tickets = tickets.filter(
            Q(title__icontains=search_query) | Q(description__icontains=search_query)
        )
    # Filter by Status
    if status_filter:
        tickets = tickets.filter(status=status_filter)

    # Filter by Assigned Technician (Scope)
    if view_scope == 'mine':
        tickets = tickets.filter(assignee=request.user)

    context = {
        'tickets': tickets,
        'search_query': search_query,
        'status_filter': status_filter,
        'view_scope': view_scope,
    }
    return render(request, 'ticketApp/index.html', context)


@login_required
def create_ticket(request):
    preselected_contact_id = request.GET.get('contact_id', '')

    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.status = 'TODO'

            # 1. FIXED MAPPING: Explicitly pull and assign the selected staff user object
            if form.cleaned_data.get('assignee'):
                ticket.assignee = form.cleaned_data['assignee']

            # 2. AUTOMATIC PARENT COMPANY LOOKUP:
            if not ticket.company and ticket.crm_contact:
                ticket.company = ticket.crm_contact.company

            ticket.save()  # Saves everything securely to your 9-table database
            send_ticket_confirmation_email(ticket)
            messages.success(request, 'Support ticket written directly to CRM database!')
            return redirect('index')

    else:
        initial_data = {}
        initial_data['assignee'] = request.user.id  # <-- ADD THIS LINE RIGHT HERE!

        if preselected_contact_id:
            initial_data['crm_contact'] = preselected_contact_id

            # =========================================================================
            # 🏢 DYNAMIC UX LINK OVERRIDE: Auto-populate the parent company select option
            # =========================================================================
            try:
                contact_record = ContactCRM.objects.get(pk=preselected_contact_id)
                if contact_record.company:
                    # Pre-selects his true corporate link directly inside your dropdown!
                    initial_data['company'] = contact_record.company
            except ContactCRM.DoesNotExist:
                pass

        form = TicketForm(initial=initial_data)

    return render(request, 'ticketApp/create_ticket.html', {'form': form})

def ticket_by_id(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    comments = ticket.comments.all().order_by('created_at')

    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, "Authentication required.")
            return redirect('ticket_by_id', pk=pk)

        # Check which form was submitted using a hidden HTML input name string
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

@login_required
def get_contacts_by_company_api(request):
    """Safe, read-only JSON endpoint that feeds the dropdown filter live on screen."""
    company_id = request.GET.get('company_id')

    if company_id:
        # Pull only existing CRM contact profiles bound to this specific corporate file
        contacts = ContactCRM.objects.filter(company_id=company_id).order_by('last_name')
    else:
        # Fallback layout: show independent profiles if no company is selected
        contacts = ContactCRM.objects.filter(company__isnull=True).order_by('last_name')

    # Translate database rows into a clean text matrix for your template script
    contact_list = [
        {'id': c.contact_id, 'name': f"{c.first_name} {c.last_name}"} for c in contacts
    ]
    return JsonResponse({'contacts': contact_list})

@login_required
def add_comment(request, pk):
    """Intercepts comment submissions and routes them securely by internal status flags."""
    ticket = get_object_or_404(Ticket, pk=pk)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.ticket = ticket
            comment.author = request.user
            comment.save()  # Saves the record cleanly to PostgreSQL with its is_internal flag

            messages.success(request, "Communication ledger note appended successfully.")

    return redirect('ticket_by_id', pk=pk)

@login_required
def caller_intake(request):
    """Customer Phone Intake workstation desk handles call logs, company filters, and contacts."""
    search_query = request.GET.get('search_query', '').strip()
    contacts = None
    companies = None  # <-- ADDED THIS PROPERTY ANCHOR

    # Always pull the complete alphabetical array for your 'Browse All' tray card desk
    all_companies = CompanyCRM.objects.all().order_by('company_name')

    if search_query:
        # 1. NEW COMPREHENSIVE SEARCH: Query your Company table directly for keyword matches
        companies = CompanyCRM.objects.filter(
            Q(company_name__icontains=search_query)
        ).distinct().order_by('company_name')

        # 2. Existing Comprehensive Search: Query your Contacts table directly
        contacts = ContactCRM.objects.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(company__company_name__icontains=search_query)
        ).distinct().order_by('last_name')

    # 2. ENSURE THE VARIABLE IS PRESENT INSIDE THE FINAL CONTEXT DICTIONARY
    context = {
        'contacts': contacts,
        'companies': companies,
        'search_query': search_query,
        'all_companies': all_companies, # <-- DOUBLE CHECK THIS LINE SEALS IT
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

@csrf_exempt  # Allows secure cross-origin submissions from your main marketing site
def web_intake_api(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only secure POST execution pipelines allowed.'}, status=405)

    try:
        # Parse the incoming JSON payload submitted from mashburndatasystems.com
        data = json.loads(request.body)
        email_address = data.get('email', '').strip().lower()
        title = data.get('title', '').strip()
        description = data.get('description', '').strip()
        system_details = data.get('system_details', '').strip() # e.g. OS, App Version

        if not email_address or not title or not description:
            return JsonResponse({'error': 'Missing mandatory tracking parameters.'}, status=400)

        # 1. Query PostgreSQL CRM Contacts Table for Sender Matching
        matching_contact = ContactCRM.objects.filter(email__iexact=email_address).first()

        if not matching_contact:
            # Fallback: Auto-generate an external contact record if unknown
            parsed_name = email_address.split('@')[0]
            matching_contact = ContactCRM.objects.create(
                first_name=parsed_name,
                last_name="Web Form Submitter",
                email=email_address
            )

        # Append any technical environment details straight to the description layout payload
        full_description = f"{description}\n\n---\nTechnical Environment Details:\n{system_details}"

        # 2. Write Ticket Directly into Live Production Grid Row
        new_ticket = Ticket.objects.create(
            title=title[:200],
            description=full_description,
            status='TODO',
            crm_contact=matching_contact,
            company=matching_contact.company if matching_contact.company else None
        )
        # TRIGGER AUTO-RESPONDER OUTBOUND packet
        send_ticket_confirmation_email(new_ticket)

        return JsonResponse({
            'success': True,
            'message': f'Ticket #{new_ticket.ticket_id} logged into production grid successfully.'
        }, status=201)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON request structural framing.'}, status=400)

def send_ticket_confirmation_email(ticket):
    """
    Automated transactional assistant that pulls a customer's email from
    PostgreSQL and fires a branded HTML tracker message immediately.
    """
    if not ticket.crm_contact or not ticket.crm_contact.email:
        return  # Abort safely if caller has no email recorded in CRM

    customer_email = ticket.crm_contact.email
    customer_name = f"{ticket.crm_contact.first_name} {ticket.crm_contact.last_name}"

    subject = f"[Ticket #{ticket.ticket_id}] Support Request Received: {ticket.title}"

    # Professional plain-text fallback content
    message_body = (
        f"Hi {ticket.crm_contact.first_name},\n\n"
        f"Your support request has been successfully logged directly into our system.\n\n"
        f"--- Ticket Details ---\n"
        f"Ticket Tracking ID: #{ticket.ticket_id}\n"
        f"Issue Topic: {ticket.title}\n"
        f"Current Status: New / To Do\n\n"
        f"A support technician has been notified and is reviewing your case file. "
        f"You can reply directly to this email if you need to provide extra information.\n\n"
        f"Best regards,\n"
        f"The Mashburn Data Systems IT Helpdesk Team"
    )

    try:
        send_mail(
            subject=subject,
            message=message_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[customer_email],
            fail_silently=False,  # Triggers terminal errors during local debugging if port blocks occur
        )
        print(f"CONFIRMATION EMAIL SENT SUCCESSFULLY TO: {customer_email}")
    except Exception as e:
        print(f"SMTP DELIVERY EXCEPTION ERROR: {str(e)}")

@login_required
def helpdesk_analytics(request):
    # Ensure only staff or managers can view team metrics
    if not request.user.is_staff:
        messages.error(request, "Access denied. Manager clearance required.")
        return redirect('index')

    # 1. Calculate critical queue volumes
    total_tickets = Ticket.objects.count()
    unassigned_count = Ticket.objects.filter(assignee__isnull=True).count()

    # 2. Extract Status Metrics distribution
    status_counts = Ticket.objects.values('status').annotate(total=Count('ticket_id'))
    status_dict = {'TODO': 0, 'PROG': 0, 'REV': 0, 'DONE': 0}
    for item in status_counts:
        status_dict[item['status']] = item['total']

    # 3. Aggregate individual technician workloads across the team
    # This runs a live group-by query joining your techs to their active ticket counts
    tech_workloads = User.objects.annotate(
        active_tickets=Count('tickets', filter=Q(tickets__status='DONE'))
    ).filter(active_tickets__gt=0).order_by('-active_tickets')

    context = {
        'total_tickets': total_tickets,
        'unassigned_count': unassigned_count,
        'status': status_dict,
        'tech_workloads': tech_workloads,
    }
    return render(request, 'ticketApp/analytics.html', context)

@login_required
@staff_member_required  # Security check: Only staff managers can access the roster tools
def roster_management(request):
    """Operational Hub to display, add, and toggle helpdesk technician profiles."""
    techs = User.objects.all().order_by('username')

    if request.method == 'POST' and 'add_tech' in request.POST:
        create_form = TechnicianCreationForm(request.POST)
        if create_form.is_valid():
            create_form.save()
            messages.success(request,
                             f"Technician account '{create_form.cleaned_data['username']}' initialized successfully!")
            return redirect('roster_management')
    else:
        create_form = TechnicianCreationForm()

    context = {
        'techs': techs,
        'create_form': create_form,
        'reset_form': TechPasswordResetForm()
    }
    return render(request, 'ticketApp/roster.html', context)


@login_required
@staff_member_required
@require_POST
def force_reset_password(request, user_id):
    """Bypasses mail servers to immediately force-overwrite an agent's password string."""
    tech = get_object_or_404(User, pk=user_id)
    reset_form = TechPasswordResetForm(request.POST)

    if reset_form.is_valid():
        tech.set_password(reset_form.cleaned_data['new_password'])
        tech.save()
        messages.success(request, f"Password for agent '{tech.username}' has been securely reset.")
    else:
        messages.error(request, "Invalid password specifications provided.")

    return redirect('roster_management')


@login_required
@staff_member_required
def toggle_tech_status(request, user_id):
    """Instantly revokes or reinstates server access without deleting historical log connections."""
    tech = get_object_or_404(User, pk=user_id)

    if tech == request.user:
        messages.error(request, "Security protection block: You cannot deactivate your own administrative account.")
    else:
        tech.is_active = not tech.is_active
        tech.save()
        status_text = "Activated" if tech.is_active else "Deactivated/Locked"
        messages.success(request, f"Account status for '{tech.username}' flipped to: {status_text}")

    return redirect('roster_management')

@login_required
@require_POST
def claim_ticket_api(request, ticket_id):
    """Assign an unclaimed ticket to the logged-in technician."""

    with transaction.atomic():
        ticket = get_object_or_404(
            Ticket.objects.select_for_update(),
            pk=ticket_id
        )

        if ticket.assignee_id is not None:
            return JsonResponse({
                'success': False,
                'message': 'This ticket is already assigned.'
            }, status=409)

        ticket.assignee = request.user

        if ticket.status == 'TODO':
            ticket.status = 'PROG'

        ticket.save()

    return JsonResponse({
        'success': True,
        'username': request.user.username
    })

@login_required
def company_profile_ledger(request, company_id):
    """Internal master ledger pulling native company assets, matching personnel trees, and history."""
    company = get_object_or_404(CompanyCRM, pk=company_id)

    # Extract all individual contacts tied to this parent corporation
    contacts = ContactCRM.objects.filter(company=company).order_by('last_name')

    # Extract all support tickets assigned to this account file
    tickets = Ticket.objects.filter(company=company).order_by('-ticket_id')

    context = {
        'company': company,
        'contacts': contacts,
        'tickets': tickets
    }
    return render(request, 'ticketApp/company_ledger.html', context)


@login_required
def delete_ticket_manager_override(request, pk):
    """Secure administrative route allowing managers to wipe accidental duplicates from the database."""
    # SECURITY GATE: Turn away standard agents instantly if they are not a superuser
    if not request.user.is_superuser:
        messages.error(request, "Access Denied: Administrative credential levels required to delete data rows.")
        return redirect('ticket_by_id', pk=pk)

    ticket = get_object_or_404(Ticket, pk=pk)
    ticket_title = ticket.title
    ticket.delete()  # Clears the row out of PostgreSQL completely

    messages.warning(request, f"Incident record '{ticket_title}' has been permanently purged from system logs.")
    return redirect('index')

@login_required
def profile_edit(request):
    """Secure settings workspace allowing technicians to update their phone parameters on the fly."""
    profile, created = TechProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = TechProfileForm(request.POST, instance=request.user, profile=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Your technician profile settings have been updated successfully.")
            return redirect('profile_edit')
    else:
        form = TechProfileForm(instance=request.user, profile=profile)

    return render(request, 'ticketApp/profile_edit.html', {'form': form})

