"""
Configuración de producción para PythonAnywhere
Este archivo extiende la configuración base pero sobrescribe
los valores necesarios para el entorno de producción.
"""

from .settings import *
import os

# Seguridad para producción
DEBUG = False

# Asegúrate de incluir tu dominio de PythonAnywhere aquí
ALLOWED_HOSTS = ['tusitio.pythonanywhere.com']  # Reemplaza 'tusitio' con tu nombre de usuario

# Configuración estática para PythonAnywhere
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# Configuración de base de datos
# Si usas MySQL en PythonAnywhere:
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'tusitio$tarotnautica',  # Reemplaza 'tusitio' con tu nombre de usuario
        'USER': 'tusitio',  # Reemplaza con tu nombre de usuario
        'PASSWORD': os.getenv('DB_PASSWORD', ''),  # Configura esto en la consola de PythonAnywhere
        'HOST': 'tusitio.mysql.pythonanywhere-services.com',  # Reemplaza 'tusitio' con tu nombre de usuario
        'PORT': '3306',
    }
}

# Ruta de log que funciona en PythonAnywhere
LOGGING['handlers']['file']['filename'] = '/var/log/tarotnautica_api.log'

# Si necesitas configurar cualquier otra variable específica de producción, hazlo aquí
