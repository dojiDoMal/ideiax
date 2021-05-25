from model_mommy import mommy
from pytest import fixture


class TestEvaluation:
    @fixture
    def evaluation(self, db):
        return mommy.make('Evaluation')

    def test_created(self, evaluation):
        assert evaluation.id is not None
