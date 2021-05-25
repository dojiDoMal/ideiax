from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.http.response import Http404

from pytest import mark, raises

from ...models import Challenge
from ...views import (challenge_new, challenge_detail, challenge_edit, challenge_remove)


class TestChallengeNew:
    def test_anonymous(self, rf):
        request = rf.get('/')
        request.user = AnonymousUser()
        response = challenge_new(request)
        assert (response.status_code, response.url) == (302, '/accounts/login/?next=/')

    def test_permission_denied(self, rf, common_user):
        request = rf.get('/')
        request.user = common_user
        with raises(PermissionDenied):
            challenge_new(request)

    def test_get(self, rf, mocker):
        render = mocker.patch('ideax.ideax.views.render')
        form = mocker.patch('ideax.ideax.views.ChallengeForm')

        request = rf.get(f'/')
        request.user = mocker.Mock()
        challenge_new(request)

        form.assert_called_once()
        render.assert_called_once_with(request, 'ideax/challenge_new.html', {'form': form.return_value})

    def test_post(self, rf, mocker, messages):
        form = mocker.patch('ideax.ideax.views.ChallengeForm')
        form.return_value.is_valid.return_value = True
        user_profile = mocker.patch('ideax.users.models.UserProfile.objects')
        user_profile.get.return_value = None

        request = rf.post('/', {})
        request.user = mocker.Mock()
        request._messages = messages
        response = challenge_new(request)

        assert (response.status_code, response.url) == (302, '/challenge/list/')
        assert messages.is_success
        assert messages.messages == ['Challenge saved successfully!']


class TestChallengeDetail:
    def test_anonymous(self, rf):
        request = rf.get('/')
        request.user = AnonymousUser()
        response = challenge_detail(request, 999)
        assert (response.status_code, response.url) == (302, '/accounts/login/?next=/')

    def test_get(self, rf, mocker):
        get = mocker.patch('ideax.ideax.views.get_object_or_404')
        render = mocker.patch('ideax.ideax.views.render')
        challenge = mocker.patch('ideax.ideax.views.Challenge')

        request = rf.get('/')
        request.user = mocker.Mock()
        challenge_detail(request, 999)

        get.assert_called_once_with(challenge, pk=999)
        get.return_value.idea_set.filter.assert_called_once_with(discarded=False)
        render.assert_called_once_with(request, 'ideax/challenge_detail.html',
                                       {'challenge': get.return_value,
                                        'ideas': get.return_value.idea_set.filter.return_value})


class TestChallengeEdit:
    def test_anonymous(self, rf):
        request = rf.get(f'/challenge/99999/edit/')
        request.user = AnonymousUser()
        response = challenge_edit(request, 99999)
        assert (response.status_code, response.url) == (302, '/accounts/login/?next=/challenge/99999/edit/')

    def test_not_found(self, rf, admin_user):
        request = rf.get(f'/challenge/99999/edit/')
        request.user = admin_user
        with raises(Http404):
            challenge_edit(request, 99999)

    def test_get_common_user(self, rf, common_user):
        request = rf.get('/challenge/1/edit/')
        request.user = common_user
        with raises(PermissionDenied):
            challenge_edit(request, 1)

    def test_get(self, rf, mocker):
        get = mocker.patch('ideax.ideax.views.get_object_or_404')
        render = mocker.patch('ideax.ideax.views.render')
        form = mocker.patch('ideax.ideax.views.ChallengeForm')

        request = rf.get(f'/challenge/55/edit/')
        request.user = mocker.Mock()
        challenge_edit(request, 55)

        get.assert_called_once_with(Challenge, pk=55)
        render.assert_called_once_with(request, 'ideax/challenge_edit.html', {'form': form.return_value})

    def test_post(self, rf, mocker, messages):
        get = mocker.patch('ideax.ideax.views.get_object_or_404')
        challenge_form = mocker.patch('ideax.ideax.views.ChallengeForm')
        challenge_form.return_value.is_valid.return_value = True

        request = rf.post(f'/challenge/55/edit/', {})
        request.user = mocker.Mock()
        request._messages = messages
        response = challenge_edit(request, 55)

        get.assert_called_once_with(Challenge, pk=55)
        challenge_form.assert_called_once_with(request.POST, request.FILES, instance=get.return_value)
        assert (response.status_code, response.url) == (302, '/challenge/list/')
        assert messages.is_success
        assert messages.messages == ['Challenge saved successfully!']


class TestChallengeRemove:
    def test_anonymous(self, rf):
        request = rf.get('/')
        request.user = AnonymousUser()
        response = challenge_remove(request, 999)
        assert (response.status_code, response.url) == (302, '/accounts/login/?next=/')

    def test_common_user(self, rf, common_user):
        request = rf.get('/')
        request.user = common_user
        with raises(PermissionDenied):
            challenge_remove(request, 1)

    @mark.skip
    def test_get(self, rf, mocker, messages):
        get_featured_challenges = mocker.patch('ideax.ideax.views.get_featured_challenges')
        get_featured_challenges.return_value = {}
        mocker.patch('ideax.ideax.views.Challenge')

        request = rf.get('/')
        request.user = mocker.Mock()
        request._messages = messages
        challenge_remove(request, 999)

        assert messages.is_success
        assert messages.messages == ['Challenge removed successfully!']
