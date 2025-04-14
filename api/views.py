from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import (UserProfile, Hechizo, Pocion, CompraHechizo, CompraPocion,
                     CartaTarot, TipoTirada, TiradaRealizada, CartaEnTirada)
from .subscription_handler import reset_subscription_benefits
from .serializers import (
    UserProfileSerializer, HechizoSerializer, PocionSerializer,
    UserSerializer, CompraHechizoSerializer, CompraPocionSerializer,
    CartaTarotSerializer, TipoTiradaSerializer, TiradaRealizadaSerializer, 
    CartaEnTiradaSerializer, CrearTiradaSerializer
)
from rest_framework_simplejwt.views import TokenObtainPairView
from .custom_token import CustomTokenObtainPairSerializer
import random
import os
import anthropic
import logging
from django.conf import settings

# Configurar logging
logger = logging.getLogger(__name__)




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
    Genera la interpretación de una tirada de tarot utilizando la API de Anthropic.
    
    Args:
        tirada: Objeto TiradaRealizada con la información de la tirada
        cartas_en_tirada: Lista de objetos CartaEnTirada
    
    Returns:
        str: Interpretación generada por la IA
    """
    try:
        # Cargar variables de entorno directamente para asegurar que tenemos acceso a la clave API
        from dotenv import load_dotenv
        load_dotenv()
        
        # Obtener la clave API de las variables de entorno
        ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')
        
        if not ANTHROPIC_API_KEY:
            logger.error("No se encontró la clave API de Anthropic en variables de entorno")
            raise ValueError("API key no encontrada")
        
        logger.info(f"Usando API key: {ANTHROPIC_API_KEY[:8]}...")
        
        # Crear cliente de Anthropic con timeout explícito
        client = anthropic.Anthropic(
            api_key=ANTHROPIC_API_KEY,
            # Configuración explícita del tiempo de espera
            http_client=anthropic.AnthropicHTTPClient(
                timeout=60.0,  # Timeout global de 60 segundos
            )
        )
        
        # Determinar nombres de posiciones según tipo de tirada
        if tirada.tipo_tirada.tipo == 'basica':
            nombres_posicion = ["Pasado", "Presente", "Futuro"]
        elif tirada.tipo_tirada.tipo == 'claridad':
            nombres_posicion = [
                "Situación General", 
                "Obstáculo Principal", "Influencia Consciente", "Influencia Inconsciente",
                "Consejo", "Resultado Potencial"
            ]
        elif tirada.tipo_tirada.tipo == 'profunda':
            nombres_posicion = [
                "Esencia del Problema",
                "Pensamiento Personal", "Pensamiento Externo", "Pensamiento Ideal",
                "Emociones Personales", "Emociones Externas", "Emociones Ideales",
                "Situación Material Personal", "Situación Material Externa", "Situación Material Ideal",
                "Resultado Final"
            ]
        else:
            nombres_posicion = [f"Posición {i+1}" for i in range(tirada.tipo_tirada.num_cartas)]
        
        # Asegurar que hay suficientes nombres para todas las posiciones
        if len(nombres_posicion) < tirada.tipo_tirada.num_cartas:
            nombres_posicion.extend([f"Posición {i+1}" for i in range(len(nombres_posicion), tirada.tipo_tirada.num_cartas)])
        
        # Construir lista de significados de las cartas
        significados = []
        for carta_tirada in cartas_en_tirada:
            posicion_idx = carta_tirada.posicion - 1  # Convertir a índice base 0
            nombre_posicion = nombres_posicion[posicion_idx] if posicion_idx < len(nombres_posicion) else f"Posición {carta_tirada.posicion}"
            
            significado = carta_tirada.carta.significado_invertido if carta_tirada.invertida else carta_tirada.carta.significado_normal
            orientacion = "invertida" if carta_tirada.invertida else "normal"
            
            significados.append(f"Posición {carta_tirada.posicion} ({nombre_posicion}): {carta_tirada.carta.nombre}, {orientacion}. Significado: {significado}")
        
        # Crear prompt para la API de Anthropic - más simplificado
        system_prompt = "Eres un tarotista experto que proporciona interpretaciones místicas pero prácticas."

        user_prompt = f"""Interpreta esta tirada de tarot para la pregunta: "{tirada.pregunta}"

Tipo de tirada: {tirada.tipo_tirada.nombre}

Cartas:
{chr(10).join(significados)}

Necesito: significado general, conexiones entre cartas, respuesta a mi pregunta, consejos prácticos y mensaje principal."""
        
        # Usar un modelo más pequeño y rápido para evitar problemas de timeout
        logger.info("Enviando solicitud a Anthropic API...")
        response = client.messages.create(
            model="claude-3-haiku-20240307",  # Modelo más pequeño/rápido
            max_tokens=1000,
            temperature=0.7,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )
        
        # Extraer la interpretación del objeto de respuesta
        interpretacion = response.content[0].text
        
        # Log de éxito
        logger.info(f"Interpretación generada exitosamente para tirada ID: {tirada.id}")
        
        return interpretacion
        
    except Exception as e:
        # Log detallado del error
        import traceback
        logger.error(f"Error al generar interpretación: {str(e)}")
        logger.error(traceback.format_exc())
        
        # En caso de error, usar interpretación de respaldo
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
