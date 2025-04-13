# load_tarot_readings.py
import os
import django

# Configurar entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# Importar después de configurar Django
from api.models import TipoTirada

# Datos de los tipos de tirada con límites y costos actualizados
TAROT_READINGS = [
    {
        "nombre": "Tirada Básica (Pasado-Presente-Futuro)",
        "tipo": "basica",
        "num_cartas": 3,
        "descripcion": "La tirada más clásica del tarot. Tres cartas que representan el pasado que ha influido en tu situación actual, las energías del presente, y el futuro que se está formando basado en el camino actual.",
        "costo_gemas": 3,
        "limite_mensual": 10,
        "layout_descripcion": "Tres cartas en línea horizontal. La carta de la izquierda representa el pasado, la del centro el presente, y la de la derecha el futuro."
    },
    {
        "nombre": "Tirada de Claridad",
        "tipo": "claridad",
        "num_cartas": 6,
        "descripcion": "Una tirada más profunda que ofrece una visión ampliada de tu situación. Examina la situación general, obstáculos, influencias conscientes e inconscientes, consejos, y el resultado potencial.",
        "costo_gemas": 5,
        "limite_mensual": 10,
        "layout_descripcion": "Seis cartas dispuestas en cruz. La primera carta en el centro representa la situación general. La segunda carta encima representa el obstáculo principal. La tercera carta a la derecha representa la influencia consciente. La cuarta carta a la izquierda representa la influencia inconsciente. La quinta carta debajo representa el consejo a seguir. La sexta carta en la parte superior representa el resultado potencial."
    },
    {
        "nombre": "Tirada Profunda",
        "tipo": "profunda",
        "num_cartas": 11,
        "descripcion": "La tirada más completa para situaciones complejas. Analiza la esencia del problema y explora los aspectos mentales, emocionales y materiales de la situación, así como su desarrollo potencial.",
        "costo_gemas": 7,
        "limite_mensual": 10,
        "layout_descripcion": "Once cartas dispuestas en forma de árbol. La primera carta en la base representa la esencia del problema. Las cartas 2-4 representan el plano mental (pensamiento personal, externo e ideal). Las cartas 5-7 representan el plano emocional (emociones personales, externas e ideales). Las cartas 8-10 representan el plano material (situación material personal, externa e ideal). La carta 11 en la cima representa el resultado final."
    }
]

def load_readings():
    # Limpiar base de datos existente (opcional)
    TipoTirada.objects.all().delete()
    
    # Cargar nuevos tipos de tirada
    for reading_data in TAROT_READINGS:
        TipoTirada.objects.create(**reading_data)
        print(f"Tipo de tirada creada: {reading_data['nombre']}")
    
    print(f"Total de tipos de tirada cargados: {TipoTirada.objects.count()}")

if __name__ == "__main__":
    load_readings()