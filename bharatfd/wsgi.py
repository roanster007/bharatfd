"""
WSGI config for bharatfd project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from faqs.lib import initialize_services

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bharatfd.settings")

application = get_wsgi_application()

# Intitialize the cache services.
initialize_services()
