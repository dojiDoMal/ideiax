from pytest import fixture, mark
from ..models import Idea
from model_mommy import mommy
from django.contrib.auth.models import User
from ..enums import NotificationType
from ..idea_notification import idea_notify_email, idea_send_notify, idea_send_email

@fixture
def setup(mocker):
    mocker.patch('django.core.mail.send_mail', return_value=False)
    mocker.patch('notifications.signals.notify', return_value=True)
    mocker.patch('django.dispatch.Signal', return_value=True)

@mark.django_db(transaction=False)
def test_send_email(mocker):

    idea = mocker.patch('ideax.ideax.models.Idea')
    user = mocker.patch('django.contrib.auth.models.User')

    idea_send_email(idea, user, NotificationType.COMMENT)

# @mark.django_db(transaction=False)
# def test_send_notify(mocker):

#     idea = mocker.patch('ideax.ideax.models.Idea')
#     user = mocker.patch('django.contrib.auth.models.User')

#     idea_send_notify(idea, user, NotificationType.COMMENT)