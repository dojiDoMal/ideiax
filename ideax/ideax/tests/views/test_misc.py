import json

from datetime import datetime, timedelta
from itertools import product

from django.db.models import QuerySet

import pytz

from model_mommy import mommy

from ...views import get_authors, get_featured_challenges, get_term_of_user


class TestNonMiscView:
    """Test for non view functions in ideax.views (for refactor)"""
    def test_get_term_of_user_empty(self, rf, db):
        request = rf.get('/')
        response = get_term_of_user(request)
        assert response.status_code == 200
        assert json.loads(response.content) == {'term': 'No Term of Use found'}

    def test_get_term_of_user(self, rf, db):
        mommy.make('Use_Term', term='EULA Test', final_date=datetime.now(pytz.UTC) + timedelta(days=1))
        request = rf.get('/')
        response = get_term_of_user(request)
        assert response.status_code == 200
        assert json.loads(response.content) == {'term': 'EULA Test'}

    def test_get_featured_challenges_empty(self, db):
        response = get_featured_challenges()
        assert isinstance(response, QuerySet)
        assert response.count() == 0

    def test_get_featured_challenges(self, db):
        challenges = {
            (active, discarted): mommy.make('Challenge', active=active, discarted=discarted)
            for active, discarted in product((False, True), repeat=2)
        }
        response = get_featured_challenges()
        assert isinstance(response, QuerySet)
        assert response.count() == 1
        assert response.first() == challenges[(True, False)]

    def test_get_authors_empty(self, db):
        response = get_authors('test@gmail.com')
        assert isinstance(response, QuerySet)
        assert response.count() == 0

    def test_get_authors(self, db):
        staff_options = (False, True)
        # User e-mail cannot be null (refactor get_authors)
        email_options = ('', 'exclude@gmail.com', 'valid@gmail.com')

        authors = {
            (staff, email): mommy.make('UserProfile', user__is_staff=staff, user__email=email)
            for staff, email in product(staff_options, email_options)
        }
        response = get_authors('exclude@gmail.com')
        assert isinstance(response, QuerySet)
        assert response.count() == 1
        assert response.first() == authors[(False, 'valid@gmail.com')]
