from django.db.models.signals import post_save
from notifications.signals import notify
from .models import Popular_Vote, Idea, Evaluation_Item, Phase, Comment


def my_handler(sender, instance, created, **kwargs):
    notify.send(instance, verb='like')
    notify.send(instance, verb='evaluate')
    notify.send(instance, verb='phase')
    notify.send(instance, verb='comment')
    notify.send(instance, verb='author')


post_save.connect(my_handler, sender=Popular_Vote)
post_save.connect(my_handler, sender=Idea)
post_save.connect(my_handler, sender=Evaluation_Item)
post_save.connect(my_handler, sender=Phase)
post_save.connect(my_handler, sender=Comment)
