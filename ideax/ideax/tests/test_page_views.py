from django.http.response import HttpResponseRedirect
from pytest import mark


class TestPageViews:
    @mark.django_db
    def test_frontpage(self, client):
        response = client.get('/')
        body = response.content.decode('utf-8', 'strict')
        assert 'class="login-button"' in body
        # assert 'você tem um canal aberto para a inovação' in body

    @mark.django_db
    def test_redirect_login(self, client):
        response = client.get('/idea/list')
        assert response.status_code == 302
        assert isinstance(response, HttpResponseRedirect)
        assert response.url == r'/accounts/login/?next=/idea/list'

    @mark.skip
    def test_idea_list_empty(self, ideax_views, client, django_user_model, mocker):
        ideax_views.audit = mocker.Mock()
        username, password = 'usuario', 'senha'
        django_user_model.objects.create_user(
            username=username,
            password=password,
            email='x@x.com'
        )
        client.login(username=username, password=password)
        response = client.get('/idea/list')
        assert response.status_code == 200
        body = response.content.decode('utf-8', 'strict')
        assert 'There are no ideas at this stage!' in body

    """TODO: refactor for IdeaPhase model"""
    def test_idea_list(self, ideax_views, client, django_user_model, mocker):
        # idea = mommy.make('Idea')
        # mommy.make('Phase_History', current_phase=Phase.GROW.id, idea=idea, current=True)
        # ideax_views.audit = mocker.Mock()
        # username, password = 'usuario', 'senha'
        # django_user_model.objects.create_user(
        #     username=username,
        #     password=password,
        #     email='x@x.com'
        # )
        # client.login(username=username, password=password)
        # response = client.get('/idea/list')
        # assert response.status_code == 200
        # body = response.content.decode('utf-8', 'strict')
        # assert 'There are no ideas at this stage!' not in body
        pass
