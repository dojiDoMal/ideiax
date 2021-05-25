from model_mommy import mommy
from pytest import raises

from ...models import Category_Image

from django.db.utils import DataError


class TestCategoryImage:
    def test_get_random_image_empty(self, db):
        category = mommy.make('Category')
        image = Category_Image.get_random_image(category)
        assert image is None

    def test_get_random_image(self, db):
        category = mommy.make('Category')
        images = [
            mommy.make('Category_Image', category=category)
            for i in range(3)
        ]
        image = Category_Image.get_random_image(category)
        assert image.category == category
        assert image in images

    def test_max_description(self, db_vendor):
        if db_vendor != 'sqlite':
            with raises(DataError):
                mommy.make('Category_Image', description='X' * 51)
