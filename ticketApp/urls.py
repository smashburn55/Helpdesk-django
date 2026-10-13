from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('intake/', views.caller_intake, name='caller_intake'),
    path('intake/company/<int:company_id>/contacts/', views.company_contacts_partial, name='company_contact_partial'),
    path('intake/contact/new/', views.quick_add_contact, name='quick_add_contact'),
    path('ticket/new/', views.create_ticket, name='create_ticket'),
    path('ticket/<int:pk>/', views.ticket_by_id, name='ticket_by_id'),
]
