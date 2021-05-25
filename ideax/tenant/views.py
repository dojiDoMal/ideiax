from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from ideax.util import get_client_ip, audit
from ideax.users.utils import create_super_user
from .utils import (
    set_connection_by_tenant,
    set_connection_public_schema,
    load_init_data
)
from .forms import ClientForm
from .models import Client


@login_required
@permission_required('tenant.add_client', raise_exception=True)
def tenant_new(request):
    if request.method == "POST":
        form = ClientForm(request.POST)

        if form.is_valid():
            set_connection_public_schema()

            tenant = form.save(commit=False)
            tenant.created_on = timezone.localtime(timezone.now())
            tenant.save()

            set_connection_by_tenant(tenant)
            create_super_user(
                form.cleaned_data['email'],
                form.cleaned_data['email'],
                form.cleaned_data['password']
            )

            load_init_data()

            set_connection_by_tenant(request.tenant)
            messages.success(request, _('Tenant created successfully!'))

            audit(
                request.user.username,
                get_client_ip(request),
                'TENANT_NEW',
                Client.__name__,
                ''
            )

            return redirect('idea_list')
    else:
        form = ClientForm()

    return render(request, 'tenant_new.html', {'form': form})
