from django.utils._os import safe_join
from django.utils.encoding import filepath_to_uri
from django.db import connection

from tenant_schemas.storage import TenantFileSystemStorage


class TenantFileSystemStorageIdeax(TenantFileSystemStorage):
    def url(self, name):
        if self.base_url is None:
            raise ValueError("This file is not accessible via a URL.")

        url = filepath_to_uri(name)

        if url is not None:
            url = url.lstrip('/')

        return safe_join(self.base_url, connection.tenant.domain_url + "/" + url)
