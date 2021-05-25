import ldap
import logging

from decouple import config
from django_auth_ldap.config import LDAPSearch

from ..django._core import AUTHENTICATION_BACKENDS


AUTHENTICATION_BACKENDS.append('django_auth_ldap.backend.LDAPBackend')
#AUTH_LDAP_SERVER_URI = config('AUTH_LDAP_SERVER_URI', default='')
#AUTH_LDAP_BIND_DN = config('AUTH_LDAP_BIND_DN', default='')
#AUTH_LDAP_BIND_PASSWORD = config('AUTH_LDAP_BIND_PASSWORD', default='')
AUTH_LDAP_GLOBAL_OPTIONS = {ldap.OPT_X_TLS_REQUIRE_CERT: ldap.OPT_X_TLS_NEVER}
AUTH_LDAP_START_TLS = config('AUTH_LDAP_START_TLS', default=0, cast=bool)
#AUTH_LDAP_USER_SEARCH = LDAPSearch(
#    config('AUTH_LDAP_USER_SEARCH', default='ou=users,dc=example,dc=com'),
#    ldap.SCOPE_SUBTREE, "(mail=%(user)s)")
AUTH_LDAP_USER_ATTR_MAP = {
    "first_name": "givenName",
    "last_name": "sn",
    "email": "mail"
}
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'ideax.users.backend.LDAPBackendByTenant',
]
AUTH_LDAP_PROFILE_ATTR_MAP = {
    "memberOf": "memberOf",
}


logger = logging.getLogger('django_auth_ldap')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)
