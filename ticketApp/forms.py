from django import forms
from django.contrib.auth.models import User
from .models import Ticket, ContactCRM, CompanyCRM, Comment, TechProfile

# 1. NEW TICKET INTAKE FORM

class TicketForm(forms.ModelForm):
    """Upgraded Ticket Form featuring dynamic editable corporate and technician selectors."""

    company = forms.ModelChoiceField(
        queryset=CompanyCRM.objects.all().order_by('company_name'),
        required=False,
        empty_label="-- Independent Customer (No Corporate File) --",
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Assigned Corporate Account"
    )

    # NEW WORKFLOW SELECTOR: Dynamic dropdown pulling all helpdesk users/agents
    assignee = forms.ModelChoiceField(
        queryset=User.objects.all().order_by('username'),
        required=False,
        empty_label="-- Unassigned / Queue Default --",
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Assign Support Technician"
    )

    class Meta:
        model = Ticket
        # ADDED 'assigned_tech' cleanly to your fields list right here
        fields = ['title', 'description', 'status', 'priority', 'company', 'assignee', 'crm_contact']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Brief issue summary...'}),
            'description': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Detailed diagnostics...'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'crm_contact': forms.HiddenInput(),
        }


# 2. INTERACTIVE DISCUSSION COMMENT FORM

class CommentForm(forms.ModelForm):
    """Upgraded comment form supporting private internal troubleshooting logs."""
    class Meta:
        model = Comment
        fields = ['text', 'is_internal']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control form-control-sm',
                'rows': 3,
                'placeholder': 'Type your diagnostic update or private notes here...'
            }),
            'is_internal': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'id': 'internalNoteCheck'
            })
        }


# 3. TECHNICIAN METADATA PROPERTY MANAGEMENT FORM
class StatusUpdateForm(forms.ModelForm):
    """Handles updating ticket parameters from the detail sidebar panel."""

    # Expose your alphabetical corporate accounts registry cleanly
    company = forms.ModelChoiceField(
        queryset=CompanyCRM.objects.all().order_by('company_name'),
        required=False,
        empty_label="-- Independent Client (No Corporate File) --",
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'}),
        label="Assigned Company File"
    )
    # 👤 NEW: INTERACTIVE CONTACT SELECTOR MATRIX
    crm_contact = forms.ModelChoiceField(
        queryset=ContactCRM.objects.all().order_by('last_name', 'first_name'),
        required=False,
        empty_label="-- Unknown / System Placeholder --",
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'}),
        label="Assigned Customer Contact"
    )

    class Meta:
        model = Ticket
        fields = ['status', 'assignee', 'priority', 'company', 'crm_contact']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'assignee': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class ': 'form-select form-select-sm'}), # <-- Clean dropdown style

        }

class QuickContactForm(forms.Form):
    first_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    phone = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    # Tech can pick an existing company file to attach them to
    company = forms.ModelChoiceField(
        queryset=CompanyCRM.objects.all().order_by('company_name'),
        required=False,
        empty_label="-- Independent / No Company --",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

class TechnicianCreationForm(forms.ModelForm):
    """Secure operational form to initialize a fresh helpdesk agent row with strict criteria."""
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'John'}),
        required=True,
        label="First Name"
    )
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Doe'}),
        required=True,
        label="Last Name"
    )
    phone_number = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': '555-123-4567'}),
        required=True,
        label="Primary Phone Number"
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Set initial password...'}),
        label="Initial Access Password"
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'e.g., jdoe'}),
            'email': forms.EmailInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'agent@yourdomain.com'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.is_staff = True
        if commit:
            user.save()
            # Dynamically saves the phone number to the user's hidden metadata profile
            # This ensures we store it cleanly without crashing your current PostgreSQL tables
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            user.save()
        return user

class TechPasswordResetForm(forms.Form):
    """Manager-override text form to force-overwrite a forgotten password."""
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Type new secure password...'}),
        label="New Overwrite Password"
    )

class TechProfileForm(forms.ModelForm):
    """Form to handle core technician data and phone information concurrently."""
    first_name = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    phone_number = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(555) 555-5555'}))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        # Pull the custom profile object if passed in to populate the telephone field layout
        profile = kwargs.pop('profile', None)
        super().__init__(*args, **kwargs)
        if profile:
            self.fields['phone_number'].initial = profile.phone_number

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            # Automatically save or update the linked tech phone record row too
            profile, created = TechProfile.objects.get_or_create(user=user)
            profile.phone_number = self.cleaned_data['phone_number']
            profile.save()
        return user
