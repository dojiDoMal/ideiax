from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.translation import ugettext_lazy as _ # noqa
from copy import deepcopy

from ...util import get_client_ip, audit, is_digit
from ..forms import DimensionForm, Category_DimensionForm, Category_DimensionFormset, Category_DimensionModelFormset
from ..models import Dimension, Category_Dimension
from ..validators import validate_add_edit_criteria, validate_dimension, validate_delete_dimension, validate_delete_category
from ..helpers import DimensionHelper, CategoryDimensionHelper
import re

def get_form_error_msg(form):
    form.is_valid()
    msg=[]
    for key, values in form.errors.items():
        for value in values:
            if value not in msg:
                msg.append(value)
    return msg

def get_formset_error_msg(formset):
    formset.is_valid()
    msg=[]
    for item in formset.errors:
        for key, values in item.items():
            if key is not 'id':
                for value in values:
                    if value not in msg:
                        msg.append(value)
    return msg

def filter_deleted_forms(formset):
    form_deletion_prefix = []
    deleted_forms = []

    for key in formset.data.keys():
        result = re.findall(r"form-\d+-DELETE", key)
        if len(result) > 0:
            form_deletion_prefix.append(re.findall(r"\d+", result[0])[0])
    
    for form in formset:
        result = re.findall(r'\d+', form.prefix) 
        if len(result) > 0 and result[0] in form_deletion_prefix:
            deleted_forms.append(form)

    return deleted_forms 

def filter_valid_forms(formset, deleted_forms=[]):
    form_list = []

    for form in formset:
        if form.is_valid() and form not in deleted_forms and len(form.clean())>0:
            form_list.append(form)
        else:
            data = form.data
            delete = form.prefix + "-DELETE"
            id = form.prefix + "-id"
            value = form.prefix + "-value"
            description = form.prefix + "-description"
            if delete not in data.keys() or not data[delete]:
                model = Category_Dimension()
                model.id = data[id] if id in data.keys() and is_digit(data[id]) else None
                model.pk = data[id] if id in data.keys() and is_digit(data[id]) else None
                model.value = int(data[value]) if value in data.keys() and is_digit(data[value]) else None  
                model.description = data[description] if description in data.keys() else None
                form_list.append(Category_DimensionForm(instance=model))
    return form_list

def filter_valid_deleted_categories(dimension, formset):
    
    deleted_forms = filter_deleted_forms(formset)
    form_list = filter_valid_forms(formset, deleted_forms)

    valid_categories = list(map(form_to_category, form_list))

    deleted_categories = list(map(form_to_category, deleted_forms))
    storered = CategoryDimensionHelper.filter_category_dimension_list(dimension)
    filter_deleted = lambda category: category not in valid_categories and category not in deleted_categories
    deleted_categories += list(filter(filter_deleted, storered))
    
    return [valid_categories, deleted_categories]

def form_to_category(form):    
    try:
        return form.save(commit=True)
    except:
        return form.instance

def generate_formset_data_from_critarya(categories):

    data ={
        'form-MAX_NUM_FORMS': '',
    }

    data['form-TOTAL_FORMS'] = len(categories)
    data['form-INITIAL_FORMS'] = len(categories)

    for counter, item in enumerate(categories):
        data['form-{0}-id'.format(counter)] = item.id
        data['form-{0}-value'.format(counter)] = item.value
        data['form-{0}-description'.format(counter)] = item.description
    return data

@login_required
@permission_required('ideax.add_dimension', raise_exception=True)
def dimension_new(request):
    if request.method == "POST":
        form = DimensionForm(request.POST)
        formset = Category_DimensionFormset(request.POST)
        msgs = []
        msgs += get_form_error_msg(form)
        msgs += get_formset_error_msg(formset)

        if form.is_valid() and formset.is_valid():
            categories = []
            dimension = form.save(commit=False)
            msgs += validate_dimension(dimension) 
            
            for form in formset:
                category = form.save(commit=False)
                categories.append(category) 
            msgs += validate_add_edit_criteria(categories)

            if len(msgs)==0:
                CategoryDimensionHelper.update(request, dimension, categories)
                messages.success(request, _('Dimension saved successfully!'))
                audit(request.user.username, get_client_ip(request), 'CREATE_DIMENSION', Dimension.__name__, dimension.log_msg())
                return redirect('dimension_list')
            else:
                form = DimensionForm(request.POST)
                formset = Category_DimensionFormset(request.POST)
                                                        
        for item in msgs:
            messages.error(request, _(item))  
    else:
        form = DimensionForm()
        formset = Category_DimensionFormset()

    return render(request, 'ideax/dimension_new.html', {'form': form, 'formset':formset, 'label_criteria': _('Criteria')})

@login_required
@permission_required('ideax.change_dimension', raise_exception=True)
def dimension_edit(request, pk):
    dimension = get_object_or_404(Dimension, pk=pk)

    if request.method == "POST":
        msgs = []
           
        form = DimensionForm(request.POST, instance=dimension)
        formset = Category_DimensionModelFormset(request.POST)
        msgs += get_form_error_msg(form)
        msgs += list(filter(lambda msg: msg not in msgs, get_formset_error_msg(formset)))         
        
        categories, deleted_category = filter_valid_deleted_categories(dimension, formset)
        
        dimension = form.save(commit=False)
        dimension_base = deepcopy(dimension)
        msgs += validate_dimension(dimension) if dimension_base.title != dimension.title else []      
        msgs += list(filter(lambda msg: msg not in msgs, validate_add_edit_criteria(categories)))  
        msgs += validate_delete_category(categories, deleted_category) 

        if len(msgs)==0:
            CategoryDimensionHelper.update(request, dimension, categories, deleted_category)
            messages.success(request, _('Dimension changed successfully!'))
            return redirect('dimension_list')
        else:
            audit(request.user.username, get_client_ip(request), 'DIMENSION_UPDATE', Dimension.__name__, dimension.log_msg())                                                          
            form = DimensionForm(request.POST, instance=dimension)
            data = generate_formset_data_from_critarya(categories)
            for category in data:
                audit(request.user.username, get_client_ip(request), 'CATEGORY_UPDATE', Category_Dimension.__name__, category.log_msg())  
            formset = Category_DimensionModelFormset(data=data)

        for item in msgs:
            messages.error(request, _(item))  
    else:
        audit(request.user.username, get_client_ip(request), 'DIMENSION_UPDATE', Dimension.__name__, dimension.log_msg())
        categories_queryset = CategoryDimensionHelper.filter_category_dimension_list(dimension)
        for category in categories_queryset:
            audit(request.user.username, get_client_ip(request), 'CATEGORY_UPDATE', Dimension.__name__, category.log_msg())
        form = DimensionForm(instance=dimension)
        formset = Category_DimensionModelFormset(queryset=categories_queryset)

    return render(request, 'ideax/dimension_edit.html', {'form': form, 'formset'  : formset, 'label_criteria': _('Criteria')})

@login_required
def dimension_list(request):
    audit(request.user.username, get_client_ip(request), 'DIMENSION_LIST', Dimension.__name__, '')
    dimension_dict = DimensionHelper.get_dimension_list()
    for dimension in dimension_dict['dimension_list']:
        audit(request.user.username, get_client_ip(request), 'DIMENSION', Dimension.__name__, dimension.log_msg())
    return render(request, 'ideax/dimension_list.html', dimension_dict)

@login_required
@permission_required('ideax.delete_dimension', raise_exception=True)
def dimension_remove(request, pk):
    dimension = get_object_or_404(Dimension, pk=pk)

    msgs = validate_delete_dimension(dimension)
    if len(msgs) != 0:
        for message in msgs:
            messages.error(request, _(message))
    else:
        categorias = CategoryDimensionHelper.filter_category_dimension_list(dimension)
        CategoryDimensionHelper.delete(categorias)
        
        dimension.active = False
        dimension.save()
        messages.success(request, _('Dimension removed successfully!'))
        msg = "{0} - {1}".format(str(pk), dimension.title)
        audit(request.user.username, get_client_ip(request), 'REMOVE_DIMENSION', Dimension.__name__, msg)
    
    return redirect('dimension_list')
