from django.db.utils import IntegrityError

from pytest import fixture, raises

from ...models import UserProfile


class TestProfileModel:
    @fixture
    def user(self, django_user_model):
        return django_user_model.objects.create(username='someone', password='secret')

    def test_str(self, user):
        up = UserProfile(user=user)
        assert str(up) == 'someone'

    def test_user_related(self, user):
        UserProfile(user=user, ip='1.1.1.1')
        assert user.userprofile.ip == '1.1.1.1'

    def test_required(self, user):
        up = UserProfile.objects.create(user=user)

        assert up.id is not None
        assert up.use_term_accept is False
        assert up.manager is False
        assert up.acceptance_date is None
        assert up.user is user
        assert up.user.userprofile is up

    def test_uniqueness(self, user):
        """OneToOneField restriction"""
        UserProfile.objects.create(user=user)

        with raises(IntegrityError):
            UserProfile.objects.create(user=user)
