from .base import *
from config import *

INSTALLED_APPS += [
]

DEBUG = False

ALLOWED_HOSTS = ['localhost', '64.227.25.145', 'spritesanddice.com', 'www.spritesanddice.com']

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

try:
    from .local import *
except ImportError:
    pass
