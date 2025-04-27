from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
import random


# --- Custom User Manager ---
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("El correo electrónico es obligatorio")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

# --- Custom User Model ---
class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

#--- User Profile Model ---
class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    gemas = models.PositiveIntegerField(default=0)
    tiene_suscripcion = models.BooleanField(default=False)
    tiradas_basicas_usadas = models.PositiveIntegerField(default=0)
    tiradas_claridad_usadas = models.PositiveIntegerField(default=0)
    tiradas_profundas_usadas = models.PositiveIntegerField(default=0)
    fecha_reset = models.DateField(auto_now_add=True)

    def reset_tiradas_mensuales(self):
        from datetime import date
        today = date.today()
        if self.fecha_reset.month != today.month or self.fecha_reset.year != today.year:
            self.tiradas_basicas_usadas = 0
            self.tiradas_claridad_usadas = 0
            self.tiradas_profundas_usadas = 0
            self.fecha_reset = today
            self.save()
            
            

class Hechizo(models.Model):
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio_gemas = models.PositiveIntegerField(default=1)
    activo = models.BooleanField(default=True)
    categoria = models.CharField(
        max_length=20,
        choices=[('amor', 'Amor'), ('dinero', 'Dinero'), ('miselaneo', 'Misceláneo')],
        default='miselaneo'
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo

class Pocion(models.Model):
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio_gemas = models.PositiveIntegerField(default=1)
    activo = models.BooleanField(default=True)
    categoria = models.CharField(
        max_length=20,
        choices=[('amor', 'Amor'), ('dinero', 'Dinero'), ('miselaneo', 'Misceláneo')],
        default='miselaneo'
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo

# Nuevos modelos para registrar compras
class CompraHechizo(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='compras_hechizos')
    hechizo = models.ForeignKey(Hechizo, on_delete=models.CASCADE)
    fecha_compra = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'hechizo')  # Evitar duplicados
        
    def __str__(self):
        return f"{self.user.email} - {self.hechizo.titulo}"

class CompraPocion(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='compras_pociones')
    pocion = models.ForeignKey(Pocion, on_delete=models.CASCADE)
    fecha_compra = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'pocion')  # Evitar duplicados
        
    def __str__(self):
        return f"{self.user.email} - {self.pocion.titulo}"

# Modelo de Carta de Tarot (Arcanos Mayores)
class CartaTarot(models.Model):
    nombre = models.CharField(max_length=100)
    numero = models.IntegerField()  # 0-21 para los Arcanos Mayores
    imagen_nombre = models.CharField(max_length=100)  # Nombre del archivo en el frontend
    significado_normal = models.TextField()
    significado_invertido = models.TextField()
    
    def __str__(self):
        return f"{self.numero} - {self.nombre}"
    
    class Meta:
        ordering = ['numero']
        verbose_name = "Carta de Tarot"
        verbose_name_plural = "Cartas de Tarot"

# Modelo para Tipo de Tirada
class TipoTirada(models.Model):
    TIPO_CHOICES = [
        ('basica', 'Tirada Básica'),
        ('claridad', 'Tirada de Claridad'),
        ('profunda', 'Tirada Profunda')
    ]
    
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    num_cartas = models.IntegerField()
    descripcion = models.TextField()
    costo_gemas = models.PositiveIntegerField(default=1)
    limite_mensual = models.PositiveIntegerField(default=0)  # Para usuarios con suscripción
    layout_descripcion = models.TextField(help_text="Descripción de la disposición de las cartas")
    
    def __str__(self):
        return self.nombre

# Modelo para registrar las tiradas realizadas
class TiradaRealizada(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='tiradas')
    tipo_tirada = models.ForeignKey(TipoTirada, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    pregunta = models.TextField()
    interpretacion = models.TextField()  # Respuesta de la API
    
    def __str__(self):
        return f"{self.user.email} - {self.tipo_tirada.nombre} - {self.fecha.strftime('%d/%m/%Y')}"

# Modelo para las cartas de una tirada
class CartaEnTirada(models.Model):
    tirada = models.ForeignKey(TiradaRealizada, on_delete=models.CASCADE, related_name='cartas')
    carta = models.ForeignKey(CartaTarot, on_delete=models.CASCADE)
    posicion = models.IntegerField(help_text="Número de posición en la tirada (1, 2, 3...)")
    invertida = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['posicion']
    
    def __str__(self):
        estado = "Invertida" if self.invertida else "Normal"
        return f"{self.carta.nombre} - Posición {self.posicion} - {estado}"

# Nuevos modelos para Stripe
class StripeCustomer(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    stripe_customer_id = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.stripe_customer_id}"

class StripeSubscription(models.Model):
    STATUS_CHOICES = [
        ('active', 'Activa'),
        ('past_due', 'Pago Pendiente'),
        ('canceled', 'Cancelada'),
        ('incomplete', 'Incompleta'),
        ('incomplete_expired', 'Expirada'),
        ('trialing', 'En Periodo de Prueba'),
        ('unpaid', 'No Pagada')
    ]

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    stripe_subscription_id = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    current_period_end = models.DateTimeField()
    cancel_at_period_end = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - {self.status}"

class StripePayment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('completed', 'Completado'),
        ('failed', 'Fallido'),
        ('refunded', 'Reembolsado')
    ]

    PAYMENT_TYPE_CHOICES = [
        ('subscription', 'Suscripción'),
        ('gems', 'Compra de Gemas')
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    stripe_payment_intent_id = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES)
    gems_amount = models.IntegerField(null=True, blank=True)  # Solo para compras de gemas
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - {self.payment_type} - {self.amount} {self.currency}"

class PayPalPayment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    order_id = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    gems_amount = models.IntegerField()
    status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"PayPal Payment {self.order_id} - {self.status}"

class PayPalSubscription(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    subscription_id = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"PayPal Subscription {self.subscription_id} - {self.status}"