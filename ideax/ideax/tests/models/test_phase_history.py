from model_mommy import mommy
from pytest import fixture


class TestPhaseHistory:
    @fixture
    def phase_history(self, db):
        return mommy.make('Phase_History')

    def test_created(self, phase_history):
        assert phase_history.id is not None

    def test_previous_phase_positive_value(self, phase_history):
        assert phase_history.previous_phase >= 0
