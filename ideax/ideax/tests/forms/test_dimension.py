from pytest import fixture, mark

from ...forms import DimensionForm


class TestDimensionForm:
    @fixture
    def data(self):
        return {
            'title': 'Mobile',
            'description': 'Mobile interface',
            'weight': 50,
            'init_date': '2018-02-01',
            'last_update': '2018-12-31',
            'active' : True
        }

    def test_valid(self, data):
        form = DimensionForm(data)
        assert form.is_valid()

    def test_invalid(self, snapshot):
        data = {}
        form = DimensionForm(data)
        assert not form.is_valid()
        assert len(form.errors) == 3
        snapshot.assert_match(form.errors)

    def test_max(self, data, snapshot):
        data['title'] = 'X' * 201
        data['description'] = 'X' * 501
        form = DimensionForm(data)
        assert not form.is_valid()
        snapshot.assert_match(form.errors)

    @mark.skip
    def test_max_ptbr(self, data, snapshot, set_pt_br_language):
        data['title'] = 'X' * 201
        data['description'] = 'X' * 501
        form = DimensionForm(data)
        assert not form.is_valid()
        snapshot.assert_match(form.errors)

    @mark.skip('TODO: Missing date range validation')
    def test_invalid_period(self, db, data):
        data['active'] = False
        form = DimensionForm(data)
        assert not form.is_valid()
