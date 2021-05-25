from model_mommy import mommy
from pytest import fixture


class TestComment:
    @fixture
    def comment(self, db):
        return mommy.make('Comment')

    def test_created(self, comment):
        assert comment.id is not None

    def test_comment_phase(self, comment):
        assert comment.comment_phase >= 0
