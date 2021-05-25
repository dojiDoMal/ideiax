from django.db.utils import DataError

from model_mommy import mommy
from pytest import raises, fixture, mark

from ...models import Idea


class TestIdea:
    @fixture
    def idea(self, db):
        return mommy.make('Idea')

    def test_get_current_phase_history(self, idea):
        ph = mommy.make('Phase_History', idea=idea, current=True)
        assert idea.get_current_phase_history() == ph

    def test_get_absolute_url(self):
        idea = Idea(id=999)
        assert idea.get_absolute_url() == '/idea/999/'

    def test_get_approval_rate_zero(self, idea):
        assert idea.get_approval_rate() == 0

    def test_get_approval_rate(self, idea):
        mommy.make('Popular_Vote', idea=idea, like=True)
        mommy.make('Popular_Vote', idea=idea, like=False)
        assert idea.get_approval_rate() == 50

    # Teste a seguir sempre vai falhar, pois django não aplica limite a textfields, somente a charfields
    @mark.skip
    def test_max_length_summary(self, db_vendor):
        if db_vendor != 'sqlite':
            with raises(DataError):
                mommy.make('Idea', summary='X' * 141)

    def test_max_length_title(self, db_vendor):
        if db_vendor != 'sqlite':
            with raises(DataError):
                mommy.make('Idea', title='X' * 201)

    # Teste a seguir sempre vai falhar, pois django não aplica limite a textfields
    @mark.skip
    def test_max_length_oportunity(self, db_vendor):
        if db_vendor != 'sqlite':
            with raises(DataError):
                mommy.make('Idea', oportunity='X' * 2501)

    # Teste a seguir sempre vai falhar, pois django não aplica limite a textfields
    @mark.skip
    def test_max_length_target(self, db_vendor):
        if db_vendor != 'sqlite':
            with raises(DataError):
                mommy.make('Idea', target='X' * 501)

    def test_max_length_category_image(self, db_vendor):
        if db_vendor != 'sqlite':
            with raises(DataError):
                mommy.make('Idea', category_image='X' * 201)

    # Teste a seguir sempre vai falhar, pois django não aplica limite a textfields
    @mark.skip
    def test_max_length_solution(self, db_vendor):
        if db_vendor != 'sqlite':
            with raises(DataError):
                mommy.make('Idea', solution='X' * 2501)

    def test_get_approval_rate_mock(self, mocker):
        likes = mocker.patch.object(Idea, 'count_likes')
        likes.return_value = 1
        dislikes = mocker.patch.object(Idea, 'count_dislikes')
        dislikes.return_value = 1
        idea = Idea()
        assert idea.get_approval_rate() == 50

    def test_score_value(self, idea):
        assert idea.score == 0
