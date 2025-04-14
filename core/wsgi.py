"""
WSGI config for core project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
import sys

# Agregar la ruta del proyecto al path de Python
# path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# if path not in sys.path:
#     sys.path.append(path)

from django.core.wsgi import get_wsgi_application

# Determinar el entorno por una variable de entorno
is_production = os.environ.get('DJANGO_PRODUCTION', '') == 'True'
settings_module = 'core.settings_production' if is_production else 'core.settings'

os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)

application = get_wsgi_application()
