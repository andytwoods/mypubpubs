from .base import *

INSTALLED_APPS += ["debug_toolbar", ]
MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware", ]

DEBUG = True

INTERNAL_IPS = [
    # ...
    "127.0.0.1",
    # ...
]

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
