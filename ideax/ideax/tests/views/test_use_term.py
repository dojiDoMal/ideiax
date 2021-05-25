from datetime import date

from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.http.response import Http404

from model_mommy import mommy
from pytest import mark, raises

from ...forms import UseTermForm
from ...views.use_term import (UseTermHelper, accept_use_term, get_valid_use_term, save_use_term, use_term_detail,
                               use_term_edit, use_term_list, use_term_new, use_term_remove)


class TestAcceptUseTermView:
    def test_accept_use_term_anonymous(self, rf):
        request = rf.get('/term/accept')
        request.user = AnonymousUser()
        response = accept_use_term(request)
        assert (response.status_code, response.url) == (302, '/accounts/login/?next=/term/accept')

    def test_accept_use_term_not_accepted(self, rf, common_user, messages, mocker):
        mocker.patch('ideax.users.models.UserProfile.objects')
        get_ip = mocker.patch('ideax.ideax.views.use_term.get_ip')
        mocker.patch('ideax.ideax.views.use_term.audit')
        common_user.userprofile.use_term_accept = False
        request = rf.get('/term/accept')
        request.user = common_user
        request._messages = messages
        response = accept_use_term(request)
        assert (response.status_code, response.url) == (302, '/')
        assert messages.messages == ['Term of use accepted!']
        get_ip.assert_called_once_with(request)

    @mark.skip
    def test_accept_use_term_accepted(self, rf, admin_user, messages, mocker):
        mocker.patch('ideax.ideax.views.use_term.audit')
        admin_user.userprofile.use_term_accept = True
        request = rf.get('/term/accept')
        request.user = admin_user
        request._messages = messages
        response = accept_use_term(request)
        assert (response.status_code, response.url) == (302, '/')
        assert messages.messages == ['Term of use already accepted!']


class TestUseTermEdit:
    def test_anonymous(self, rf):
        request = rf.get(f'/useterm/99999/edit/')
        request.user = AnonymousUser()
        response = use_term_edit(request, 99999)
        assert (response.status_code, response.url) == (302, '/accounts/login/?next=/useterm/99999/edit/')

    def test_not_found(self, rf, admin_user):
        request = rf.get(f'/useterm/99999/edit/')
        request.user = admin_user
        with raises(Http404):
            use_term_edit(request, 99999)

    def test_get_common_user(self, rf, common_user):
        request = rf.get('/useterm/1/edit/')
        request.user = common_user
        with raises(PermissionDenied):
            use_term_edit(request, 1)

    def test_get(self, rf, admin_user, ideax_views, mocker):
        use_term = mommy.make('Use_Term')
        use_term_form = mocker.patch.object(ideax_views.use_term, 'UseTermForm')
        save_use_term = mocker.patch.object(ideax_views.use_term, 'save_use_term')

        request = rf.get(f'/useterm/{use_term.id}/edit/')
        request.user = admin_user
        use_term_edit(request, use_term.id)
        use_term_form.assert_called_once_with(instance=use_term)
        save_use_term.assert_called_once_with(request, use_term_form.return_value, 'ideax/use_term_edit.html')

    def test_post(self, rf, admin_user, ideax_views, mocker):
        use_term = mommy.make('Use_Term')
        use_term_form = mocker.patch.object(ideax_views.use_term, 'UseTermForm')
        save_use_term = mocker.patch.object(ideax_views.use_term, 'save_use_term')

        request = rf.post(f'/useterm/{use_term.id}/edit/')
        request.user = admin_user
        use_term_edit(request, use_term.id)
        use_term_form.assert_called_once_with(request.POST, instance=use_term)
        save_use_term.assert_called_once_with(request, use_term_form.return_value, 'ideax/use_term_edit.html')


class TestSaveUseTerm:
    def test_get_full(self, rf, admin_user):
        # TODO: Change to a integrate test
        use_term = mommy.make('Use_Term')
        request = rf.get(f'/useterm/{use_term.id}/edit/')
        request.user = admin_user
        response = save_use_term(request, UseTermForm(instance=use_term), 'ideax/use_term_edit.html')
        body = response.content.decode('utf-8')
        assert response.status_code == 200
        assert '<form method="post" class="js-use_term-update-form"' in body
        assert "input type='hidden' name='csrfmiddlewaretoken'" in body
        assert '<button type="submit" class="btn btn-primary">Update</button>' in body

    def test_get_mocked(self, rf, admin_user, ideax_views, mocker):
        render = mocker.patch.object(ideax_views.use_term, 'render')
        request = rf.get('/')
        request.user = admin_user
        save_use_term(request, 'form', 'use_term_edit.html')
        render.assert_called_once_with(request, 'use_term_edit.html', {'form': 'form'})

    def test_post_invalid_final_date(self, rf, mocker, messages):
        form = mocker.patch('ideax.ideax.forms.UseTermForm')
        form.is_valid.return_value = True
        form.save.return_value.is_invalid_date.return_value = True
        terms = mocker.patch('ideax.ideax.models.Use_Term.objects')
        terms.all.return_value = []
        render = mocker.patch('ideax.ideax.views.use_term.render')
        user_profile = mocker.patch('ideax.users.models.UserProfile.objects')
        user_profile.get.return_value = None

        request = rf.post('/', {})
        request.user = mocker.Mock()
        request._messages = messages
        save_use_term(request, form, 'use_term_edit.html')

        render.assert_called_once_with(request, 'use_term_edit.html', {'form': form})
        assert messages.messages == ['Invalid Final Date']

    def test_post_new(self, rf, mocker, messages):
        """Without DB (100% mocked)"""

        form = mocker.patch('ideax.ideax.forms.UseTermForm')
        form.is_valid.return_value = True
        form.save.return_value.is_invalid_date.return_value = False
        terms = mocker.patch('ideax.ideax.models.Use_Term.objects')
        terms.get_active.return_value = True
        render = mocker.patch('ideax.ideax.views.use_term.render')
        user_profile = mocker.patch('ideax.users.models.UserProfile.objects')
        user_profile.get.return_value = None

        request = rf.post('/', {})
        request.user = mocker.Mock()
        request._messages = messages
        save_use_term(request, form, 'use_term_edit.html', True)
        render.assert_called_once_with(request, 'use_term_edit.html', {'form': form})
        assert messages.messages == ['Already exists a active Term Of Use']
        user_profile.get.assert_called_once_with(user=request.user)
        form.save.assert_called_once_with(commit=False)

    def test_post_new_inactive(self, rf, mocker, messages):
        form = mocker.patch('ideax.ideax.forms.UseTermForm')
        form.is_valid.return_value = True
        form.save.return_value.is_invalid_date.return_value = False
        terms = mocker.patch('ideax.ideax.models.Use_Term.objects')
        terms.get_active.return_value = False
        user_profile = mocker.patch('ideax.users.models.UserProfile.objects')
        user_profile.get.return_value = None

        request = rf.post('/', {})
        request.user = mocker.Mock()
        request._messages = messages
        response = save_use_term(request, form, 'use_term_edit.html', True)
        assert (response.status_code, response.url) == (302, '/useterm/list/')
        assert messages.messages == ['Term of Use saved successfully!']
        user_profile.get.assert_called_once_with(user=request.user)

    @mark.skip('TODO: save use term with invalid form')
    def test_post_form_invalid(self, rf, admin_user, mocker):
        form = mocker.patch('ideax.ideax.forms.UseTermForm')
        form.is_valid.return_value = False
        form.save.return_value.is_invalid_date.return_value = False
        request = rf.post('/', {})
        request.user = admin_user
        response = save_use_term(request, form, 'use_term_edit.html', True)
        # TODO: maybe a message
        assert response is not None


class TestUseTermRemove:
    def test_anonymous(self, rf):
        request = rf.get('/')
        request.user = AnonymousUser()
        response = use_term_remove(request, 999)
        assert (response.status_code, response.url) == (302, '/accounts/login/?next=/')

    def test_common_user(self, rf, common_user):
        request = rf.get('/')
        request.user = common_user
        with raises(PermissionDenied):
            use_term_remove(request, 1)

    def test_invalid_method(self, rf, mocker):
        mocker.patch('ideax.ideax.views.use_term.get_object_or_404')
        request = rf.post('/', {})
        request.user = mocker.Mock()
        response = use_term_remove(request, 999)
        assert response is None

    def test_get(self, rf, mocker, messages):
        get = mocker.patch('ideax.ideax.views.use_term.get_object_or_404')
        get_use_term_list = mocker.patch('ideax.ideax.views.use_term.UseTermHelper.get_use_term_list')
        get_use_term_list.return_value = {}
        render = mocker.patch('ideax.ideax.views.use_term.render')
        use_term = mocker.patch('ideax.ideax.views.use_term.Use_Term')

        request = rf.get('/')
        request.user = mocker.Mock()
        request._messages = messages
        use_term_remove(request, 999)

        get.assert_called_once_with(use_term, pk=999)
        render.assert_called_once_with(request, 'ideax/use_term_list.html', {})
        assert messages.messages == ['Terms of Use removed successfully!']


class TestUseTermDetail:
    def test_anonymous(self, rf):
        request = rf.get('/')
        request.user = AnonymousUser()
        response = use_term_detail(request, 999)
        assert (response.status_code, response.url) == (302, '/accounts/login/?next=/')

    def test_get(self, rf, mocker):
        get = mocker.patch('ideax.ideax.views.use_term.get_object_or_404')
        render = mocker.patch('ideax.ideax.views.use_term.render')
        use_term = mocker.patch('ideax.ideax.views.use_term.Use_Term')

        request = rf.get('/')
        request.user = mocker.Mock()
        use_term_detail(request, 999)

        get.assert_called_once_with(use_term, pk=999)
        render.assert_called_once_with(request, 'ideax/use_term_detail.html', {'use_term': get.return_value})


class TestGetValidUseTerm:
    def test_empty(self, rf, mocker):
        terms = mocker.patch('ideax.ideax.models.Use_Term.objects')
        terms.all.return_value = []
        render = mocker.patch('ideax.ideax.views.use_term.render')

        request = rf.get('/')
        get_valid_use_term(request)

        render.assert_called_once_with(request, 'ideax/use_term.html', {'use_term': 'No Term of Use found'})

    def test_no_valid(self, rf, mocker):
        terms = mocker.patch('ideax.ideax.models.Use_Term.objects')
        terms.all.return_value = [mocker.Mock(is_past_due=False)]
        render = mocker.patch('ideax.ideax.views.use_term.render')

        request = rf.get('/')
        get_valid_use_term(request)

        render.assert_called_once_with(request, 'ideax/use_term.html', {'use_term': 'No Term of Use found'})

    def test_valid(self, rf, mocker):
        terms = mocker.patch('ideax.ideax.models.Use_Term.objects')
        term = mocker.Mock(is_past_due=True)
        terms.all.return_value = [term]
        render = mocker.patch('ideax.ideax.views.use_term.render')

        request = rf.get('/')
        get_valid_use_term(request)

        render.assert_called_once_with(request, 'ideax/use_term.html', {'use_term': term})


class TestUseTermList:
    def test_anonymous(self, rf):
        request = rf.get('/')
        request.user = AnonymousUser()
        response = use_term_list(request)
        assert (response.status_code, response.url) == (302, '/accounts/login/?next=/')

    def test_get(self, rf, mocker):
        get_use_term_list = mocker.patch('ideax.ideax.views.use_term.UseTermHelper.get_use_term_list')
        get_use_term_list.return_value = {}
        render = mocker.patch('ideax.ideax.views.use_term.render')

        request = rf.get('/')
        request.user = mocker.Mock()
        use_term_list(request)

        render.assert_called_once_with(request, 'ideax/use_term_list.html', {})


class TestUseTermNew:
    def test_anonymous(self, rf):
        request = rf.get('/')
        request.user = AnonymousUser()
        response = use_term_new(request)
        assert (response.status_code, response.url) == (302, '/accounts/login/?next=/')

    def test_get_common_user(self, rf, common_user):
        request = rf.get('/')
        request.user = common_user
        with raises(PermissionDenied):
            use_term_new(request, 1)

    def test_get(self, rf, mocker):
        form = mocker.patch('ideax.ideax.views.use_term.UseTermForm')
        form.return_value = {}
        save_use_term = mocker.patch('ideax.ideax.views.use_term.save_use_term')

        request = rf.get('/')
        request.user = mocker.Mock()
        use_term_new(request)

        form.assert_called_once_with()
        save_use_term.assert_called_once_with(request, {}, 'ideax/use_term_new.html', True)

    def test_post(self, rf, mocker):
        form = mocker.patch('ideax.ideax.views.use_term.UseTermForm')
        form.return_value = {}
        save_use_term = mocker.patch('ideax.ideax.views.use_term.save_use_term')

        request = rf.post('/', {})
        request.user = mocker.Mock()
        use_term_new(request)

        form.assert_called_once_with(request.POST)
        save_use_term.assert_called_once_with(request, {}, 'ideax/use_term_new.html', True)


class TestUseTermHelper:
    @mark.skip
    def test_get_use_term_list(self, ideax_views, db, mocker):
        datelib = mocker.patch('ideax.ideax.views.use_term.date')
        datelib.today.return_value = date(2010, 1, 1)
        response = UseTermHelper.get_use_term_list()
        assert len(response['use_term_list']) == 1
        assert response['use_term_list'][0].term == 'A generic Term of Use.'
        assert response['today'] == date(2010, 1, 1)
