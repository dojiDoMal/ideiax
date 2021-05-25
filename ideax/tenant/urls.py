from django.urls import path
from .views import tenant_new


urlpatterns = [
    path('tenant/new', tenant_new, name='new-tenant'),
]
