import logging

from ipware import get_client_ip as get_client_ipware

PRIVATE_IPS_PREFIX = ('10.', '172.', '192.', )


def get_ip(request):
    client_ip, is_routable = get_client_ipware(request)
    if client_ip is None:
        # it's necessary LOG this information
        return request.META.get('REMOTE_ADDR')
    else:
        return client_ip


def get_client_ip(request):
    """get the client ip from the request
    """
    remote_address = request.META.get('REMOTE_ADDR')
    # set the default value of the ip to be the REMOTE_ADDR if available
    # else None
    ip = remote_address
    # try to get the first non-proxy ip (not a private ip) from the
    # HTTP_X_FORWARDED_FOR
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        proxies = x_forwarded_for.split(',')
        # remove the private ips from the beginning
        while (len(proxies) > 0 and proxies[0].startswith(PRIVATE_IPS_PREFIX)):
            proxies.pop(0)
        # take the first ip which is not a private one (of a proxy)
        if len(proxies) > 0:
            ip = proxies[0]

    return ip


# Creating log object
logger = logging.getLogger('audit_log')

def audit(username, ip_addr, operation, class_name, object_id):
    logger.info(
        '%(username)s|%(ip_addr)s|%(operation)s|%(class_name)s|%(object_id)s',
        {
            'username': username,
            'ip_addr': ip_addr,
            'operation': operation,
            'class_name': class_name,
            'object_id': object_id
        }
    )

def is_digit(val):
    try:
        return val.replace("-", "").isdigit()
    except:
        return False
