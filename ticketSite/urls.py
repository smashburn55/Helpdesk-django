from django.contrib import admin
from django.urls import path, include  # <-- Make sure 'include' is imported here

urlpatterns = [
    path('admin/', admin.site.allowed_urls if hasattr(admin.site, 'allowed_urls') else admin.site.urls),
    path('', include('ticketApp.urls')),  # <-- This connects your app's homepage routes!
]
