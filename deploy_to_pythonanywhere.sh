#!/bin/bash
# Script para ayudar con el despliegue en PythonAnywhere
# NOTA: Este script es solo una guía de referencia. NO ejecutarlo directamente sin revisar.
# Uso: Se recomienda copiar y pegar los comandos manualmente en la consola de PythonAnywhere.

echo "==================================================="
echo "  Guía de Comandos para Desplegar en PythonAnywhere"
echo "==================================================="
echo
echo "Este script NO debe ser ejecutado directamente."
echo "Es una referencia para los comandos que necesitas ejecutar en PythonAnywhere."
echo
echo "==== 1. Crear entorno virtual ===="
echo "cd ~/tarotNautica/backend"
echo "python -m venv venv"
echo "source venv/bin/activate"
echo
echo "==== 2. Instalar dependencias ===="
echo "pip install -r requirements-production.txt"
echo
echo "==== 3. Configurar variables de entorno ===="
echo "# Crear archivo .env o configurar en el archivo WSGI"
echo "export DJANGO_PRODUCTION=True"
echo "export SECRET_KEY=tu_clave_secreta_aqui"
echo "export DB_PASSWORD=tu_contraseña_mysql"
echo "export ANTHROPIC_API_KEY=tu_clave_api_anthropic"
echo
echo "==== 4. Recolectar archivos estáticos ===="
echo "python manage.py collectstatic --settings=core.settings_production --noinput"
echo
echo "==== 5. Migrar base de datos ===="
echo "python manage.py migrate --settings=core.settings_production"
echo
echo "==== 6. Crear superusuario (opcional) ===="
echo "python manage.py createsuperuser --settings=core.settings_production"
echo
echo "==== 7. Verificar entorno ===="
echo "python check_environment.py"
echo
echo "==== 8. No olvides personalizar settings_production.py ===="
echo "# Actualiza ALLOWED_HOSTS con tu dominio real"
echo "# Configura DATABASE con tus credenciales reales"
echo
echo "==== 9. Reiniciar aplicación web desde la interfaz de PythonAnywhere ===="
echo "# Haz clic en 'Reload' en la pestaña Web"
echo
echo "==================================================="
echo "Para más detalles, consulta DEPLOY_PYTHONANYWHERE.md"
echo "==================================================="
