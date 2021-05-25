import os

from PIL import Image
from django import forms
from django.forms import formset_factory
from django.forms.models import modelformset_factory
from django.utils.translation import ugettext_lazy as _ # noqa
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.core.validators import MaxValueValidator, MinValueValidator, MaxLengthValidator
from django.conf import settings
from tinymce import TinyMCE
from martor.fields import MartorFormField

from .models import Idea, Criterion, Category, Challenge, Use_Term, Category_Image, Dimension, Category_Dimension, IdeaPhase


class IdeaForm(forms.ModelForm):
    challenge = forms.ModelChoiceField(
        queryset=Challenge.objects.filter(discarted=False),
        empty_label=_('Not related to any challenge'),
        required=False,
        label=_('Challenge')
    )
    oportunity = MartorFormField(label=_('Oportunity'), max_length=Idea._meta.get_field('oportunity').max_length)
    solution = MartorFormField(label=_('Solution'), max_length=Idea._meta.get_field('solution').max_length)
    target = MartorFormField(label=_('Target'), max_length=Idea._meta.get_field('target').max_length)
    summary = MartorFormField(label=_('Summary'), max_length=Idea._meta.get_field('summary').max_length)

    def __init__(self, *args, **kwargs):
        queryset = kwargs.pop('authors', None)
        super(IdeaForm, self).__init__(*args, **kwargs)
        self.fields['authors'] = forms.ModelMultipleChoiceField(
            queryset=queryset,
            widget=FilteredSelectMultiple("", is_stacked=False),
            required=False,
            label=_('Coauthors')
        )

    class Meta:
        model = Idea
        fields = ('title', 'summary', 'oportunity', 'solution', 'target', 'category', 'challenge', 'authors')
        labels = {'title': _('Title'), 'category': _('Category')}

    class Media:
        css = {
            'all': (os.path.join(settings.BASE_DIR, '/static/admin/css/widgets.css')),
        }
        js = ('/admin/jsi18n', 'jquery.js', 'jquery.init.js', 'core.js', 'SelectBox.js', 'SelectFilter2.js')


class IdeaFormUpdate(forms.ModelForm):

    class Meta:
        model = Idea
        fields = ('title', 'oportunity', 'solution', 'target')
        labels = {
            'title': _('Title'),
            'oportunity': _('Oportunity'),
            'solution': _('Solution'),
            'target': _('Target'),
        }


class CriterionForm(forms.ModelForm):

    class Meta:
        model = Criterion
        fields = ('description', 'peso')
        labels = {'peso': _('Weight'), 'description': _('Description')}


class CategoryForm(forms.ModelForm):

    class Meta:
        model = Category
        fields = ('title', 'description', )
        labels = {'title': _('Title'), 'description': _('Description')}


class CategoryImageForm(forms.ModelForm):

    class Meta:
        model = Category_Image
        fields = ('description', 'image', 'category')
        labels = {'description': _('Description'), 'image': _('Image'), 'category': _('Category')}


class ChallengeForm(forms.ModelForm):
    x = forms.FloatField(widget=forms.HiddenInput())
    y = forms.FloatField(widget=forms.HiddenInput())
    width = forms.FloatField(widget=forms.HiddenInput())
    height = forms.FloatField(widget=forms.HiddenInput())

    description = MartorFormField(
        label=_('Description'),
        max_length=Challenge._meta.get_field('description').max_length
    )

    class Meta:
        model = Challenge
        fields = (
            'title',
            'image',
            'x',
            'y',
            'width',
            'height',
            'summary',
            'requester',
            'description',
            'active',
            'limit_date',
            'init_date',
            'featured',
            'category',
        )
        labels = {
            'title': _('Title'),
            'image': _('Image'),
            'summary': _('Summary'),
            'requester': _('Requester'),
            'active': _('Active'),
            'limit_date': _('Limit Date'),
            'init_date': _('Init Date'),
            'featured': _('Featured'),
            'category': _('Category')}
        widgets = {
            'limit_date': forms.DateInput(attrs={'placeholder': 'dd/mm/aaaa'}),
            'init_date': forms.DateInput(attrs={'placeholder': 'dd/mm/aaaa'}),
        }

    def save(self):
        data = self.cleaned_data

        challenge = Challenge(title=data['title'],
                              image=data['image'],
                              summary=data['summary'],
                              requester=data['requester'],
                              description=data['description'],
                              limit_date=data['limit_date'],
                              init_date=data['init_date'],
                              active=data['active'],
                              featured=data['featured'],
                              category=data['category'],
                              discarted=False)

        x = self.cleaned_data.get('x')
        y = self.cleaned_data.get('y')
        w = self.cleaned_data.get('width')
        h = self.cleaned_data.get('height')

        image = Image.open(challenge.image)
        cropped_image = image.crop((x, y, w+x, h+y))

        img_path = challenge.image.path.split('/')
        img_name = img_path.pop()
        img_path.append('challenges')
        img_path.append(img_name)
        img_path = "/".join(img_path)

        cropped_image.save(img_path, format='JPEG', subsampling=0, quality=100)

        challenge.image = '/challenges/'+img_name

        return challenge


class UseTermForm(forms.ModelForm):

    class Meta:
        model = Use_Term
        fields = ('term', 'init_date', 'final_date')
        labels = {'term': _('Term'), 'init_date': _('Initial Date'), 'final_date': _('Final Date')}
        widgets = {
            'term': TinyMCE(),
        }


class EvaluationForm(forms.Form):
    FORMAT_ID = 'category_dimension_%s'
    FORMAT_ID_NOTE = 'note_dimension_%s'

    def __init__(self, *args, **kwargs):
        dimensions = kwargs.pop('extra', None)
        initial_arguments = kwargs.pop('initial', None)
        super(EvaluationForm, self).__init__(*args, **kwargs)

        def __category_dimension_id_return(item):
            if item is not None:
                return item.id
            else:
                return None

        if initial_arguments:
            for i in initial_arguments:
                id_field = self.FORMAT_ID % initial_arguments[i].dimension.pk
                self.fields[id_field] = forms.ModelChoiceField(
                    queryset=initial_arguments[i].dimension.category_dimension_set,
                    label=initial_arguments[i].dimension.title,
                    initial=__category_dimension_id_return(initial_arguments[i].category_dimension),
                    help_text=initial_arguments[i].dimension.description
                )

                id_field_note = self.FORMAT_ID_NOTE % initial_arguments[i].dimension.pk
                self.fields[id_field_note] = forms.CharField(initial=initial_arguments[i].note,
                                                             widget=forms.Textarea,
                                                             label='',
                                                             required=False)
        if dimensions:
            for dim in dimensions:
                self.fields[self.FORMAT_ID % dim.pk] = forms.ModelChoiceField(
                    queryset=dim.category_dimension_set.filter(active=True),
                    label=dim.title,
                    help_text=dim.description,
                    required=False,
                )
                self.fields[self.FORMAT_ID_NOTE % dim.pk] = forms.CharField(
                    widget=forms.Textarea,
                    label='',
                    required=False,
                )

class DimensionForm(forms.ModelForm):

    messages ={
        'required': _("All fields are mandatory"),
        'invalid': _('The weight of a dimension must be in the range of 1 to 5'),
        'title_size': _("Dimension title must have up to 200 characters."),
        'description_size': _("Dimension description must be up to 500 characters.")
    }

    title =  forms.CharField(label=_('Title'), error_messages={'required': messages['required']},
        validators=[MaxLengthValidator(200, message=messages['title_size'])])
    description =  forms.CharField(label=_('Description'), error_messages={'required': messages['required']},
        validators=[MaxLengthValidator(500, message=messages['description_size'])])

    weight = forms.DecimalField(label=_('Weight'), error_messages={'required': messages['required']},
        validators=[MaxValueValidator(5, messages['invalid']),
                    MinValueValidator(1, messages['invalid'])],
        widget=forms.NumberInput)

    class Meta:
        model = Dimension
        fields = ('title', 'description', 'weight')

class Category_DimensionForm(forms.ModelForm):

    messages ={
        'required': _("All fields are mandatory"),
        'invalid': _('The values of a criterion must be in the range of 1 to 5.'),
        'description_size': _("Criterion description must be up to 200 characters.")
    }

    description =  forms.CharField(error_messages={'required': messages['required']},
            validators=[MaxLengthValidator(200, message=messages['description_size'])])

    value = forms.DecimalField(error_messages={'required': messages['required']},
            widget=forms.NumberInput,
            validators=[MaxValueValidator(5, messages['invalid']),
                        MinValueValidator(1, messages['invalid'])])

    id = forms.DecimalField(required=False,
            widget=forms.NumberInput,
            validators=[MaxValueValidator(5, messages['invalid']),
                        MinValueValidator(1, messages['invalid'])])

    class Meta:
        model = Category_Dimension
        fields = ('description', 'value', 'id')
        labels = {
            'description': _('Description'), 'value': _('Value'),
        }

Category_DimensionFormset = formset_factory(Category_DimensionForm, extra=1)

Category_DimensionModelFormset = modelformset_factory(Category_Dimension, form=Category_DimensionForm,
                        fields=('description', 'value', 'id'),
                        widgets = {'value': forms.NumberInput(), 'requerid': True},
                        error_messages={'required': _("All fields are mandatory")},
                        extra=0,
                        can_delete=True)

class IdeaPhaseForm(forms.ModelForm):

    class Meta:
        model = IdeaPhase
        fields = ('name', 'description', 'order')
        labels = {
            'name': _('Name'), 'description': _('Description'), 'order': _('Order'),
            }

class ReportForm(forms.Form):
    start_date = forms.DateField(input_formats=['%d/%m/%Y'], label=_('Initial Date'),
                                 widget=forms.DateInput(attrs={'placeholder': 'dd/mm/aaaa'}), required=False)
    end_date = forms.DateField(input_formats=['%d/%m/%Y'], label=_('Final Date'),
                                 widget=forms.DateInput(attrs={'placeholder': 'dd/mm/aaaa'}), required=False)
    author = forms.CharField(required=False, label=_('Author'))
    phase = forms.ChoiceField(choices=(), required=False, label=_('Idea Phase'))
    discarded = forms.BooleanField(required=False, label=_(
        'Discarded'), widget=forms.CheckboxInput(attrs={'title': _('Consider discarded ideas?')}))


class HiddenReportForm(forms.Form):
    st = forms.DateField(input_formats=['%d/%m/%Y'], widget=forms.HiddenInput(), required=False)
    en = forms.DateField(input_formats=['%d/%m/%Y'], widget=forms.HiddenInput(), required=False)
    au = forms.CharField(required=False, widget=forms.HiddenInput())
    ph = forms.ChoiceField(choices=(), required=False, widget=forms.HiddenInput())
    ds = forms.BooleanField(required=False, widget=forms.HiddenInput())
