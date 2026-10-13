from django import forms
from .models import Ticket, ContactCRM, CompanyCRM, Comment


# 1. NEW TICKET INTAKE FORM
class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['title', 'description', 'crm_contact']

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

