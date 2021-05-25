from django.core.files.uploadedfile import SimpleUploadedFile
from model_mommy import mommy
from pytest import fixture, mark
from ...forms import ChallengeForm


class TestChallengeForm:
    @fixture
    def data(self):
        mommy.make('Challenge')
        return {
            'title': 'Test Challenge Title',
            'summary': 'Test Challenge Summary',
            'requester': 'Test Challenge Requester',
            'description': 'Test Challenge Description',
            'discarted': False,
        }

    def test_max_description(self, db, data, test_image):
        data['description'] = 'X' * 2501
        form = ChallengeForm(data, files={
            'image': SimpleUploadedFile('favicon.png', test_image)
        })
        assert not form.is_valid()
        assert form.errors['description'] == [
            'Ensure this value has at most 2500 characters (it has 2501).',
        ]

    @mark.usefixtures('set_pt_br_language')
    def test_max_description_ptbr(self, db, data, test_image):
        data['description'] = 'X' * 2501
        form = ChallengeForm(data, files={
            'image': SimpleUploadedFile('favicon.png', test_image)
        })
        assert not form.is_valid()
        assert form.errors['description'] == [
            'Certifique-se de que o valor tenha no máximo 2500 caracteres (ele possui 2501).',
        ]

    def test_max_title(self, db, data, test_image):
        data['title'] = 'X' * 101
        form = ChallengeForm(data, files={
            'image': SimpleUploadedFile('favicon.png', test_image)
        })
        assert not form.is_valid()
        assert form.errors['title'] == [
            'Ensure this value has at most 100 characters (it has 101).',
        ]

    @mark.usefixtures('set_pt_br_language')
    def test_max_title_ptbr(self, db, data, test_image):
        data['title'] = 'X' * 101
        form = ChallengeForm(data, files={
            'image': SimpleUploadedFile('favicon.png', test_image)
        })
        assert not form.is_valid()
        assert form.errors['title'] == [
            'Certifique-se de que o valor tenha no máximo 100 caracteres (ele possui 101).',
        ]

    def test_max_summary(self, db, data, test_image):
        data['summary'] = 'X' * 141
        form = ChallengeForm(data, files={
            'image': SimpleUploadedFile('favicon.png', test_image)
        })
        assert not form.is_valid()
        assert form.errors['summary'] == [
            'Ensure this value has at most 140 characters (it has 141).',
        ]

    @mark.usefixtures('set_pt_br_language')
    def test_max_summary_ptbr(self, db, data, test_image):
        data['summary'] = 'X' * 141
        form = ChallengeForm(data, files={
            'image': SimpleUploadedFile('favicon.png', test_image)
        })
        assert not form.is_valid()
        assert form.errors['summary'] == [
            'Certifique-se de que o valor tenha no máximo 140 caracteres (ele possui 141).',
        ]

    def test_max_requester(self, db, data, test_image):
        data['requester'] = 'X' * 141
        form = ChallengeForm(data, files={
            'image': SimpleUploadedFile('favicon.png', test_image)
        })
        assert not form.is_valid()
        assert form.errors['requester'] == [
            'Ensure this value has at most 140 characters (it has 141).',
        ]

    @mark.usefixtures('set_pt_br_language')
    def test_max_requester_ptbr(self, db, data, test_image):
        data['requester'] = 'X' * 141
        form = ChallengeForm(data, files={
            'image': SimpleUploadedFile('favicon.png', test_image)
        })
        assert not form.is_valid()
        assert form.errors['requester'] == [
            'Certifique-se de que o valor tenha no máximo 140 caracteres (ele possui 141).',
        ]

    def test_invalid(self, snapshot):
        form = ChallengeForm({})
        assert not form.is_valid()

    def test_valid(self, db, test_image):
        category = mommy.make('Category')
        data = {
            'title': 'Documento Único',
            'description': 'Redução do número de documentos para os órgãos públicos',
            'summary': 'Redução ...',
            'limit_date': '2018-12-31',
            'init_date': '2018-01-01',
            'requester': 'Juracy Filho',
            'category': category.id,
            'height': '200',
            'width': '200',
            'x': '200',
            'y': '200',
        }

        form = ChallengeForm(data, files={
            'image': SimpleUploadedFile('favicon.png', test_image)
        })
        assert form.errors == {}
        assert form.is_valid()
