from model_mommy import mommy
from pytest import fixture


class TestEvaluationItem:
    @fixture
    def evaluation_item(self, db):
        return mommy.make('Evaluation_Item')

    def test_created(self, evaluation_item):
        assert evaluation_item.id is not None

    def test_default_value(self, evaluation_item):
        assert evaluation_item.value == 0
