from pytest import mark, fixture

from ...forms import CategoryForm


class TestCategoryForm:
    @fixture
    def data(self):
        return {
            'title': 'Mobile',
            'description': 'Mobile interface',
        }

    def test_valid(self, data):
        form = CategoryForm(data)
        assert form.is_valid()

    def test_invalid(self, snapshot):
        data = {}
        form = CategoryForm(data)
        assert not form.is_valid()
        assert len(form.errors) == 2
        snapshot.assert_match(form.errors)

    def test_max(self, data, snapshot):
        data['title'] = 'X' * 51
        data['description'] = 'X' * 201
        form = CategoryForm(data)
        assert not form.is_valid()
        snapshot.assert_match(form.errors)

    @mark.skip
    def test_max_ptbr(self, data, snapshot, set_pt_br_language):
        data['title'] = 'X' * 51
        data['description'] = 'X' * 201
        form = CategoryForm(data)
        assert not form.is_valid()
        snapshot.assert_match(form.errors)
