from ..models import UserProfile
from ..signals import check_user_profile
from pytest import mark


class TestSignals:
    @mark.skip
    def test_check_user_profile(self, django_user_model):
        user = django_user_model.objects.create_user(
            username='username',
            password='password'
        )

        assert UserProfile.objects.count() == 1
        check_user_profile(__name__, None, user)
        assert UserProfile.objects.count() == 2  # Criação de um UserProfile
        check_user_profile(__name__, None, user)
        assert UserProfile.objects.count() == 2  # UserProfile já existente
