from model_mommy import mommy
from pytest import fixture
from ...models import Dimension


class TestDimension:
    @fixture
    def dimension(self, db):
        return mommy.make('Dimension')

    def test_created(self, dimension):
        assert dimension.id is not None

    def test_str(self):
        dimension = Dimension(title='Dimension')
        assert str(dimension) == 'Dimension'
