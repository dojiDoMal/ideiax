from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _ # noqa
from django.contrib.auth.models import Group
from .helpers import DimensionHelper, CategoryDimensionHelper, parcial_evaluation
from .models import Dimension, Category_Dimension, Evaluation
from .enums import EvaluationPhase
from ..singleton import ProfanityCheck

class IdeaxValidate:
    def __init__(self, validators=[]):
        self.validators = validators

    def __call__(self, value):
        errors = []
        for validator in self.validators:
            try:
                validator(value)
            except ValidationError as e:
                errors.append(e.message)
        return errors

# Dimension
def validate_dimension(dimension):
    if len(Dimension.objects.filter(title__iexact=dimension.title, active=True)) > 0:
        return [_('A dimension with this title already exists')]
    return []

def validate_delete_dimension(dimension):

    assert dimension is not None

    if parcial_evaluation(dimension):
        return [_('The dimension is being used in an evaluation. Can not delete.')]
    return []

# Category
def validate_delete_category(categories, deleted_category):

    assert deleted_category is not None

    msg = []

    for category in deleted_category:
        if category.id is not None and parcial_evaluation(dimension=category.dimension, category=category):
            if len(msg) == 0:
                msg.append(_('The criterion is being used in evaluating an idea. Can not delete.'))
            categories.append(category)
    return msg

def validate_add_edit_criteria(categories):
    validation = IdeaxValidate([all_fields_are_requireds,
                                is_at_least_one_criteria_filled, 
                                is_at_least_one_criteria_has_max_value, 
                                is_two_criterias_same_name])
    return validation(categories)

def is_at_least_one_criteria_filled(categorias):
    for category in categorias:
        if category.value is not None and category.description is not None and category.value != "" and category.description != "":
            return None
    raise ValidationError(message =_('A dimension must have at least one criterion.'))

def all_fields_are_requireds(categorias):
    for category in categorias:
        ok = True
        if category.value == None or category.description == None: 
            ok = False
        if ok and (category.value == "" or len(category.description.replace(" ", "")) == 0): 
            ok = False
        if not ok:
            raise ValidationError(message =_("All fields are mandatory"))

def is_at_least_one_criteria_has_max_value(categorias):
    for category in categorias:
        if category.value is not None and category.value == 5:
            return None
    raise ValidationError(message =_('There must be at least one criterion in the dimension that has the maximum grade of the assessment as the value.'))

def is_two_criterias_same_name(categorias):
    names = []
    for category in categorias:
        if category.description is not None:
            if category.description.replace(" ", "").upper() in names:
                raise ValidationError(message =_('There is already a criterion with this title in dimension.'))
            elif len(category.description.replace(" ", ""))>0:
                names.append(category.description.replace(" ", "").upper())

def check_comment(raw_comment):
    if ProfanityCheck.wordcheck().search_badwords(raw_comment):
        return  _("Please check your message it has inappropriate content.")

    if not raw_comment:
        return  _("You have to write a comment.")
        
    return None
