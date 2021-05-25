from django.contrib.auth.decorators import login_required, permission_required
from django.utils import timezone
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.translation import ugettext_lazy as _ # noqa

from ...users.models import UserProfile
from ...util import get_client_ip, audit
from ..forms import CategoryImageForm
from ..models import Category_Image


@login_required
@permission_required('ideax.add_category_image', raise_exception=True)
def category_image_new(request):
    if request.method == "POST":
        form = CategoryImageForm(request.POST, request.FILES)

        if form.is_valid():
            category_image = form.save(commit=False)
            category_image.author = UserProfile.objects.get(user=request.user)
            category_image.creation_date = timezone.now()
            category_image.save()
            messages.success(request, _('Category Image saved successfully!'))
            audit(
                request.user.username,
                get_client_ip(request),
                'CREATE_CATEGORY_IMAGE',
                Category_Image.__name__,
                category_image.id)
            return redirect('category_image_list')
    else:
        form = CategoryImageForm()
    return render(request, 'ideax/category_image_new.html', {'form': form})


@login_required
def category_image_list(request):
    category_images = Category_Image.objects.all()
    audit(request.user.username, get_client_ip(request), 'LIST_CATEGORY_IMAGE', Category_Image.__name__, '')
    return render(request, 'ideax/category_image_list.html', {'category_images': category_images})


@login_required
@permission_required('ideax.change_category_image', raise_exception=True)
def category_image_edit(request, pk):
    category_image = get_object_or_404(Category_Image, pk=pk)

    if request.method == "POST":
        form = CategoryImageForm(request.POST, request.FILES, instance=category_image)

        if form.is_valid():
            form.save()
            messages.success(request, _('Category Image changed successfully!'))
            audit(
                request.user.username,
                get_client_ip(request),
                'EDIT_CATEGORY_IMAGE',
                Category_Image.__name__,
                str(pk))
            return redirect('category_image_list')
    else:
        form = CategoryImageForm(instance=category_image)
    return render(request, 'ideax/category_image_edit.html', {'form': form})


@login_required
@permission_required('ideax.delete_category_image', raise_exception=True)
def category_image_remove(request, pk):
    category_image = get_object_or_404(Category_Image, pk=pk)
    category_image.delete()
    messages.success(request, _('Category Image removed successfully!'))
    audit(request.user.username, get_client_ip(request), 'REMOVE_CATEGORY_IMAGE', Category_Image.__name__, str(pk))
    return redirect('category_image_list')
