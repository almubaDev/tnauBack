#api urls

from django.urls import path
from .views import (welcome, perfil_usuario, comprar_gemas, activar_suscripcion, 
                    usar_tirada, cancelar_suscripcion, listar_hechizos, listar_pociones,
                    comprar_hechizo, comprar_pocion, mis_hechizos, mis_pociones,
                    register_user, listar_cartas_tarot, detalle_carta_tarot,
                    listar_tipos_tirada, detalle_tipo_tirada, historial_tiradas,
                    detalle_tirada, realizar_tirada, crear_tirada, obtener_tirada,
                    create_paypal_payment, paypal_payment_webhook, create_paypal_subscription,
                    paypal_subscription_webhook)
from . import stripe_views

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
    path('tiradas/crear/', crear_tirada, name='crear_tirada'),
    path('tiradas/<int:tirada_id>/', obtener_tirada, name='obtener_tirada'),

    # Endpoints de Stripe
    path('crear-intent-pago/', stripe_views.create_payment_intent, name='crear-intent-pago'),
    path('crear-suscripcion/', stripe_views.create_subscription, name='crear-suscripcion'),
    path('cancelar-suscripcion/', stripe_views.cancel_subscription, name='cancelar-suscripcion'),
    path('stripe-webhook/', stripe_views.stripe_webhook, name='stripe-webhook'),

    # PayPal endpoints
    path('paypal/payment/create/', create_paypal_payment, name='create_paypal_payment'),
    path('paypal/payment/webhook/', paypal_payment_webhook, name='paypal_payment_webhook'),
    path('paypal/subscription/create/', create_paypal_subscription, name='create_paypal_subscription'),
    path('paypal/subscription/webhook/', paypal_subscription_webhook, name='paypal_subscription_webhook'),
]