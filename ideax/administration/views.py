from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def administration(request):
    # FIXME after easy access to audit function
    # audit(request.user.username, get_client_ip(request), 'ADMINISTRATION_PAGE', Idea.__name__, '')
    return render(request, 'administration/index.html')
