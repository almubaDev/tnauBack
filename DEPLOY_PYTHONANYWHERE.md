# Guía de Despliegue para TarotNautica en PythonAnywhere

Esta guía te ayudará a desplegar el backend de TarotNautica en PythonAnywhere manteniendo un entorno de producción separado del entorno de desarrollo.

## 1. Preparación de Archivos

Los siguientes archivos han sido preparados para facilitar el despliegue:

- `core/settings_production.py`: Configuración específica para el entorno de producción
- `requirements-production.txt`: Dependencias necesarias para producción
- `core/wsgi.py`: Modificado para detectar entorno de producción

## 2. Configurar cuenta en PythonAnywhere

1. Regístrate en [PythonAnywhere](https://www.pythonanywhere.com/) si aún no tienes una cuenta
2. Crea una nueva aplicación web desde el dashboard:
   - Selecciona "Web" en el menú superior
   - Haz clic en "Add a new web app"
   - Selecciona "Manual configuration"
   - Selecciona Python 3.10 (o la versión disponible compatible con Django 4.2)

## 3. Subir el código

Existen varias formas de subir tu código:

### Opción 1: Git (recomendado)
```bash
# En tu consola de PythonAnywhere
$ cd ~
$ git clone <tu-repositorio-git>
```

### Opción 2: Zip
1. Comprime tu proyecto
2. Sube el archivo ZIP desde la página "Files" de PythonAnywhere
3. Descomprime el archivo en tu directorio home

## 4. Configurar el entorno virtual

```bash
# En la consola de PythonAnywhere
$ cd ~/tarotNautica/backend
$ python -m venv venv
$ source venv/bin/activate
$ pip install -r requirements-production.txt
```

## 5. Configurar base de datos

1. Ve a la sección "Databases" en PythonAnywhere
2. Crea una base de datos MySQL
3. Anota el nombre de usuario, contraseña y nombre de la base de datos
4. Actualiza `settings_production.py` con esa información

## 6. Configurar variables de entorno

Crea un archivo `.env` en el directorio ~/tarotNautica/backend:

```
SECRET_KEY=tu_clave_secreta_aqui
DJANGO_PRODUCTION=True
DB_PASSWORD=tu_contraseña_mysql
ANTHROPIC_API_KEY=tu_clave_api_anthropic
```

O configura estas variables en el archivo WSGI:

1. Ve a la pestaña "Web"
2. Desplázate hasta la sección "Code" y haz clic en el enlace WSGI
3. Añade estas líneas antes de la importación del wsgi:

```python
import os
os.environ['DJANGO_PRODUCTION'] = 'True'
os.environ['SECRET_KEY'] = 'tu_clave_secreta_aqui'
os.environ['DB_PASSWORD'] = 'tu_contraseña_mysql'
os.environ['ANTHROPIC_API_KEY'] = 'tu_clave_api_anthropic'
```

## 7. Configurar archivos estáticos

```bash
# En la consola de PythonAnywhere
$ cd ~/tarotNautica/backend
$ python manage.py collectstatic --settings=core.settings_production
```

## 8. Migrar la base de datos

```bash
# En la consola de PythonAnywhere
$ cd ~/tarotNautica/backend
$ python manage.py migrate --settings=core.settings_production
```

## 9. Configurar la app web

1. Ve a la pestaña "Web"
2. En la sección "Code":
   - Source code: /home/tusitio/tarotNautica/backend
   - Working directory: /home/tusitio/tarotNautica/backend
   - WSGI configuration file: /var/www/tusitio_pythonanywhere_com_wsgi.py

3. Edita el archivo WSGI para que se vea así:

```python
import os
import sys

# Añadir entorno de producción
os.environ['DJANGO_PRODUCTION'] = 'True'

# Añadir path al proyecto
path = '/home/tusitio/tarotNautica/backend'
if path not in sys.path:
    sys.path.append(path)

# Punto de entrada a la aplicación
from core.wsgi import application
```

4. En la sección "Static files":
   - URL: /static/
   - Directory: /home/tusitio/tarotNautica/backend/static

## 10. Reiniciar la aplicación

Haz clic en "Reload" en la parte superior de la página para reiniciar tu aplicación.

## Solución de problemas

- Si encuentras problemas, verifica los logs de error en la sección "Web" > "Logs"
- Asegúrate de que las rutas a los archivos estáticos sean correctas
- Verifica que todas las variables de entorno estén configuradas correctamente

## Actualización de la aplicación

Para actualizar tu aplicación después de hacer cambios:

```bash
# Si usas Git
$ cd ~/tarotNautica
$ git pull

# Luego actualiza la base de datos si es necesario
$ cd backend
$ source venv/bin/activate
$ python manage.py migrate --settings=core.settings_production

# Y finalmente reinicia la aplicación desde la interfaz web
