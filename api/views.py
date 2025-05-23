from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import (UserProfile, Hechizo, Pocion, CompraHechizo, CompraPocion,
                     CartaTarot, TipoTirada, TiradaRealizada, CartaEnTirada,
                     PayPalPayment, PayPalSubscription)
from .subscription_handler import reset_subscription_benefits
from .serializers import (
    UserProfileSerializer, HechizoSerializer, PocionSerializer,
    UserSerializer, CompraHechizoSerializer, CompraPocionSerializer,
    CartaTarotSerializer, TipoTiradaSerializer, TiradaRealizadaSerializer, 
    CartaEnTiradaSerializer, CrearTiradaSerializer, PayPalPaymentSerializer,
    PayPalSubscriptionSerializer
)
from rest_framework_simplejwt.views import TokenObtainPairView
from .custom_token import CustomTokenObtainPairSerializer
import random
import os
import anthropic
import logging
from django.conf import settings
import requests
import base64
import json
from django.core.cache import cache

# Configurar logging
logger = logging.getLogger(__name__)

def get_paypal_config():
    """Get PayPal configuration"""
    return {
        'client_id': settings.PAYPAL_CLIENT_ID,
        'client_secret': settings.PAYPAL_CLIENT_SECRET,
        'mode': 'sandbox' if settings.DEBUG else 'live',
        'api_base': 'https://api-m.sandbox.paypal.com' if settings.DEBUG else 'https://api-m.paypal.com'
    }

def get_paypal_access_token():
    """Get PayPal OAuth access token"""
    token = cache.get('paypal_access_token')
    if token:
        return token

    config = get_paypal_config()
    auth = base64.b64encode(f"{config['client_id']}:{config['client_secret']}".encode()).decode()
    headers = {
        'Authorization': f'Basic {auth}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {'grant_type': 'client_credentials'}
    
    response = requests.post(
        f'{config["api_base"]}/v1/oauth2/token',
        headers=headers,
        data=data
    )
    
    if response.status_code == 200:
        token = response.json()['access_token']
        cache.set('paypal_access_token', token, 60 * 60 * 7)
        return token
    
    raise Exception('Failed to get PayPal access token')

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    
@api_view(['GET'])
def welcome(request):
    return Response({"message": "Bienvenido a Tarotnautica"})

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        # UserProfile se crea automáticamente gracias a la señal post_save
        return Response({
            "status": "success",
            "message": "Usuario registrado correctamente",
            "email": user.email
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def perfil_usuario(request):
    perfil = UserProfile.objects.get(user=request.user)
    serializer = UserProfileSerializer(perfil)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def activar_suscripcion(request):
    profile = request.user.profile
    was_subscribed = profile.tiene_suscripcion
    profile.tiene_suscripcion = True
    
    # Reset tiradas and add bonus gemas when subscribing
    if not was_subscribed:
        profile = reset_subscription_benefits(profile)
    else:
        profile.save()
        
    return Response({
        "status": "ok", 
        "suscripcion": True,
        "gemas": profile.gemas,
        "tiradas_reset": not was_subscribed
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancelar_suscripcion(request):
    profile = request.user.profile
    profile.tiene_suscripcion = False
    profile.save()
    return Response({"status": "ok", "suscripcion": False})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def comprar_gemas(request):
    profile = request.user.profile
    cantidad = request.data.get("cantidad", 0)

    try:
        cantidad = int(cantidad)
        if cantidad <= 0:
            return Response({"error": "Cantidad inválida"}, status=400)

        profile.gemas += cantidad
        profile.save()
        return Response({"status": "ok", "gemas": profile.gemas})
    except:
        return Response({"error": "Error al procesar compra"}, status=500)


def validar_tirada(profile, tipo):
    profile.reset_tiradas_mensuales()

    limites = {
        "basica": (profile.tiradas_basicas_usadas, 100, 1),
        "claridad": (profile.tiradas_claridad_usadas, 50, 2),
        "profunda": (profile.tiradas_profundas_usadas, 30, 7),
    }

    usadas, limite, costo_gemas = limites.get(tipo)

    if profile.tiene_suscripcion and usadas < limite:
        # Puede usar gratis
        if tipo == "basica":
            profile.tiradas_basicas_usadas += 1
        elif tipo == "claridad":
            profile.tiradas_claridad_usadas += 1
        elif tipo == "profunda":
            profile.tiradas_profundas_usadas += 1
        profile.save()
        return True, "OK - suscripción", 0

    if profile.gemas >= costo_gemas:
        profile.gemas -= costo_gemas
        profile.save()
        return True, "OK - usando gemas", costo_gemas

    return False, "No tienes suficientes gemas o tiradas disponibles", 0


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def usar_tirada(request):
    tipo = request.data.get("tipo")  # 'basica', 'claridad', 'profunda'
    profile = request.user.profile

    valido, mensaje, costo = validar_tirada(profile, tipo)

    if valido:
        return Response({
            "status": "ok",
            "mensaje": mensaje,
            "gemas_restantes": profile.gemas
        })
    else:
        return Response({"error": mensaje}, status=400)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_hechizos(request):
    categoria = request.query_params.get('categoria', None)
    hechizos = Hechizo.objects.filter(activo=True)
    if categoria:
        hechizos = hechizos.filter(categoria=categoria)
    serializer = HechizoSerializer(hechizos, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_pociones(request):
    categoria = request.query_params.get('categoria', None)
    pociones = Pocion.objects.filter(activo=True)
    if categoria:
        pociones = pociones.filter(categoria=categoria)
    serializer = PocionSerializer(pociones, many=True)
    return Response(serializer.data)

# Nuevos endpoints para compras
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def comprar_hechizo(request):
    try:
        hechizo_id = request.data.get('hechizo_id')
        hechizo = Hechizo.objects.get(id=hechizo_id, activo=True)
        
        # Verificar si ya lo compró
        if CompraHechizo.objects.filter(user=request.user, hechizo=hechizo).exists():
            return Response({"status": "ya_comprado", "mensaje": "Ya has comprado este hechizo"})
        
        # Verificar gemas suficientes
        profile = request.user.profile
        if profile.gemas < hechizo.precio_gemas:
            return Response(
                {"status": "error", "mensaje": "No tienes suficientes gemas"}, 
                status=400
            )
        
        # Descontar gemas
        profile.gemas -= hechizo.precio_gemas
        profile.save()
        
        # Registrar compra
        CompraHechizo.objects.create(user=request.user, hechizo=hechizo)
        
        return Response({
            "status": "ok", 
            "mensaje": "Hechizo comprado exitosamente",
            "gemas_restantes": profile.gemas
        })
    
    except Hechizo.DoesNotExist:
        return Response({"status": "error", "mensaje": "Hechizo no encontrado"}, status=404)
    except Exception as e:
        return Response({"status": "error", "mensaje": str(e)}, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def comprar_pocion(request):
    try:
        pocion_id = request.data.get('pocion_id')
        pocion = Pocion.objects.get(id=pocion_id, activo=True)
        
        # Verificar si ya lo compró
        if CompraPocion.objects.filter(user=request.user, pocion=pocion).exists():
            return Response({"status": "ya_comprado", "mensaje": "Ya has comprado esta poción"})
        
        # Verificar suscripción
        profile = request.user.profile
        if not profile.tiene_suscripcion:
            return Response(
                {"status": "error", "mensaje": "Necesitas suscripción para comprar pociones"}, 
                status=400
            )
            
        # Verificar gemas suficientes
        if profile.gemas < pocion.precio_gemas:
            return Response(
                {"status": "error", "mensaje": "No tienes suficientes gemas"}, 
                status=400
            )
        
        # Descontar gemas
        profile.gemas -= pocion.precio_gemas
        profile.save()
        
        # Registrar compra
        CompraPocion.objects.create(user=request.user, pocion=pocion)
        
        return Response({
            "status": "ok", 
            "mensaje": "Poción comprada exitosamente",
            "gemas_restantes": profile.gemas
        })
    
    except Pocion.DoesNotExist:
        return Response({"status": "error", "mensaje": "Poción no encontrada"}, status=404)
    except Exception as e:
        return Response({"status": "error", "mensaje": str(e)}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mis_hechizos(request):
    compras = CompraHechizo.objects.filter(user=request.user)
    hechizos_ids = compras.values_list('hechizo_id', flat=True)
    return Response({
        "hechizos_comprados": list(hechizos_ids)
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mis_pociones(request):
    compras = CompraPocion.objects.filter(user=request.user)
    pociones_ids = compras.values_list('pocion_id', flat=True)
    return Response({
        "pociones_compradas": list(pociones_ids)
    })
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_cartas_tarot(request):
    """Listar todas las cartas de tarot disponibles"""
    cartas = CartaTarot.objects.all()
    serializer = CartaTarotSerializer(cartas, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def detalle_carta_tarot(request, carta_id):
    """Ver detalle de una carta específica"""
    try:
        carta = CartaTarot.objects.get(id=carta_id)
        serializer = CartaTarotSerializer(carta)
        return Response(serializer.data)
    except CartaTarot.DoesNotExist:
        return Response({"error": "Carta no encontrada"}, status=404)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_tipos_tirada(request):
    """Listar todos los tipos de tirada disponibles"""
    tiradas = TipoTirada.objects.all()
    serializer = TipoTiradaSerializer(tiradas, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def detalle_tipo_tirada(request, tirada_id):
    """Ver detalle de un tipo de tirada específico"""
    try:
        tirada = TipoTirada.objects.get(id=tirada_id)
        serializer = TipoTiradaSerializer(tirada)
        return Response(serializer.data)
    except TipoTirada.DoesNotExist:
        return Response({"error": "Tipo de tirada no encontrado"}, status=404)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def historial_tiradas(request):
    """Ver historial de tiradas del usuario"""
    tiradas = TiradaRealizada.objects.filter(user=request.user).order_by('-fecha')
    serializer = TiradaRealizadaSerializer(tiradas, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def detalle_tirada(request, tirada_id):
    """Ver detalle de una tirada específica"""
    try:
        tirada = TiradaRealizada.objects.get(id=tirada_id, user=request.user)
        serializer = TiradaRealizadaSerializer(tirada)
        return Response(serializer.data)
    except TiradaRealizada.DoesNotExist:
        return Response({"error": "Tirada no encontrada"}, status=404)

def validar_puede_hacer_tirada(user, tipo_tirada):
    """
    Verifica si el usuario puede realizar una tirada:
    1. Si tiene suscripción, verifica los límites mensuales
    2. Si no tiene suscripción, descuenta gemas
    
    Retorna (puede_hacer_tirada, mensaje, costo_gemas)
    """
    profile = user.profile
    profile.reset_tiradas_mensuales()  # Resetear contadores si cambió el mes
    
    # Determinar límites según tipo de tirada
    if tipo_tirada.tipo == 'basica':
        tiradas_usadas = profile.tiradas_basicas_usadas
        campo_actualizar = 'tiradas_basicas_usadas'
    elif tipo_tirada.tipo == 'claridad':
        tiradas_usadas = profile.tiradas_claridad_usadas
        campo_actualizar = 'tiradas_claridad_usadas'
    elif tipo_tirada.tipo == 'profunda':
        tiradas_usadas = profile.tiradas_profundas_usadas
        campo_actualizar = 'tiradas_profundas_usadas'
    else:
        return False, "Tipo de tirada no válido", 0
    
    # Si tiene suscripción y no ha excedido límites mensuales
    if profile.tiene_suscripcion and tiradas_usadas < tipo_tirada.limite_mensual:
        setattr(profile, campo_actualizar, tiradas_usadas + 1)
        profile.save()
        return True, "Tirada incluida en suscripción", 0
    
    # Si no tiene suscripción o ha excedido límites, verificar gemas
    costo_gemas = tipo_tirada.costo_gemas
    if profile.gemas >= costo_gemas:
        profile.gemas -= costo_gemas
        profile.save()
        return True, f"Tirada realizada (costo: {costo_gemas} gemas)", costo_gemas
    
    return False, f"No tienes suficientes gemas para esta tirada. Necesitas {costo_gemas} gemas.", 0

def obtener_interpretacion_tirada(tirada, cartas_en_tirada):
    """
    Genera interpretación usando Anthropic API con manejo de errores mejorado
    """
    try:
        # Obtener API key directamente de las variables de entorno
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        
        if not api_key:
            logger.error("API key no encontrada en variables de entorno")
            return generar_interpretacion_fallback(tirada)
            
        # Preparar los datos de las cartas
        cartas_texto = []
        for carta in cartas_en_tirada:
            estado = "invertida" if carta.invertida else "normal"
            significado = carta.carta.significado_invertido if carta.invertida else carta.carta.significado_normal
            cartas_texto.append(f"Carta {carta.posicion}: {carta.carta.nombre} ({estado}) - {significado[:150]}...")
        
        cartas_info = "\n".join(cartas_texto)
        
        # Usar requests directamente para mayor control (más estable que el SDK en algunos entornos)
        import requests
        
        headers = {
            "x-api-key": api_key,
            "content-type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        data = {
            "model": "claude-3-5-sonnet-20240620",
            "max_tokens": 1000,
            "temperature": 0.7,
            "system": "Eres un experto tarotista que proporciona interpretaciones místicas pero prácticas.",
            "messages": [
                {
                    "role": "user", 
                    "content": f"""Interpreta esta tirada de tarot para la pregunta: "{tirada.pregunta}"
                    
                    Tipo de tirada: {tirada.tipo_tirada.nombre}
                    
                    Cartas:
                    {cartas_info}
                    
                    Da una interpretación completa, esotérica y mística pero práctica, relacionando las cartas entre sí y respondiendo a la pregunta. Usa genere neutral para referirte al consultante ya que no sabemos si es hombre o mujer"""
                }
            ]
        }
        
        # Hacer la solicitud con un timeout generoso
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=data,
            timeout=30  # 30 segundos de timeout
        )
        
        # Verificar si la respuesta fue exitosa
        if response.status_code == 200:
            resultado = response.json()
            interpretacion = resultado.get("content", [{}])[0].get("text", "")
            if interpretacion:
                return interpretacion
                
        # Si llegamos aquí, hubo algún problema con la respuesta
        logger.error(f"Error API Anthropic: {response.status_code} - {response.text}")
        return generar_interpretacion_fallback(tirada)
        
    except Exception as e:
        # Capturar y registrar cualquier excepción
        logger.error(f"Error en obtener_interpretacion_tirada: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return generar_interpretacion_fallback(tirada)

def generar_interpretacion_fallback(tirada):
    """
    Genera una interpretación de respaldo cuando hay problemas con la API.
    Esta función proporciona una respuesta mística general que parece una interpretación real.
    
    Args:
        tirada: Objeto TiradaRealizada
    
    Returns:
        str: Interpretación de respaldo
    """
    nombre_tirada = tirada.tipo_tirada.nombre if hasattr(tirada, 'tipo_tirada') and tirada.tipo_tirada else "del tarot"
    pregunta = tirada.pregunta if tirada.pregunta else "tu consulta"
    
    interpretacion = f"""
    Al contemplar tu tirada {nombre_tirada} sobre "{pregunta}", 
    percibo energías entrelazadas que revelan aspectos importantes de tu situación actual.
    
    Las cartas han acudido a ti en este momento específico por una razón. No es casualidad, 
    sino causalidad mística que conecta tu esencia con los arquetipos universales representados en el tarot.
    
    La disposición actual sugiere que te encuentras en un punto de transición, donde el pasado 
    ejerce su influencia sobre tu presente, mientras que el futuro se despliega según las energías 
    que estás cultivando ahora.
    
    Veo un patrón de elementos contrastantes: luces y sombras, desafíos y oportunidades, 
    que te invitan a encontrar el equilibrio en medio de las polaridades de la existencia.
    
    Las cartas revelan que parte de la respuesta que buscas ya está en tu interior, 
    pero quizás no has reconocido plenamente su presencia o significado. 
    La sabiduría del tarot te anima a conectar con tu intuición y escuchar esa voz interior.
    
    El consejo principal que emerge de esta tirada es permanecer centrado mientras 
    navegas por los cambios que se presentan. La adaptabilidad y la consciencia 
    serán tus mejores aliadas en el camino que se despliega ante ti.
    
    Recuerda que las cartas no determinan un destino inmutable, sino que iluminan 
    potenciales y tendencias energéticas que pueden ser transformadas mediante 
    tus decisiones y tu nivel de consciencia.
    
    Este es un momento para confiar en el proceso de la vida, sabiendo que cada experiencia, 
    sea desafiante o placentera, contribuye a tu crecimiento y evolución espiritual.
    """
    
    return interpretacion

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def realizar_tirada(request):
    """Realizar una nueva tirada de tarot"""
    serializer = CrearTiradaSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)
    
    tipo_tirada = serializer.validated_data['tipo_tirada']
    pregunta = serializer.validated_data['pregunta']
    
    # Verificar si el usuario puede realizar esta tirada
    puede_hacer_tirada, mensaje, costo = validar_puede_hacer_tirada(request.user, tipo_tirada)
    
    if not puede_hacer_tirada:
        return Response({"error": mensaje}, status=400)
    
    # Seleccionar cartas aleatorias
    cartas = list(CartaTarot.objects.all())
    if len(cartas) < tipo_tirada.num_cartas:
        return Response({"error": "No hay suficientes cartas registradas para este tipo de tirada"}, status=400)
    
    cartas_seleccionadas = random.sample(cartas, tipo_tirada.num_cartas)
    
    # Crear la tirada
    tirada = TiradaRealizada.objects.create(
        user=request.user,
        tipo_tirada=tipo_tirada,
        pregunta=pregunta,
        interpretacion=""  # La interpretación se añadirá después
    )
    
    # Crear las cartas en la tirada
    cartas_en_tirada = []
    for i, carta in enumerate(cartas_seleccionadas):
        # 50% de probabilidad de que la carta esté invertida
        invertida = random.choice([True, False])
        
        carta_tirada = CartaEnTirada.objects.create(
            tirada=tirada,
            carta=carta,
            posicion=i+1,
            invertida=invertida
        )
        cartas_en_tirada.append(carta_tirada)
    
    # Obtener interpretación usando la función mejorada con Anthropic
    interpretacion = obtener_interpretacion_tirada(tirada, cartas_en_tirada)
    tirada.interpretacion = interpretacion
    tirada.save()
    
    # Devolver resultado
    serializer = TiradaRealizadaSerializer(tirada)
    return Response({
        "mensaje": mensaje,
        "costo_gemas": costo,
        "tirada": serializer.data
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_paypal_payment(request):
    try:
        amount = request.data.get('amount')
        gems_amount = request.data.get('gems_amount')
        
        if not amount or not gems_amount:
            return Response({
                'error': 'Amount and gems_amount are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create PayPal order
        access_token = get_paypal_access_token()
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        order_data = {
            'intent': 'CAPTURE',
            'purchase_units': [{
                'amount': {
                    'currency_code': 'USD',
                    'value': str(amount)
                },
                'description': f'Purchase {gems_amount} gems in TarotNautica'
            }],
            'application_context': {
                'return_url': settings.PAYPAL_RETURN_URL,
                'cancel_url': settings.PAYPAL_CANCEL_URL
            }
        }
        
        response = requests.post(
            f'{PAYPAL_API_BASE}/v2/checkout/orders',
            headers=headers,
            json=order_data
        )
        
        if response.status_code != 201:
            return Response({
                'error': 'Failed to create PayPal order'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        order_response = response.json()
        
        # Create local payment record
        payment = PayPalPayment.objects.create(
            user=request.user,
            amount=amount,
            currency='USD',
            status='PENDING',
            payment_type='GEMS',
            gems_amount=gems_amount,
            order_id=order_response['id']
        )
        
        serializer = PayPalPaymentSerializer(payment)
        return Response({
            **serializer.data,
            'order_id': order_response['id'],
            'links': order_response['links']
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f'Error creating PayPal payment: {str(e)}')
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def paypal_payment_webhook(request):
    try:
        # Verify webhook signature
        webhook_id = settings.PAYPAL_WEBHOOK_ID
        headers = {
            'Authorization': f'Bearer {get_paypal_access_token()}',
            'Content-Type': 'application/json'
        }
        
        verification_data = {
            'auth_algo': request.headers.get('PAYPAL-AUTH-ALGO'),
            'cert_url': request.headers.get('PAYPAL-CERT-URL'),
            'transmission_id': request.headers.get('PAYPAL-TRANSMISSION-ID'),
            'transmission_sig': request.headers.get('PAYPAL-TRANSMISSION-SIG'),
            'transmission_time': request.headers.get('PAYPAL-TRANSMISSION-TIME'),
            'webhook_id': webhook_id,
            'webhook_event': request.data
        }
        
        verify_response = requests.post(
            f'{PAYPAL_API_BASE}/v1/notifications/verify-webhook-signature',
            headers=headers,
            json=verification_data
        )
        
        if verify_response.status_code != 200 or verify_response.json()['verification_status'] != 'SUCCESS':
            return Response({
                'error': 'Invalid webhook signature'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Process webhook
        event_type = request.data.get('event_type')
        resource = request.data.get('resource', {})
        order_id = resource.get('id')
        
        if not order_id:
            return Response({
                'error': 'Order ID not found in webhook'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        payment = PayPalPayment.objects.get(order_id=order_id)
        
        if event_type == 'CHECKOUT.ORDER.APPROVED':
            payment.status = 'COMPLETED'
            payment.save()
            
            # Add gems to user's account
            user_profile = UserProfile.objects.get(user=payment.user)
            user_profile.gemas += payment.gems_amount
            user_profile.save()
            
            logger.info(f'Added {payment.gems_amount} gems to user {payment.user.id}')
        
        serializer = PayPalPaymentSerializer(payment)
        return Response(serializer.data)
        
    except PayPalPayment.DoesNotExist:
        return Response({
            'error': 'Payment not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f'Error processing PayPal webhook: {str(e)}')
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_paypal_subscription(request):
    try:
        # Create PayPal subscription
        access_token = get_paypal_access_token()
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
            'Prefer': 'return=representation'
        }
        
        subscription_data = {
            'plan_id': settings.PAYPAL_PLAN_ID,
            'application_context': {
                'return_url': settings.PAYPAL_SUBSCRIPTION_RETURN_URL,
                'cancel_url': settings.PAYPAL_SUBSCRIPTION_CANCEL_URL,
                'user_action': 'SUBSCRIBE_NOW'
            }
        }
        
        response = requests.post(
            f'{PAYPAL_API_BASE}/v1/billing/subscriptions',
            headers=headers,
            json=subscription_data
        )
        
        if response.status_code != 201:
            return Response({
                'error': 'Failed to create PayPal subscription'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        subscription_response = response.json()
        
        # Create local subscription record
        subscription = PayPalSubscription.objects.create(
            user=request.user,
            subscription_id=subscription_response['id'],
            status='PENDING'
        )
        
        serializer = PayPalSubscriptionSerializer(subscription)
        return Response({
            **serializer.data,
            'links': subscription_response['links']
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f'Error creating PayPal subscription: {str(e)}')
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def paypal_subscription_webhook(request):
    try:
        # Verify webhook signature
        webhook_id = settings.PAYPAL_WEBHOOK_ID
        headers = {
            'Authorization': f'Bearer {get_paypal_access_token()}',
            'Content-Type': 'application/json'
        }
        
        verification_data = {
            'auth_algo': request.headers.get('PAYPAL-AUTH-ALGO'),
            'cert_url': request.headers.get('PAYPAL-CERT-URL'),
            'transmission_id': request.headers.get('PAYPAL-TRANSMISSION-ID'),
            'transmission_sig': request.headers.get('PAYPAL-TRANSMISSION-SIG'),
            'transmission_time': request.headers.get('PAYPAL-TRANSMISSION-TIME'),
            'webhook_id': webhook_id,
            'webhook_event': request.data
        }
        
        verify_response = requests.post(
            f'{PAYPAL_API_BASE}/v1/notifications/verify-webhook-signature',
            headers=headers,
            json=verification_data
        )
        
        if verify_response.status_code != 200 or verify_response.json()['verification_status'] != 'SUCCESS':
            return Response({
                'error': 'Invalid webhook signature'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Process webhook
        event_type = request.data.get('event_type')
        resource = request.data.get('resource', {})
        subscription_id = resource.get('id')
        
        if not subscription_id:
            return Response({
                'error': 'Subscription ID not found in webhook'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        subscription = PayPalSubscription.objects.get(subscription_id=subscription_id)
        
        if event_type == 'BILLING.SUBSCRIPTION.ACTIVATED':
            subscription.status = 'ACTIVE'
            subscription.save()
            
            # Update user's premium status
            user_profile = UserProfile.objects.get(user=subscription.user)
            was_subscribed = user_profile.tiene_suscripcion
            user_profile.tiene_suscripcion = True
            
            # Reset tiradas and add bonus gemas when subscribing
            if not was_subscribed:
                user_profile = reset_subscription_benefits(user_profile)
            else:
                user_profile.save()
                
            logger.info(f'Activated premium subscription for user {subscription.user.id}')
            
        elif event_type == 'BILLING.SUBSCRIPTION.CANCELLED':
            subscription.status = 'CANCELLED'
            subscription.save()
            
            # Update user's premium status
            user_profile = UserProfile.objects.get(user=subscription.user)
            user_profile.tiene_suscripcion = False
            user_profile.save()
            
            logger.info(f'Cancelled premium subscription for user {subscription.user.id}')
        
        serializer = PayPalSubscriptionSerializer(subscription)
        return Response(serializer.data)
        
    except PayPalSubscription.DoesNotExist:
        return Response({
            'error': 'Subscription not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f'Error processing PayPal subscription webhook: {str(e)}')
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
