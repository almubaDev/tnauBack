#api urls

from django.urls import path
from .views import (welcome, perfil_usuario, comprar_gemas, activar_suscripcion, 
                    usar_tirada, cancelar_suscripcion, listar_hechizos, listar_pociones,
                    comprar_hechizo, comprar_pocion, mis_hechizos, mis_pociones,
                    register_user, listar_cartas_tarot, detalle_carta_tarot,
                    listar_tipos_tirada, detalle_tipo_tirada, historial_tiradas,
                    detalle_tirada, realizar_tirada)

urlpatterns = [
    path('', welcome),
    path('registro/', register_user, name='register_user'),
    path('perfil/', perfil_usuario),
    path('comprar-gemas/', comprar_gemas),
    path('activar-suscripcion/', activar_suscripcion),
    path('cancelar-suscripcion/', cancelar_suscripcion),
    path('usar-tirada/', usar_tirada),
    path('hechizos/', listar_hechizos, name='listar_hechizos'),
    path('pociones/', listar_pociones, name='listar_pociones'),
    
    # Rutas para compras
    path('comprar-hechizo/', comprar_hechizo, name='comprar_hechizo'),
    path('comprar-pocion/', comprar_pocion, name='comprar_pocion'),
    path('mis-hechizos/', mis_hechizos, name='mis_hechizos'),
    path('mis-pociones/', mis_pociones, name='mis_pociones'),
    
    # Rutas para Tarot
    path('cartas-tarot/', listar_cartas_tarot, name='listar_cartas_tarot'),
    path('cartas-tarot/<int:carta_id>/', detalle_carta_tarot, name='detalle_carta_tarot'),
    path('listar-tipos-tirada/', listar_tipos_tirada, name='listar_tipos_tirada'),
    path('tipo-tirada/<int:tirada_id>/', detalle_tipo_tirada, name='detalle_tipo_tirada'),
    path('historial-tiradas/', historial_tiradas, name='historial_tiradas'),
    path('tirada/<int:tirada_id>/', detalle_tirada, name='detalle_tirada'),
    path('realizar-tirada/', realizar_tirada, name='realizar_tirada'),
]