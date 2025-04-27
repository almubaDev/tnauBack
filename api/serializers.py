from rest_framework import serializers
from .models import (
    UserProfile, Hechizo, Pocion, CompraHechizo, CompraPocion, CustomUser,
    CartaTarot, TipoTirada, TiradaRealizada, CartaEnTirada, PayPalPayment, PayPalSubscription
)
from django.contrib.auth.password_validation import validate_password
from rest_framework.validators import UniqueValidator

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['user', 'gemas', 'tiene_suscripcion', 'tiradas_basicas_usadas', 'tiradas_claridad_usadas', 'tiradas_profundas_usadas']

class HechizoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hechizo
        fields = ['id', 'titulo', 'descripcion', 'precio_gemas', 'categoria']


class PocionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pocion
        fields = ['id', 'titulo', 'descripcion', 'precio_gemas', 'categoria']

class CompraHechizoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompraHechizo
        fields = ['id', 'hechizo', 'fecha_compra']

class CompraPocionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompraPocion
        fields = ['id', 'pocion', 'fecha_compra']

class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=CustomUser.objects.all())]
    )
    password = serializers.CharField(
        write_only=True, 
        required=True, 
        validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = CustomUser
        fields = ('email', 'password', 'password2')
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Las contraseñas no coinciden."})
        return attrs
    
    def create(self, validated_data):
        # Eliminar password2 del diccionario ya que no es parte del modelo
        validated_data.pop('password2')
        
        # Crear el usuario 
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password']
        )
        
        return user

# Serializers para Tarot
class CartaTarotSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartaTarot
        fields = ['id', 'nombre', 'numero', 'imagen_nombre', 'significado_normal', 'significado_invertido']

class TipoTiradaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoTirada
        fields = ['id', 'nombre', 'tipo', 'num_cartas', 'descripcion', 'costo_gemas', 'limite_mensual', 'layout_descripcion']

class CartaEnTiradaSerializer(serializers.ModelSerializer):
    carta_nombre = serializers.CharField(source='carta.nombre', read_only=True)
    carta_imagen = serializers.CharField(source='carta.imagen_nombre', read_only=True)
    significado = serializers.SerializerMethodField()
    
    class Meta:
        model = CartaEnTirada
        fields = ['id', 'carta', 'carta_nombre', 'carta_imagen', 'posicion', 'invertida', 'significado']
    
    def get_significado(self, obj):
        if obj.invertida:
            return obj.carta.significado_invertido
        return obj.carta.significado_normal

class TiradaRealizadaSerializer(serializers.ModelSerializer):
    cartas = CartaEnTiradaSerializer(many=True, read_only=True)
    tipo_tirada_nombre = serializers.CharField(source='tipo_tirada.nombre', read_only=True)
    
    class Meta:
        model = TiradaRealizada
        fields = ['id', 'user', 'tipo_tirada', 'tipo_tirada_nombre', 'fecha', 'pregunta', 'interpretacion', 'cartas']

# Serializer para crear una nueva tirada
class CrearTiradaSerializer(serializers.Serializer):
    tipo_tirada = serializers.PrimaryKeyRelatedField(queryset=TipoTirada.objects.all())
    pregunta = serializers.CharField(required=True)

class PayPalPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayPalPayment
        fields = ['id', 'user', 'order_id', 'amount', 'currency', 'status', 
                 'payment_type', 'gems_amount', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class PayPalSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayPalSubscription
        fields = ['id', 'user', 'subscription_id', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']