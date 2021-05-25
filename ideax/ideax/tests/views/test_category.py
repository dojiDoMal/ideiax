from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.http.response import Http404

from model_mommy import mommy
from pytest import raises

from ...models import Category
from ...views.category import CategoryHelper, category_edit, category_list, category_new, category_remove


class TestCategoryNew:
    def test_anonymous(self, rf):
        request = rf.get('/')
        request.user = AnonymousUser()
        response = category_new(request)
        assert (response.status_code, response.url) == (302, '/accounts/login/?next=/')

    def test_permission_denied(self, rf, common_user):
        request = rf.get('/')
        request.user = common_user
        with raises(PermissionDenied):
            category_new(request)

    def test_get(self, rf, factory_user, mocker):
        render = mocker.patch('ideax.ideax.views.category.render')
        form = mocker.patch('ideax.ideax.views.category.CategoryForm')

        request = rf.get('/')
        request.user = factory_user('ideax.add_category')

        category_new(request)
        form.assert_called_once()
        render.assert_called_once_with(request, 'ideax/category_new.html', {'form': form.return_value})

    def test_post(self, rf, factory_user, mocker, messages):
        audit = mocker.patch('ideax.ideax.views.category.audit')
        form = mocker.patch('ideax.ideax.views.category.CategoryForm')
        form.return_value.is_valid.return_value = True
        user_profile = mocker.patch('ideax.users.models.UserProfile.objects')
        user_profile.get.return_value = None

        request = rf.post('/', {})
        request.user = factory_user('ideax.add_category')
        request._messages = messages

        response = category_new(request)
        form.assert_called_once_with(request.POST)
        audit.assert_called_once()
        assert (response.status_code, response.url) == (302, '/category/list/')
        assert messages.is_success
        assert messages.messages == ['Category saved successfully!']

    def test_post_invalid_form(self, rf, factory_user, mocker):
        form = mocker.patch('ideax.ideax.views.category.CategoryForm')
        form.return_value.is_valid.return_value = False
        user_profile = mocker.patch('ideax.users.models.UserProfile.objects')
        user_profile.get.return_value = None

        request = rf.post('/', {})
        request.user = factory_user('ideax.add_category')

        response = category_new(request)
        # TODO: Maybe a message
        assert response.status_code == 200


class TestCategoryEdit:
    def test_anonymous(self, rf):
        request = rf.get(f'/category/99999/edit/')
        request.user = AnonymousUser()
        response = category_edit(request, 99999)
        assert (response.status_code, response.url) == (302, '/accounts/login/?next=/category/99999/edit/')

    def test_not_found(self, rf, factory_user, db):
        request = rf.get(f'/category/99999/edit/')
        request.user = factory_user('ideax.change_category')
        with raises(Http404):
            category_edit(request, 99999)

    def test_get_common_user(self, rf, common_user):
        request = rf.get('/category/1/edit/')
        request.user = common_user
        with raises(PermissionDenied):
            category_edit(request, 1)

    def test_get(self, rf, factory_user, mocker):
        get = mocker.patch('ideax.ideax.views.category.get_object_or_404')
        render = mocker.patch('ideax.ideax.views.category.render')
        form = mocker.patch('ideax.ideax.views.category.CategoryForm')

        request = rf.get(f'/category/55/edit/')
        request.user = factory_user('ideax.change_category')
        category_edit(request, 55)

        get.assert_called_once_with(Category, pk=55)
        render.assert_called_once_with(request, 'ideax/category_edit.html', {'form': form.return_value})

    def test_post(self, rf, factory_user, mocker, messages):
        get = mocker.patch('ideax.ideax.views.category.get_object_or_404')
        mocker.patch('ideax.ideax.views.category.audit')
        category_form = mocker.patch('ideax.ideax.views.category.CategoryForm')
        category_form.return_value.is_valid.return_value = True

        request = rf.post(f'/category/55/edit/', {})
        request.user = factory_user('ideax.change_category')
        request._messages = messages
        response = category_edit(request, 55)

        get.assert_called_once_with(Category, pk=55)
        category_form.assert_called_once_with(request.POST, instance=get.return_value)
        assert (response.status_code, response.url) == (302, '/category/list/')
        assert messages.is_success
        assert messages.messages == ['Category changed successfully!']

    def test_post_invalid_form(self, rf, factory_user, mocker, messages):
        get = mocker.patch('ideax.ideax.views.category.get_object_or_404')
        mocker.patch('ideax.ideax.views.category.audit')
        category_form = mocker.patch('ideax.ideax.views.category.CategoryForm')
        category_form.return_value.is_valid.return_value = False
        render = mocker.patch('ideax.ideax.views.category.render')

        request = rf.post(f'/category/55/edit/', {})
        request.user = factory_user('ideax.change_category')
        request._messages = messages
        category_edit(request, 55)

        get.assert_called_once_with(Category, pk=55)
        category_form.assert_called_once_with(request.POST, instance=get.return_value)
        # TODO: any fail message?
        render.assert_called_once_with(request, 'ideax/category_edit.html', {'form': category_form.return_value})


class TestCategoryRemove:
    def test_anonymous(self, rf):
        request = rf.get('/')
        request.user = AnonymousUser()
        response = category_remove(request, 999)
        assert (response.status_code, response.url) == (302, '/accounts/login/?next=/')

    def test_common_user(self, rf, common_user):
        request = rf.get('/')
        request.user = common_user
        with raises(PermissionDenied):
            category_remove(request, 1)

    def test_get(self, rf, factory_user, mocker, messages):
        audit = mocker.patch('ideax.ideax.views.category.audit')
        get = mocker.patch('ideax.ideax.views.category.get_object_or_404')
        get_category_list = mocker.patch('ideax.ideax.views.category.CategoryHelper.get_category_list')
        get_category_list.return_value = {}
        category = mocker.patch('ideax.ideax.views.category.Category')
        category.__name__ = 'Category'

        request = rf.get('/')
        request.user = factory_user('ideax.delete_category')
        request._messages = messages
        response = category_remove(request, 999)

        get.assert_called_once_with(category, pk=999)
        audit.assert_called_once()
        assert (response.status_code, response.url) == (302, '/category/list/')
        assert get.return_value.discarded is True
        assert messages.is_success
        assert messages.messages == ['Category removed successfully!']


class TestCategoryList:
    def test_anonymous(self, rf):
        request = rf.get('/')
        request.user = AnonymousUser()
        response = category_list(request)
        assert (response.status_code, response.url) == (302, '/accounts/login/?next=/')

    def test_get(self, rf, mocker, common_user):
        mocker.patch('ideax.ideax.views.category.audit')
        get_category_list = mocker.patch('ideax.ideax.views.category.CategoryHelper.get_category_list')
        get_category_list.return_value = {}
        render = mocker.patch('ideax.ideax.views.category.render')

        request = rf.get('/')
        request.user = common_user
        category_list(request)

        render.assert_called_once_with(request, 'ideax/category_list.html', {})


class TestCategoryHelper:
    def test_get_category_list(self, db):
        category = mommy.make('Category')
        categories = CategoryHelper.get_category_list()
        assert list(categories.keys()) == ['category_list']
        assert categories['category_list'].last() == category
