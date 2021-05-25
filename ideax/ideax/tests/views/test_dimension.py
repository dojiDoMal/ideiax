from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.http.response import Http404
from django.utils.translation import ugettext_lazy as _ # noqa
from pytest import raises
from pytest import mark

from ...models import Dimension, Category_Dimension
from ...forms  import Category_DimensionFormset, Category_DimensionModelFormset
from ...views.dimension import DimensionHelper, dimension_edit, dimension_list, dimension_new, dimension_remove


class TestDimensionNew:
    def test_anonymous(self, rf):
        request = rf.get('/')
        request.user = AnonymousUser()
        response = dimension_new(request)
        assert (response.status_code, response.url) == (302, '/accounts/login/?next=/')

    def test_permission_denied(self, rf, common_user):
        request = rf.get('/')
        request.user = common_user
        with raises(PermissionDenied):
            dimension_new(request)

    def test_get(self, rf, factory_user, mocker):
        render = mocker.patch('ideax.ideax.views.dimension.render')
        form = mocker.patch('ideax.ideax.views.dimension.DimensionForm')
        formset = mocker.patch('ideax.ideax.views.dimension.Category_DimensionFormset')

        request = rf.get('/')
        request.user = factory_user('ideax.add_dimension')

        dimension_new(request)
        form.assert_called_once()
        render.assert_called_once_with(request, 'ideax/dimension_new.html', {'form': form.return_value, 
                                                                            'formset':formset.return_value, 
                                                                            'label_criteria': _('Criteria') })

    @mark.django_db
    def test_post(self, rf, factory_user, mocker, messages):
        audit = mocker.patch('ideax.ideax.views.dimension.audit')
        form = mocker.patch('ideax.ideax.views.dimension.DimensionForm')
        form.return_value.is_valid.return_value = True
        
        dimension = Dimension()
        dimension.weight = 5
        form.return_value.save.return_value = dimension
        
        formset = mocker.patch('ideax.ideax.views.dimension.Category_DimensionFormset')
        formset.return_value.is_valid.return_value = True

        mocker.patch('ideax.ideax.views.dimension.DimensionHelper.contain_dimension_by_title', return_value = False)
        mocker.patch('ideax.ideax.views.dimension.CategoryDimensionHelper.validate', return_value = [])
        mocker.patch('ideax.ideax.views.dimension.CategoryDimensionHelper.update')

        user_profile = mocker.patch('ideax.users.models.UserProfile.objects')
        user_profile.get.return_value = None

        request = rf.post('/', {})
        request.user = factory_user('ideax.add_dimension')
        request._messages = messages

        response = dimension_new(request)
        form.assert_called_once_with(request.POST)
        formset.assert_called_once_with(request.POST)

        audit.assert_called_once()
        assert (response.status_code, response.url) == (302, '/dimension/')
        assert messages.is_success
        assert messages.messages == [_('Dimension saved successfully!')]

    def test_post_invalid_form(self, rf, factory_user, mocker):
        form = mocker.patch('ideax.ideax.views.dimension.DimensionForm')
        form.return_value.is_valid.return_value = False

        formset = mocker.patch('ideax.ideax.views.dimension.Category_DimensionFormset')
        formset.return_value.is_valid.return_value = False

        user_profile = mocker.patch('ideax.users.models.UserProfile.objects')
        user_profile.get.return_value = None

        request = rf.post('/', {})
        request.user = factory_user('ideax.add_dimension')

        response = dimension_new(request)
        assert response.status_code == 200


class TestDimensionEdit:
    def test_anonymous(self, rf):
        request = rf.get(f'/dimension/99999/edit/')
        request.user = AnonymousUser()
        response = dimension_edit(request, 99999)
        assert (response.status_code, response.url) == (302, '/accounts/login/?next=/dimension/99999/edit/')
    
    def test_not_found(self, rf, factory_user, db):
        request = rf.get(f'/dimension/99999/edit/')
        request.user = factory_user('ideax.change_dimension')
        with raises(Http404):
            dimension_edit(request, 99999)

    def test_get_common_user(self, rf, common_user):
        request = rf.get('/dimension/1/edit/')
        request.user = common_user
        with raises(PermissionDenied):
            dimension_edit(request, 1)

    @mark.django_db
    def test_get(self, rf, factory_user, mocker):
        get = mocker.patch('ideax.ideax.views.dimension.get_object_or_404')
        render = mocker.patch('ideax.ideax.views.dimension.render')
        form = mocker.patch('ideax.ideax.views.dimension.DimensionForm')

        dimension = Dimension()
        dimension.title ="teste"
        dimension.description = "teste"
        dimension.weight = 5

        dimension.save()

        category = Category_Dimension()
        category.dimension_id = dimension.pk
        category.title = "teste 1"
        category.value = 5

        category.save()        

        request = rf.get(f'/dimension/' + str(dimension.pk) + '/edit/')
        request.user = factory_user('ideax.change_dimension')
        print(dimension.pk)
        dimension_edit(request, str(dimension.pk))

        get.assert_called_once_with(Dimension, pk=dimension.pk)
        render.assert_called_once_with(request, 'ideax/dimension_edit.html', {'form': form.return_value})

    def test_post(self, rf, factory_user, mocker, messages):
        get = mocker.patch('ideax.ideax.views.dimension.get_object_or_404')
        mocker.patch('ideax.ideax.views.dimension.audit')
        dimension_form = mocker.patch('ideax.ideax.views.dimension.DimensionForm')
        dimension_form.return_value.is_valid.return_value = True

        formset = mocker.patch('ideax.ideax.views.dimension.Category_DimensionModelFormset')
        formset.return_value.is_valid.return_value = True

        request = rf.post(f'/dimension/55/edit/', {})
        request.user = factory_user('ideax.change_dimension')
        request._messages = messages
        response = dimension_edit(request, 55)

        get.assert_called_once_with(Dimension, pk=55)
        dimension_form.assert_called_once_with(request.POST, instance=get.return_value)
        assert (response.status_code, response.url) == (302, '/dimension/')
        assert messages.is_success
        assert messages.messages == ['Dimension changed successfully!']

    def test_post_invalid_form(self, rf, factory_user, mocker, messages):
        get = mocker.patch('ideax.ideax.views.dimension.get_object_or_404')
        mocker.patch('ideax.ideax.views.dimension.audit')
        dimension_form = mocker.patch('ideax.ideax.views.dimension.DimensionForm')
        dimension_form.return_value.is_valid.return_value = False
        render = mocker.patch('ideax.ideax.views.dimension.render')

        request = rf.post(f'/dimension/55/edit/', {})
        request.user = factory_user('ideax.change_dimension')
        request._messages = messages
        dimension_edit(request, 55)

        get.assert_called_once_with(Dimension, pk=55)
        dimension_form.assert_called_once_with(request.POST, instance=get.return_value)
        # TODO: any fail message?
        render.assert_called_once_with(request, 'ideax/dimension_edit.html', {'form': dimension_form.return_value})


class TestDimensionRemove:
    def test_anonymous(self, rf):
        request = rf.get('/')
        request.user = AnonymousUser()
        response = dimension_remove(request, 999)
        assert (response.status_code, response.url) == (302, '/accounts/login/?next=/')

    def test_common_user(self, rf, common_user):
        request = rf.get('/')
        request.user = common_user
        with raises(PermissionDenied):
            dimension_remove(request, 1)

    def test_get(self, rf, factory_user, mocker, messages):
        audit = mocker.patch('ideax.ideax.views.dimension.audit')
        get = mocker.patch('ideax.ideax.views.dimension.get_object_or_404')
        dimension_helper = mocker.patch('ideax.ideax.views.dimension.DimensionHelper')
        dimension_helper.get_dimension_list.return_value = {}
        dimension = mocker.patch('ideax.ideax.views.dimension.Dimension')
        dimension.__name__ = 'Dimension'

        request = rf.get('/')
        request.user = factory_user('ideax.delete_dimension')
        request._messages = messages
        response = dimension_remove(request, 999)

        get.assert_called_once_with(dimension, pk=999)
        audit.assert_called_once()
        assert (response.status_code, response.url) == (302, '/dimension/')
        assert messages.is_success
        assert messages.messages == ['Dimension removed successfully!']


class TestDimensionList:
    def test_anonymous(self, rf):
        request = rf.get('/')
        request.user = AnonymousUser()
        response = dimension_list(request)
        assert (response.status_code, response.url) == (302, '/accounts/login/?next=/')

    def test_get(self, rf, mocker, common_user):
        mocker.patch('ideax.ideax.views.dimension.audit')
        dimension_helper = mocker.patch('ideax.ideax.views.dimension.DimensionHelper')
        dimension_helper.get_dimension_list.return_value = {}
        render = mocker.patch('ideax.ideax.views.dimension.render')

        request = rf.get('/')
        request.user = common_user
        dimension_list(request)

        render.assert_called_once_with(request, 'ideax/dimension_list.html', {})


class TestDimensionHelper:
    def test_get_dimension_list(self, mocker):
        objects = mocker.patch('ideax.ideax.views.dimension.Dimension.objects')
        objects.all.return_value = []

        result = DimensionHelper.get_dimension_list()

        assert result == {'dimension_list': []}
