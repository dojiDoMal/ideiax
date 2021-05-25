from model_mommy import mommy
from pytest import fixture

from ....users.models import UserProfile
from ...forms import IdeaForm


class TestIdeaForm:
    @fixture
    def authors(self):
        # TODO: Perthaps queryset should have a default value
        return UserProfile.objects.all()

    @fixture
    def data(self, db):
        category = mommy.make('Category')
        return {
            'title': 'Super idea',
            'summary': 'It will change the entire world',
            'target': 'people around the world',
            'solution': 'all the problems',
            'oportunity': 'all the time',
            'category': category.id,
        }

    def test_invalid(self, authors, snapshot):
        form = IdeaForm({}, authors=authors)
        assert not form.is_valid()
        assert len(form.errors) == 6
        snapshot.assert_match(form.errors)

    def test_valid(self, authors, data):
        form = IdeaForm(data, authors=authors)
        assert form.is_valid()

    def test_max_length_textfields(self, authors, data):
        data['summary'] = 'X' * 141
        data['oportunity'] = 'X' * 2501
        data['solution'] = 'X' * 2501
        data['target'] = 'X' * 501
        form = IdeaForm(data, authors=authors)

        message = 'Ensure this value has at most {} characters (it has {}).'
        assert not form.is_valid()
        assert form.errors['summary'][0] == message.format(140, 141)
        assert form.errors['oportunity'][0] == message.format(2500, 2501)
        assert form.errors['solution'][0] == message.format(2500, 2501)
        assert form.errors['target'][0] == message.format(500, 501)
