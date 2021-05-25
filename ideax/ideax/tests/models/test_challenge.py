from model_mommy import mommy


class TestChallenge:
    def test_str(self, db):
        challenge = mommy.make('Challenge', title='Test challenge')
        assert str(challenge) == challenge.title
