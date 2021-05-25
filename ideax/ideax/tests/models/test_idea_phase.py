from django.db.utils import DataError

from model_mommy import mommy
from pytest import fixture, raises, mark

from ...models import IdeaPhase


class TestIdeaPhase:
    @fixture
    def idea_phase(self, db):
        return mommy.make('IdeaPhase')

    def test_created(self, idea_phase):
        assert idea_phase.id is not None

    def test_str(self, idea_phase):
        idea_phase = mommy.make(IdeaPhase, name='Phase01')
        assert str(idea_phase) == 'Phase01'

    def test_max_name(self, db_vendor):
        if db_vendor != 'sqlite':
            with raises(DataError):
                mommy.make('IdeaPhase', name='X' * 51)

    # Teste a seguir sempre vai falhar, pois django não aplica limite a textfields
    @mark.skip
    def test_max_description(self, db_vendor):
        if db_vendor != 'sqlite':
            with raises(DataError):
                mommy.make('IdeaPhase', description='X' * 501)

    # verificar motivo de estar falhando
    @mark.skip
    def test_order_positive_number(self, db_vendor):
        if db_vendor != 'sqlite':
            with raises(DataError):
                mommy.make('IdeaPhase', order=1)

    def test_order_positive_value(self, idea_phase):
        idea_phase = mommy.make(IdeaPhase, order=True)
        assert idea_phase.order >= 0
