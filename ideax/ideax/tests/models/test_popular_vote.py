from model_mommy import mommy
from pytest import fixture


class TestPopularVote:
    @fixture
    def popular_vote(self, db):
        return mommy.make('Popular_Vote')

    def test_created(self, popular_vote):
        assert popular_vote.id is not None
