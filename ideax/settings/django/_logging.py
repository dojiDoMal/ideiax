import os

from ._core import BASE_DIR


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'audit': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'audit.log'),
            'maxBytes': 1024*1024*5,  # 5MB
            'backupCount': 0,
            'formatter': 'audit'
        }
    },
    'formatters': {
        'audit': {
            'format': 'AUDIT|%(asctime)s|%(message)s'
        }
    },
    'loggers': {
        'audit_log': {
            'handlers': ['audit'],
            'level': 'INFO',
            'propagate': True
        }
    }
}
