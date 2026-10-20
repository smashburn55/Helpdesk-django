from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('intake/', views.caller_intake, name='caller_intake'),
    path('intake/company/<int:company_id>/contacts/', views.company_contacts_partial, name='company_contacts_partial'),
    path('intake/contact/new/', views.quick_add_contact, name='quick_add_contact'),
    path('ticket/new/', views.create_ticket, name='create_ticket'),
    path('ticket/<int:pk>/', views.ticket_by_id, name='ticket_by_id'),
    # Add this path rule inside your ticketApp/urls.py file:
    path('api/v1/web-intake/', views.web_intake_api, name='web_intake_api'),
    path('analytics/', views.helpdesk_analytics, name='helpdesk_analytics'),
    path('management/roster/', views.roster_management, name='roster_management'),
    path('management/roster/reset/<int:user_id>/', views.force_reset_password, name='force_reset_password'),
    path('management/roster/toggle/<int:user_id>/', views.toggle_tech_status, name='toggle_tech_status'),
    # Place this path string inside your ticketApp/urls.py patterns array list:
    path('ticket/<int:ticket_id>/claim-api/', views.claim_ticket_api, name='claim_ticket_api'),
    # Place this path string inside your ticketApp/urls.py array:
    path('company/<int:company_id>/ledger/', views.company_profile_ledger, name='company_profile_ledger'),
    path('ticket/<int:pk>/delete-override/', views.delete_ticket_manager_override, name='delete_ticket_manager_override'),
# 🔐 SECURTY LOGOUT PATHWAY: Registers the 'logout' nickname globally
    path('logout/', auth_views.LogoutView.as_view(next_page='index'), name='logout'),
# Add this path line inside your urlpatterns list array inside ticketApp/urls.py
    path('profile/settings/', views.profile_edit, name='profile_edit'),
    path('ticket/<int:pk>/comment/add/', views.add_comment, name='add_comment'),
# Add this line cleanly inside your urlpatterns array list inside ticketApp/urls.py
    path('api/get-contacts-by-company/', views.get_contacts_by_company_api, name='get_contacts_by_company_api'),

]
