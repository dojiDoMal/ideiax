from django.contrib.auth.models import AnonymousUser

from ...views import index

from pytest import mark


class TestIndexView:
    def test_index_anonymous(self, rf):
        request = rf.get('/')
        request.user = AnonymousUser()
        response = index(request)
        assert response.status_code == 200
        assert 'class="login-button"' in response.content.decode('utf-8', 'strict')

    @mark.skip
    def test_index(self, ideax_views, rf, admin_user, mocker):
        ideax_views.audit = mocker.Mock()
        request = rf.get('/')
        request.user = admin_user
        response = index(request)
        assert response.status_code == 200
        # TODO: Enhance test
        assert '<title>Ideia X </title>' in response.content.decode('utf-8', 'strict')
