#!/usr/bin/env python
"""
Script para verificar el entorno de Django activo.
Ejecutar con: python check_environment.py
"""

import os
import django
import sys

# Configurar el entorno
if os.environ.get('DJANGO_PRODUCTION') == 'True':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings_production')
    print("🌎 Usando configuración de PRODUCCIÓN (PythonAnywhere)")
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    print("🔧 Usando configuración de DESARROLLO (Local)")

# Inicializar Django
django.setup()

# Importar configuración
from django.conf import settings

# Mostrar información relevante
print("\n=== Información del Entorno ===")
print(f"• DEBUG: {'Activado' if settings.DEBUG else 'Desactivado'}")
print(f"• ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
print(f"• Database Engine: {settings.DATABASES['default']['ENGINE']}")
print(f"• Database Name: {settings.DATABASES['default']['NAME']}")
print(f"• Archivos estáticos: {getattr(settings, 'STATIC_ROOT', 'No configurado')}")
print(f"• Ruta de logs: {settings.LOGGING['handlers']['file']['filename']}")
print("\n=== Variables de Entorno ===")
print(f"• DJANGO_PRODUCTION: {os.environ.get('DJANGO_PRODUCTION', 'No configurado')}")
print(f"• SECRET_KEY configurada: {'Sí' if settings.SECRET_KEY else 'No'}")
print(f"• ANTHROPIC_API_KEY configurada: {'Sí' if getattr(settings, 'ANTHROPIC_API_KEY', None) else 'No'}")

print("\n✓ Verificación completada.")
