from django import forms
from .models import Ticket, ContactCRM, CompanyCRM, Comment


# 1. NEW TICKET INTAKE FORM
class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['title', 'description', 'priority', 'crm_contact']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['crm_contact'].queryset = ContactCRM.objects.all().order_by('last_name')
        self.fields['crm_contact'].empty_label = "-- Select CRM Contact --"
        self.fields['crm_contact'].required = True
        # Apply standard Bootstrap layout formatting classes
        self.fields['title'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Brief summary...'})
        self.fields['description'].widget.attrs.update(
            {'class': 'form-control', 'rows': 4, 'placeholder': 'Describe issue...'})
        self.fields['crm_contact'].widget.attrs.update({'class': 'form-select'})


# 2. INTERACTIVE DISCUSSION COMMENT FORM
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Type your message or internal update here...'
            }),
        }


# 3. TECHNICIAN METADATA PROPERTY MANAGEMENT FORM
class StatusUpdateForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['status', 'assignee']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'assignee': forms.Select(attrs={'class': 'form-select'}),
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
from django.contrib.auth.models import User

class TechnicianCreationForm(forms.ModelForm):
    """Secure operational form to initialize a fresh helpdesk agent row."""
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Set initial password...'}),
        label="Initial Access Password"
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'e.g., jsmith'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'email': forms.EmailInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'agent@yourdomain.com'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        # CRITICAL: Forces Django to securely hash and encrypt the raw password text string
        user.set_password(self.cleaned_data["password"])
        user.is_staff = True  # Automatically grants them baseline helpdesk technician clearance rules
        if commit:
            user.save()
        return user


class TechPasswordResetForm(forms.Form):
    """Manager-override text form to force-overwrite a forgotten password."""
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Type new secure password...'}),
        label="New Overwrite Password"
    )

