from django.contrib.auth import views as auth_views
from django.urls import path

from .views import profile, login, who_innovates, set_authconfiguration, auth_configuration_edit, user_permissions_select, user_permissions_edit

urlpatterns = [
    path('accounts/login/', login, name='login'),
    path('accounts/logout/', auth_views.logout, name='logout'),
    # path('accounts/sign-up/', SignUpView.as_view(), name='sign-up'),
    path('users/profile/<username>/', profile, name='profile'),
    path('users/whoinnovates/', who_innovates, name='whoinnovates'),
    path('configuration/set/', set_authconfiguration, name='set-configuration'),
    path('configuration/edit/', auth_configuration_edit, name='edit-configuration'),
    path('permission/select/', user_permissions_select, name='select-permission'),
    path('permission/edit/<username>/', user_permissions_edit, name='edit-permission'),
]
