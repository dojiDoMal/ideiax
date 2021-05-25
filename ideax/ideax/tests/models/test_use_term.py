from django.db.utils import DataError

from datetime import datetime
from django.utils import timezone
from pytest import raises, mark

from model_mommy import mommy

from ...models import Use_Term


class TestUseTerm:
    def test_is_past_due(self, db):
        use_term = mommy.make('Use_Term')
        assert not use_term.is_past_due

    def test_is_past_due_future(self, db):
        # TODO: Evaluate use of timezone
        use_term = mommy.make('Use_Term', final_date=timezone.make_aware(datetime(2099, 12, 31)))
        assert use_term.is_past_due

    def test_valid_date(self, db):
        use_term = mommy.make(
            'Use_Term',
            init_date=timezone.make_aware(datetime(2018, 1, 1)),
            final_date=timezone.make_aware(datetime(2018, 12, 31)),
        )
        assert not use_term.is_invalid_date()

    # Teste a seguir sempre vai falhar, pois django não aplica limite a textfields
    @mark.skip
    def test_max_length_term(self, db_vendor):
        if db_vendor != 'sqlite':
            with raises(DataError):
                mommy.make('Use_Term', term='X' * 12501)

    def test_invalid_date(self, db):
        use_term = mommy.make(
            'Use_Term',
            init_date=timezone.make_aware(datetime(2019, 1, 1)),
            final_date=timezone.make_aware(datetime(2018, 12, 31)),
        )
        assert use_term.is_invalid_date()


class TestUseTermManager:
    def test_get_active_empty(self, mocker):
        all = mocker.patch.object(Use_Term.objects, 'all')
        all.return_value = []
        assert not Use_Term.objects.get_active()

    def test_get_active_inactive(self, mocker):
        all = mocker.patch.object(Use_Term.objects, 'all')
        all.return_value = [mocker.Mock(is_past_due=False)]
        assert not Use_Term.objects.get_active()

    def test_get_active_active(self, mocker):
        all = mocker.patch.object(Use_Term.objects, 'all')
        all.return_value = [mocker.Mock(is_past_due=False), mocker.Mock(is_past_due=True)]
        assert Use_Term.objects.get_active()
