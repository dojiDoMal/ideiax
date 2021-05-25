from django.contrib.auth.models import AnonymousUser
from pytest import fixture, raises
from django.http.response import Http404

from ...views import idea_detail


class TestIdeaListView:
    @fixture
    def get_ideas_init(self, ideax_views, mocker):
        return mocker.patch.object(ideax_views, 'get_ideas_init')

    def test_idea_detail_anonymous(self, rf):
        request = rf.get('/idea/detail')
        request.user = AnonymousUser()
        response = idea_detail(request)
        assert (response.status_code, response.url) == (302, '/accounts/login/?next=/idea/detail')

    def test_not_found(self, rf, admin_user):
        request = rf.get(f'/idea/99999/')
        request.user = admin_user
        with raises(Http404):
            idea_detail(request, 99999)
