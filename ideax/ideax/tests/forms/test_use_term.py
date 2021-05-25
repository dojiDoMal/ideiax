from pytest import fixture, mark

from ...forms import UseTermForm


class TestUseTermForm:
    @fixture
    def data(self):
        return {
            'term': 'EULA... Do you agree?',
            'init_date': '2018-02-01',
            'final_date': '2018-12-31',
        }

    def test_invalid(self, snapshot):
        form = UseTermForm({})
        assert not form.is_valid()
        assert len(form.errors) == 3
        snapshot.assert_match(form.errors)

    def test_valid(self, db, data):
        form = UseTermForm(data)
        assert form.is_valid()

    @mark.skip('TODO: Missing date range validation')
    def test_invalid_period(self, db, data):
        data['final_date'] = '2017-12-31'
        form = UseTermForm(data)
        assert not form.is_valid()
