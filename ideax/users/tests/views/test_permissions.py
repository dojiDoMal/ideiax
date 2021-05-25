from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.contrib.messages.storage.fallback import FallbackStorage
from pytest import mark, raises, fixture
from ...views import user_permissions_select, user_permissions_edit

class TestPermissionsView:
    @fixture
    def user(self, django_user_model):
        return django_user_model.objects.create(username='someone', password='secret')

    @fixture
    def super_user(self, django_user_model):
        return django_user_model.objects.create_superuser(username='someone2@testserver', email="someone2@testserver", password='secret')

    def test_anonymous_select(self, rf):
        request = rf.get('/permission/select/')
        request.user = AnonymousUser()
        response = user_permissions_select(request)
        assert (response.status_code, response.url) == (302, '/accounts/login/?next=/permission/select/')

    @mark.django_db
    def test_user_without_permission_select(self, rf, user):
        with raises(PermissionDenied) as error:
            request = rf.get('/permission/select/')
            request.user = user
            user_permissions_select(request)
        assert error.type == PermissionDenied

    @mark.django_db
    def test_user_with_permission_select(self, rf, super_user):
        request = rf.get('/permission/select/')
        request.user = super_user
        response = user_permissions_select(request)
        assert response.status_code == 200

    def test_anonymous_edit(self, rf):
        request = rf.get('/permission/edit/someone/')
        request.user = AnonymousUser()
        response = user_permissions_edit(request, username=request.user.username)
        assert (response.status_code, response.url) == (302, '/accounts/login/?next=/permission/edit/someone/')

    @mark.django_db
    def test_user_without_permission_edit(self, rf, user):
        with raises(PermissionDenied) as error:
            request = rf.get('/permission/edit/someone/')
            request.user = user
            user_permissions_edit(request, username=user.username)
        assert error.type == PermissionDenied

    @mark.django_db
    def test_user_with_permission_edit(self, rf, user, super_user):
        request = rf.get('/permission/edit/someone/')
        request.user = super_user
        response = user_permissions_edit(request, username=user.username)
        assert response.status_code == 200

    @mark.django_db
    def test_user_self_edit(self, rf, super_user):
        request = rf.get('/permission/edit/someone2@testserver/')
        # Fix para erro de mensagens do django em testes
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        request.user = super_user
        response = user_permissions_edit(request, username=super_user.username)
        assert response.status_code != 200
        assert (response.status_code, response.url) == (302, '/permission/select/')
