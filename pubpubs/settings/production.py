from .base import *

DEBUG = False

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True


ALLOWED_HOSTS = ['167.235.66.120', 'pubpub.social', '.pubpub.social', '0.0.0.0', 'puppub.social', ]

MIDDLEWARE.append("rollbar.contrib.django.middleware.RollbarNotifierMiddleware")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {"require_debug_false": {"()": "django.utils.log.RequireDebugFalse"}},
    "formatters": {
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(module)s "
            "%(process)d %(thread)d %(message)s"
        },
        'timestamp': {
            'format': '{asctime} {levelname} {message}',
            'style': '{',
        },
    },
    "handlers": {
        "mail_admins": {
            "level": "DEBUG",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
        },
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "local_logs": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "formatter": "timestamp",
                "filename": os.path.join(PARENT_DIR, "django.log"),
        },
        "rollbar": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            'access_token': '9e18a3b6fccf4cc7875bcb82975fda1e',
            "environment": "production",
            'root': BASE_DIR,
            'code_version': '1.0',
            "class": "rollbar.logger.RollbarHandler",
        },
    },
    "loggers": {
        "": {
            "handlers": ["local_logs", "rollbar"],
            "level": "ERROR",
            "propagate": True,
        },
        "huey": {
            "handlers": ["console"],
            "level": os.getenv("DJANGO_LOG_LEVEL", "DEBUG"),
            "propagate": False,
        },
        "django.request": {
            "handlers": [
                "mail_admins",
            ],
            "level": "ERROR",
            "propagate": True,
        },

        # "django.security.DisallowedHost": {
        #     "level": "CRITICAL",
        #     "handlers": [
        #         "mail_admins",
        #     ],
        #     "propagate": False,
        # },
    },
}

# following advice here https://adamj.eu/tech/2019/04/10/how-to-score-a+-for-security-headers-on-your-django-website/
SECURE_BROWSER_XSS_FILTER = True
SECURE_HSTS_SECONDS = 30 # slowly ramp this up
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
WHITENOISE_MANIFEST_STRICT = False


# SERVER_EMAIL = DEFAULT_FROM_EMAIL  # ditto (default from-email for Django errors)

EMAIL_BACKEND = "anymail.backends.sendgrid.EmailBackend"
ANYMAIL = {
    "SENDGRID_API_KEY": env("SENDGRID_API_KEY"),
}
