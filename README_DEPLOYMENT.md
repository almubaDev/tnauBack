# Despliegue de TarotNautica en PythonAnywhere

## Preparación de Entorno de Producción

Se han creado los siguientes archivos para preparar el backend para su despliegue en PythonAnywhere:

1. **`settings_production.py`**: Configuración específica para producción
   - Extiende la configuración base (`settings.py`)
   - Desactiva DEBUG
   - Configura ALLOWED_HOSTS para PythonAnywhere
   - Configura base de datos MySQL para PythonAnywhere
   - Establece la ruta de logs adecuada

2. **`requirements-production.txt`**: Dependencias mínimas para producción
   - Incluye solo los paquetes esenciales
   - Agrega mysqlclient para compatibilidad con MySQL
   - Reduce el tamaño del entorno virtual

3. **`check_environment.py`**: Script para verificar la configuración activa
   - Muestra qué entorno está en uso (desarrollo o producción)
   - Verifica la configuración de la base de datos
   - Comprueba las variables de entorno

4. **`deploy_to_pythonanywhere.sh`**: Guía de comandos para despliegue
   - Proporciona los pasos para configurar PythonAnywhere
   - Incluye comandos para la migración de la base de datos
   - No es para ejecución directa, sino como referencia

5. **`DEPLOY_PYTHONANYWHERE.md`**: Documentación detallada del proceso
   - Instrucciones paso a paso para el despliegue
   - Solución de problemas comunes
   - Guía para actualizar la aplicación

## Modificaciones al Código Existente

1. **`wsgi.py`**: Se ha modificado para detectar el entorno
   - Utiliza la variable `DJANGO_PRODUCTION` para determinar qué configuración usar
   - Funciona sin cambios tanto en desarrollo como en producción

## Cómo funciona

El sistema está configurado para que **no afecte** tu entorno de desarrollo:

- En desarrollo local: El código sigue utilizando `settings.py` y tu base de datos SQLite
- En PythonAnywhere: El sistema usará `settings_production.py` cuando se establezca la variable de entorno `DJANGO_PRODUCTION=True`

## Uso en Desarrollo (Local)

En tu entorno local, el backend funciona exactamente igual que antes:

```bash
# Ejecutar el servidor de desarrollo normalmente
python manage.py runserver

# Para probar las migraciones localmente
python manage.py migrate

# Para comprobar que estás en modo desarrollo
python check_environment.py
```

## Uso en Producción (PythonAnywhere)

En PythonAnywhere, deberás configurar la variable de entorno `DJANGO_PRODUCTION=True` y luego:

```bash
# Para ejecutar migraciones en producción
python manage.py migrate --settings=core.settings_production

# Para recolectar archivos estáticos en producción
python manage.py collectstatic --settings=core.settings_production

# Para comprobar que estás en modo producción
DJANGO_PRODUCTION=True python check_environment.py
```

## Pasos para el Despliegue

1. Sigue las instrucciones detalladas en `DEPLOY_PYTHONANYWHERE.md`
2. Utiliza los comandos de referencia en `deploy_to_pythonanywhere.sh`
3. Verifica tu entorno con `check_environment.py`

## Notas Importantes

- **Antes de desplegar:** Actualiza `settings_production.py` con tu dominio real de PythonAnywhere
- Configura las variables de entorno (`SECRET_KEY`, `DB_PASSWORD`, `ANTHROPIC_API_KEY`) 
- El WSGI está configurado para detectar automáticamente el entorno usando `DJANGO_PRODUCTION=True`
