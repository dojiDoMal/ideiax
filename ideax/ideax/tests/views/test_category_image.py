from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.http.response import Http404

from pytest import raises

from ...models import Category_Image
from ...views import category_image_edit, category_image_list, category_image_new, category_image_remove


class TestCategoryImageNew:
    def test_anonymous(self, rf):
        request = rf.get('/')
        request.user = AnonymousUser()
        response = category_image_new(request)
        assert (response.status_code, response.url) == (302, '/accounts/login/?next=/')

    def test_permission_denied(self, rf, common_user):
        request = rf.get('/')
        request.user = common_user
        with raises(PermissionDenied):
            category_image_new(request)

    def test_get(self, rf, factory_user, mocker):
        render = mocker.patch('ideax.ideax.views.category_image.render')
        form = mocker.patch('ideax.ideax.views.category_image.CategoryImageForm')

        request = rf.get('/')
        request.user = factory_user('ideax.add_category_image')

        category_image_new(request)
        form.assert_called_once()
        render.assert_called_once_with(request, 'ideax/category_image_new.html', {'form': form.return_value})

    def test_post(self, rf, factory_user, mocker, messages):
        audit = mocker.patch('ideax.ideax.views.category_image.audit')
        form = mocker.patch('ideax.ideax.views.category_image.CategoryImageForm')
        form.return_value.is_valid.return_value = True
        user_profile = mocker.patch('ideax.users.models.UserProfile.objects')
        user_profile.get.return_value = None

        request = rf.post('/', {})
        request.user = factory_user('ideax.add_category_image')
        request._messages = messages

        response = category_image_new(request)
        form.assert_called_once_with(request.POST, request.FILES)
        audit.assert_called_once()
        assert (response.status_code, response.url) == (302, '/categoryimage/list/')
        assert messages.is_success
        assert messages.messages == ['Category Image saved successfully!']

    def test_post_invalid_form(self, rf, factory_user, mocker):
        form = mocker.patch('ideax.ideax.views.category_image.CategoryImageForm')
        form.return_value.is_valid.return_value = False
        user_profile = mocker.patch('ideax.users.models.UserProfile.objects')
        user_profile.get.return_value = None

        request = rf.post('/', {})
        request.user = factory_user('ideax.add_category_image')

        response = category_image_new(request)
        # TODO: Maybe a message
        assert response.status_code == 200


class TestCategoryImageEdit:
    def test_anonymous(self, rf):
        request = rf.get(f'/categoryimage/99999/edit/')
        request.user = AnonymousUser()
        response = category_image_edit(request, 99999)
        assert (response.status_code, response.url) == (302, '/accounts/login/?next=/categoryimage/99999/edit/')

    def test_not_found(self, rf, admin_user):
        request = rf.get(f'/categoryimage/99999/edit/')
        request.user = admin_user
        with raises(Http404):
            category_image_edit(request, 99999)

    def test_get_common_user(self, rf, common_user):
        request = rf.get('/categoryimage/1/edit/')
        request.user = common_user
        with raises(PermissionDenied):
            category_image_edit(request, 1)

    def test_get(self, rf, factory_user, mocker):
        get = mocker.patch('ideax.ideax.views.category_image.get_object_or_404')
        render = mocker.patch('ideax.ideax.views.category_image.render')
        form = mocker.patch('ideax.ideax.views.category_image.CategoryImageForm')

        request = rf.get(f'/category/55/edit/')
        request.user = factory_user('ideax.change_category_image')
        category_image_edit(request, 55)

        get.assert_called_once_with(Category_Image, pk=55)
        render.assert_called_once_with(request, 'ideax/category_image_edit.html', {'form': form.return_value})

    def test_post(self, rf, factory_user, mocker, messages):
        get = mocker.patch('ideax.ideax.views.category_image.get_object_or_404')
        mocker.patch('ideax.ideax.views.category_image.audit')
        category_form = mocker.patch('ideax.ideax.views.category_image.CategoryImageForm')
        category_form.return_value.is_valid.return_value = True

        request = rf.post(f'/category/55/edit/', {})
        request.user = factory_user('ideax.change_category_image')
        request._messages = messages
        response = category_image_edit(request, 55)

        get.assert_called_once_with(Category_Image, pk=55)
        category_form.assert_called_once_with(request.POST, request.FILES, instance=get.return_value)
        assert (response.status_code, response.url) == (302, '/categoryimage/list/')
        assert messages.is_success
        assert messages.messages == ['Category Image changed successfully!']

    def test_post_invalid_form(self, rf, factory_user, mocker, messages):
        get = mocker.patch('ideax.ideax.views.category_image.get_object_or_404')
        mocker.patch('ideax.ideax.views.category_image.audit')
        category_form = mocker.patch('ideax.ideax.views.category_image.CategoryImageForm')
        category_form.return_value.is_valid.return_value = False
        render = mocker.patch('ideax.ideax.views.category_image.render')

        request = rf.post(f'/category/55/edit/', {})
        request.user = factory_user('ideax.change_category_image')
        request._messages = messages
        category_image_edit(request, 55)

        get.assert_called_once_with(Category_Image, pk=55)
        category_form.assert_called_once_with(request.POST, request.FILES, instance=get.return_value)
        # TODO: any fail message?
        render.assert_called_once_with(request, 'ideax/category_image_edit.html', {'form': category_form.return_value})


class TestCategoryImageRemove:
    def test_anonymous(self, rf):
        request = rf.get('/')
        request.user = AnonymousUser()
        response = category_image_remove(request, 999)
        assert (response.status_code, response.url) == (302, '/accounts/login/?next=/')

    def test_common_user(self, rf, common_user):
        request = rf.get('/')
        request.user = common_user
        with raises(PermissionDenied):
            category_image_remove(request, 1)

    def test_get(self, rf, factory_user, mocker, messages):
        audit = mocker.patch('ideax.ideax.views.category_image.audit')
        get = mocker.patch('ideax.ideax.views.category_image.get_object_or_404')
        get_category_list = mocker.patch('ideax.ideax.views.category.CategoryHelper.get_category_list')
        get_category_list.return_value = {}
        category = mocker.patch('ideax.ideax.views.category_image.Category_Image')
        category.__name__ = 'Category_Image'

        request = rf.get('/')
        request.user = factory_user('ideax.delete_category_image')
        request._messages = messages
        response = category_image_remove(request, 999)

        get.assert_called_once_with(category, pk=999)
        audit.assert_called_once()
        get.return_value.delete.assert_called_once()
        assert (response.status_code, response.url) == (302, '/categoryimage/list/')
        assert messages.is_success
        assert messages.messages == ['Category Image removed successfully!']


class TestCategoryImageList:
    def test_anonymous(self, rf):
        request = rf.get('/')
        request.user = AnonymousUser()
        response = category_image_list(request)
        assert (response.status_code, response.url) == (302, '/accounts/login/?next=/')

    def test_get(self, rf, mocker, common_user):
        mocker.patch('ideax.ideax.views.category_image.audit')
        get_category_list = mocker.patch('ideax.ideax.views.category_image.Category_Image.objects')
        get_category_list.all.return_value = []
        render = mocker.patch('ideax.ideax.views.category_image.render')

        request = rf.get('/')
        request.user = common_user
        category_image_list(request)

        render.assert_called_once_with(request, 'ideax/category_image_list.html', {'category_images': []})
