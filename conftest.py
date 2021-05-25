import logging

from django.core.management import call_command
from django.db import connection
from django.utils import translation
from pytest import fixture
from ideax.tenant.models import Client

pytest_plugins = [
    'ideax.tests.fixtures',
    'ideax.users.tests.fixtures',
    'ideax.ideax.tests.fixtures',
]


@fixture(scope='session', autouse=True)
def test_info(worker_id):
    # TODO: Search for a better way to run this code only once by node
    if worker_id in ('master', 'gw0'):
        logging.warn(f'Database vendor: {connection.vendor}')


@fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        tenant = Client(domain_url='testserver', schema_name='testserver', name='Ideia X', on_trial=False)
        tenant.save()
        call_command('loaddata', '../../../docker/initialdata.json')


@fixture(autouse=True)
def set_default_language():
    translation.activate('en')


@fixture
def db_vendor(db):
    return connection.vendor
