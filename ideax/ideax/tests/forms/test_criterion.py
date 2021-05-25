from pytest import mark, fixture

from ...forms import CriterionForm


class TestCriterionForm:
    @fixture
    def data(self):
        return {
            'description': 'Specials only',
            'peso': 5,
        }

    def test_invalid(self, snapshot):
        form = CriterionForm({})
        assert not form.is_valid()
        assert len(form.errors) == 2
        snapshot.assert_match(form.errors)

    def test_valid(self, db, data):
        form = CriterionForm(data)
        assert form.is_valid()

    @mark.skip
    def test_peso_minimum(self, db, data):
        data['peso'] = -1
        form = CriterionForm(data)
        assert not form.is_valid()

    @mark.skip
    def test_peso_maximum(self, db, data):
        data['peso'] = 999
        form = CriterionForm(data)
        assert not form.is_valid()
