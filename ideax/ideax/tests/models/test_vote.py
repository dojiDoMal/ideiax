from model_mommy import mommy
from pytest import fixture


class TestVote:
    @fixture
    def vote(self, db):
        return mommy.make('Vote')

    def test_created(self, vote):
        assert vote.id is not None
