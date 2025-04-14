"""
Script to check and update TipoTirada limits
"""
import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from api.models import TipoTirada

# Define the tirada types and their new limits
tiradas = [
    {
        'nombre': 'Tirada Básica',
        'tipo': 'basica',
        'num_cartas': 3,
        'descripcion': 'Una tirada simple de 3 cartas que representa pasado, presente y futuro.',
        'costo_gemas': 3,  # Updated from 1
        'limite_mensual': 10,  # Updated from 100
        'layout_descripcion': 'Colocación de 3 cartas en fila horizontal'
    },
    {
        'nombre': 'Tirada de Claridad',
        'tipo': 'claridad',
        'num_cartas': 6,
        'descripcion': 'Una tirada de 6 cartas para obtener mayor claridad sobre una situación específica.',
        'costo_gemas': 5,  # Updated from 2
        'limite_mensual': 10,  # Updated from 50
        'layout_descripcion': 'Colocación de 6 cartas en cruz'
    },
    {
        'nombre': 'Tirada Profunda',
        'tipo': 'profunda',
        'num_cartas': 11,
        'descripcion': 'Una tirada completa de 11 cartas para un análisis profundo de tu situación.',
        'costo_gemas': 7,
        'limite_mensual': 10,  # Updated from 30
        'layout_descripcion': 'Colocación de 11 cartas en patrón complejo'
    }
]

def update_tipo_tiradas():
    """Check and update or create TipoTirada entries"""
    print("Updating TipoTirada limits...")
    
    # Check if we need to create or update
    count = TipoTirada.objects.count()
    print(f"Found {count} existing TipoTirada entries")
    
    # For each tirada type
    for tirada_data in tiradas:
        tipo = tirada_data['tipo']
        
        # Try to find existing entry
        try:
            tirada = TipoTirada.objects.get(tipo=tipo)
            print(f"Updating existing tirada: {tirada.nombre}")
            
            # Update fields
            tirada.nombre = tirada_data['nombre']
            tirada.num_cartas = tirada_data['num_cartas']
            tirada.descripcion = tirada_data['descripcion']
            tirada.costo_gemas = tirada_data['costo_gemas']
            tirada.limite_mensual = tirada_data['limite_mensual']
            tirada.layout_descripcion = tirada_data['layout_descripcion']
            tirada.save()
            
        except TipoTirada.DoesNotExist:
            # Create new entry
            print(f"Creating new tirada: {tirada_data['nombre']}")
            TipoTirada.objects.create(**tirada_data)
    
    print("TipoTirada entries updated successfully")
    print("\nCurrent TipoTirada entries:")
    for t in TipoTirada.objects.all():
        print(f"- {t.nombre} ({t.tipo}): limit = {t.limite_mensual}")

if __name__ == "__main__":
    update_tipo_tiradas()
