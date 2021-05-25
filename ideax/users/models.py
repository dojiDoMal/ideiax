from enum import Enum
from django.db import models
from django.utils.translation import ugettext_lazy as _


class UserProfile(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.PROTECT)
    use_term_accept = models.NullBooleanField(default=False)
    acceptance_date = models.DateTimeField(null=True)
    ip = models.CharField(max_length=20, null=True)
    manager = models.NullBooleanField(default=False)

    def __str__(self):
        return self.user.username


class AuthType(Enum):
    LDAP = (1, _('LDAP'))
    # TODO: possibilitar a utilização quando for implementado
    # AD = (2, _('AD'))

    def __init__(self, id, description):
        self.id = id
        self.description = description

    @classmethod
    def choices(cls):
        return tuple((x.id, x.description) for x in cls)


class AuthConfiguration(models.Model):
    auth_type = models.PositiveSmallIntegerField(choices=AuthType.choices())
    host = models.CharField(max_length=50)
    bind_dn = models.CharField(max_length=100)
    bind_password = models.CharField(max_length=40)
    user_search_base = models.CharField(max_length=120)
    user_filter = models.CharField(max_length=100)
    active = models.BooleanField(default=True)
    configuration_date = models.DateTimeField(null=True)
    configuration_admin_ip = models.CharField(max_length=20, null=True)
    configuration_admin = models.CharField(max_length=40, null=True)
