from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.http.response import Http404

from pytest import raises

from ...models import Criterion
from ...views import criterion_edit, criterion_list, criterion_new, criterion_remove


class TestCriterionNew:
    def test_anonymous(self, rf):
        request = rf.get('/')
        request.user = AnonymousUser()
        response = criterion_new(request)
        assert (response.status_code, response.url) == (302, '/accounts/login/?next=/')

    def test_permission_denied(self, rf, common_user):
        request = rf.get('/')
        request.user = common_user
        with raises(PermissionDenied):
            criterion_new(request)

    def test_get(self, rf, factory_user, mocker):
        render = mocker.patch('ideax.ideax.views.render')
        form = mocker.patch('ideax.ideax.views.CriterionForm')

        request = rf.get('/')
        request.user = factory_user('ideax.add_criterion')

        criterion_new(request)
        form.assert_called_once()
        render.assert_called_once_with(request, 'ideax/criterion_new.html', {'form': form.return_value})

    def test_post(self, rf, factory_user, mocker, messages):
        audit = mocker.patch('ideax.ideax.views.audit')
        form = mocker.patch('ideax.ideax.views.CriterionForm')
        form.return_value.is_valid.return_value = True
        user_profile = mocker.patch('ideax.users.models.UserProfile.objects')
        user_profile.get.return_value = None

        request = rf.post('/', {})
        request.user = factory_user('ideax.add_criterion')
        request._messages = messages

        response = criterion_new(request)
        form.assert_called_once_with(request.POST)
        audit.assert_called_once()
        assert (response.status_code, response.url) == (302, '/criterion/')
        assert messages.is_success
        assert messages.messages == ['Criterion saved successfully!']

    def test_post_invalid_form(self, rf, factory_user, mocker):
        form = mocker.patch('ideax.ideax.views.CriterionForm')
        form.return_value.is_valid.return_value = False
        user_profile = mocker.patch('ideax.users.models.UserProfile.objects')
        user_profile.get.return_value = None

        request = rf.post('/', {})
        request.user = factory_user('ideax.add_criterion')

        response = criterion_new(request)
        assert response.status_code == 200


class TestCriterionEdit:
    def test_anonymous(self, rf):
        request = rf.get(f'/criterion/99999/edit/')
        request.user = AnonymousUser()
        response = criterion_edit(request, 99999)
        assert (response.status_code, response.url) == (302, '/accounts/login/?next=/criterion/99999/edit/')

    def test_not_found(self, rf, factory_user, db):
        request = rf.get(f'/criterion/99999/edit/')
        request.user = factory_user('ideax.change_criterion')
        with raises(Http404):
            criterion_edit(request, 99999)

    def test_get_common_user(self, rf, common_user):
        request = rf.get('/criterion/1/edit/')
        request.user = common_user
        with raises(PermissionDenied):
            criterion_edit(request, 1)

    def test_get(self, rf, factory_user, mocker):
        get = mocker.patch('ideax.ideax.views.get_object_or_404')
        render = mocker.patch('ideax.ideax.views.render')
        form = mocker.patch('ideax.ideax.views.CriterionForm')

        request = rf.get(f'/criterion/55/edit/')
        request.user = factory_user('ideax.change_criterion')
        criterion_edit(request, 55)

        get.assert_called_once_with(Criterion, pk=55)
        render.assert_called_once_with(request, 'ideax/criterion_edit.html', {'form': form.return_value})

    def test_post(self, rf, factory_user, mocker, messages):
        get = mocker.patch('ideax.ideax.views.get_object_or_404')
        mocker.patch('ideax.ideax.views.audit')
        criterion_form = mocker.patch('ideax.ideax.views.CriterionForm')
        criterion_form.return_value.is_valid.return_value = True

        request = rf.post(f'/criterion/55/edit/', {})
        request.user = factory_user('ideax.change_criterion')
        request._messages = messages
        response = criterion_edit(request, 55)

        get.assert_called_once_with(Criterion, pk=55)
        criterion_form.assert_called_once_with(request.POST, instance=get.return_value)
        assert (response.status_code, response.url) == (302, '/criterion/')
        assert messages.is_success
        assert messages.messages == ['Criterion changed successfully!']

    def test_post_invalid_form(self, rf, factory_user, mocker, messages):
        get = mocker.patch('ideax.ideax.views.get_object_or_404')
        mocker.patch('ideax.ideax.views.audit')
        criterion_form = mocker.patch('ideax.ideax.views.CriterionForm')
        criterion_form.return_value.is_valid.return_value = False
        render = mocker.patch('ideax.ideax.views.render')

        request = rf.post(f'/criterion/55/edit/', {})
        request.user = factory_user('ideax.change_criterion')
        request._messages = messages
        criterion_edit(request, 55)

        get.assert_called_once_with(Criterion, pk=55)
        criterion_form.assert_called_once_with(request.POST, instance=get.return_value)
        # TODO: any fail message?
        render.assert_called_once_with(request, 'ideax/criterion_edit.html', {'form': criterion_form.return_value})


class TestCriterionRemove:
    def test_anonymous(self, rf):
        request = rf.get('/')
        request.user = AnonymousUser()
        response = criterion_remove(request, 999)
        assert (response.status_code, response.url) == (302, '/accounts/login/?next=/')

    def test_common_user(self, rf, common_user):
        request = rf.get('/')
        request.user = common_user
        with raises(PermissionDenied):
            criterion_remove(request, 1)

    def test_get(self, rf, factory_user, mocker, messages):
        audit = mocker.patch('ideax.ideax.views.audit')
        get = mocker.patch('ideax.ideax.views.get_object_or_404')
        get_criterion_list = mocker.patch('ideax.ideax.views.get_criterion_list')
        get_criterion_list.return_value = {}
        criterion = mocker.patch('ideax.ideax.views.Criterion')
        criterion.__name__ = 'Criterion'

        request = rf.get('/')
        request.user = factory_user('ideax.delete_criterion')
        request._messages = messages
        response = criterion_remove(request, 999)

        get.assert_called_once_with(criterion, pk=999)
        audit.assert_called_once()
        assert (response.status_code, response.url) == (302, '/criterion/')
        assert messages.is_success
        assert messages.messages == ['Criterion removed successfully!']


class TestCriterionList:
    def test_anonymous(self, rf):
        request = rf.get('/')
        request.user = AnonymousUser()
        response = criterion_list(request)
        assert (response.status_code, response.url) == (302, '/accounts/login/?next=/')

    def test_get(self, rf, mocker, common_user):
        mocker.patch('ideax.ideax.views.audit')
        get_criterion_list = mocker.patch('ideax.ideax.views.get_criterion_list')
        get_criterion_list.return_value = {}
        render = mocker.patch('ideax.ideax.views.render')

        request = rf.get('/')
        request.user = common_user
        criterion_list(request)

        render.assert_called_once_with(request, 'ideax/criterion_list.html', {})
