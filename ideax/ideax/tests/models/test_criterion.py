from model_mommy import mommy
from pytest import fixture


class TestCriterion:
    @fixture
    def criterion(self, db):
        return mommy.make('Criterion')

    def test_created(self, criterion):
        assert criterion.id is not None

    def test_str(self, db):
        criterion = mommy.make('Criterion', description='Test criterion')
        assert str(criterion) == criterion.description
