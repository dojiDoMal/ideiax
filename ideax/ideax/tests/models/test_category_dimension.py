from django.db.utils import DataError

from model_mommy import mommy
from pytest import fixture, raises

from ...models import Category_Dimension


class TestCategoryDimension:
    @fixture
    def category_dimension(self, db):
        return mommy.make('Category_Dimension')

    def test_created(self, category_dimension):
        assert category_dimension.id is not None

    def test_str(self, category_dimension):
        category_dimension = mommy.make(Category_Dimension, description='Category')
        assert str(category_dimension) == 'Category'

    def test_max_description(self, db_vendor):
        if db_vendor != 'sqlite':
            with raises(DataError):
                mommy.make('Category_Dimension', description='X' * 201)
