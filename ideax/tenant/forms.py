from django import forms
from .models import Client


class ClientForm(forms.ModelForm):
    email = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Client
        fields = ('name', 'domain_url', 'schema_name', 'on_trial', 'email', 'password')
