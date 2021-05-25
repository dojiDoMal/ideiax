from pytest import mark
from django.contrib.auth.models import AnonymousUser

from ...views import profile


class TestProfile:
    def test_anonymous(self, rf):
        request = rf.get('/')
        request.user = AnonymousUser()
        response = profile(request)
        assert (response.status_code, response.url) == (302, '/accounts/login/?next=/')

    @mark.skip
    def test_get(self, rf, common_user, mocker):
        common_user.userprofile.authors.all.return_value = []
        render = mocker.patch('ideax.users.views.render')
        request = rf.get('/')
        request.user = common_user
        profile(request)
        render.assert_called_once_with(request, 'users/profile.html', {'user': common_user, 'ideas': []})
