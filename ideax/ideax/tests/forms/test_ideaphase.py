from pytest import fixture

from ...forms import IdeaPhaseForm


class TestIdeaPhaseForm:
    @fixture
    def data(self):
        return {
            'name': 'Phase',
            'description': 'Phase description',
            'order': '1',
        }

    def test_invalid(self, snapshot):
        form = IdeaPhaseForm({})
        assert not form.is_valid()
        assert len(form.errors) == 2
        snapshot.assert_match(form.errors)

    def test_valid(self, db, data):
        form = IdeaPhaseForm(data)
        assert form.is_valid()

    def test_order_minimum(self, db, data):
        data['order'] = -1
        form = IdeaPhaseForm(data)
        assert not form.is_valid()
