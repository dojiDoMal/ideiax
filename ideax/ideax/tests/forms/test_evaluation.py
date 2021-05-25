from pytest import mark

from ...forms import EvaluationForm


class TestEvaluationForm:
    @mark.skip('is it impossible invalidate this form?')
    def test_invalid(self):
        form = EvaluationForm({})
        assert not form.is_valid()
