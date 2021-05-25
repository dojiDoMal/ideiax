from ...forms import IdeaFormUpdate


class TestIdeaFormUpdate:
    def test_invalid(self, snapshot):
        form = IdeaFormUpdate({})
        assert not form.is_valid()
        assert len(form.errors) == 4
        snapshot.assert_match(form.errors)

    def test_valid(self, db):
        data = {
            'title': 'Super idea',
            'target': 'people around the world',
            'solution': 'all the problems',
            'oportunity': 'all the time',
        }
        form = IdeaFormUpdate(data)
        assert form.is_valid()
