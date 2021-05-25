from django.contrib.auth.decorators import login_required, permission_required
from django.utils import timezone
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.translation import ugettext_lazy as _ # noqa

from ...users.models import UserProfile
from ...util import get_client_ip, audit
from ..forms import CategoryForm
from ..models import Category


class CategoryHelper:
    @classmethod
    def get_category_list(cls):
        return {'category_list': Category.objects.filter(discarded=False)}


@login_required
@permission_required('ideax.add_category', raise_exception=True)
def category_new(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.author = UserProfile.objects.get(user=request.user)
            category.creation_date = timezone.now()
            category.save()
            messages.success(request, _('Category saved successfully!'))
            audit(request.user.username, get_client_ip(request), 'CREATE_CATEGORY', Category.__name__, category.id)
            return redirect('category_list')
    else:
        form = CategoryForm()
    return render(request, 'ideax/category_new.html', {'form': form})


@login_required
@permission_required('ideax.change_category', raise_exception=True)
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, _('Category changed successfully!'))
            audit(
                request.user.username,
                get_client_ip(request),
                'EDIT_CATEGORY_SAVE',
                Category.__name__,
                str(category.id)
            )
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)

    return render(request, 'ideax/category_edit.html', {'form': form})


@login_required
@permission_required('ideax.delete_category', raise_exception=True)
def category_remove(request, pk):
    category = get_object_or_404(Category, pk=pk)
    category.discarded = True
    category.save()
    messages.success(request, _('Category removed successfully!'))
    audit(request.user.username, get_client_ip(request), 'REMOVE_CATEGORY', Category.__name__, str(pk))
    return redirect('category_list')


@login_required
def category_list(request):
    audit(request.user.username, get_client_ip(request), 'CATEGORY_LIST', Category.__name__, '')
    return render(request, 'ideax/category_list.html', CategoryHelper.get_category_list())
