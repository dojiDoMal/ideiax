from pytest import fixture, mark
from django.core.files.uploadedfile import SimpleUploadedFile
from model_mommy import mommy

from ...forms import CategoryImageForm


class TestCategoryImageForm:
    @fixture
    def data(self):
        category = mommy.make('Category')
        return {
            'description': 'Main image',
            'category': category.id,
        }

    @fixture
    def image(self, test_image):
        return SimpleUploadedFile('category.png', test_image)

    def test_invalid(self, snapshot):
        form = CategoryImageForm({})
        assert not form.is_valid()
        assert len(form.errors) == 3
        snapshot.assert_match(form.errors)

    def test_valid(self, db, data, image):
        form = CategoryImageForm(data, files={'image': image})
        assert form.is_valid()

    def test_max_description(self, db, data, image):
        data['description'] = 'X' * 51
        form = CategoryImageForm(data, files={'image': image})
        assert not form.is_valid()
        assert form.errors['description'] == [
            'Ensure this value has at most 50 characters (it has 51).',
        ]

    @mark.usefixtures('set_pt_br_language')
    def test_max_description_ptbr(self, db, data, image):
        data['description'] = 'X' * 51
        form = CategoryImageForm(data, files={'image': image})
        assert not form.is_valid()
        assert form.errors['description'] == [
            'Certifique-se de que o valor tenha no máximo 50 caracteres (ele possui 51).'
        ]
