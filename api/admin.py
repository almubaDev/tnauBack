from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    CustomUser, UserProfile, Hechizo, Pocion, CompraHechizo, CompraPocion,
    CartaTarot, TipoTirada, TiradaRealizada, CartaEnTirada
)


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'is_staff', 'is_superuser')
    search_fields = ('email',)
    ordering = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permisos', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
        ('Fechas', {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )
    
@admin.register(Hechizo)
class HechizoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'categoria', 'precio_gemas', 'activo']
    list_filter = ['categoria', 'activo']
    search_fields = ['titulo', 'descripcion']


@admin.register(Pocion)
class PocionAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'categoria', 'precio_gemas', 'activo']
    list_filter = ['categoria', 'activo']
    search_fields = ['titulo', 'descripcion']

@admin.register(CompraHechizo)
class CompraHechizoAdmin(admin.ModelAdmin):
    list_display = ['user', 'hechizo', 'fecha_compra']
    list_filter = ['fecha_compra']
    search_fields = ['user__email', 'hechizo__titulo']

@admin.register(CompraPocion)
class CompraPocionAdmin(admin.ModelAdmin):
    list_display = ['user', 'pocion', 'fecha_compra']
    list_filter = ['fecha_compra']
    search_fields = ['user__email', 'pocion__titulo']

@admin.register(CartaTarot)
class CartaTarotAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'numero', 'imagen_nombre']
    search_fields = ['nombre', 'significado_normal', 'significado_invertido']
    list_filter = ['numero']
    ordering = ['numero']

@admin.register(TipoTirada)
class TipoTiradaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'tipo', 'num_cartas', 'costo_gemas', 'limite_mensual']
    list_filter = ['tipo']
    search_fields = ['nombre', 'descripcion']

class CartaEnTiradaInline(admin.TabularInline):
    model = CartaEnTirada
    extra = 1
    readonly_fields = ['carta', 'posicion', 'invertida']
    
@admin.register(TiradaRealizada)
class TiradaRealizadaAdmin(admin.ModelAdmin):
    list_display = ['user', 'tipo_tirada', 'fecha', 'pregunta_truncada']
    list_filter = ['tipo_tirada', 'fecha']
    search_fields = ['user__email', 'pregunta', 'interpretacion']
    inlines = [CartaEnTiradaInline]
    
    def pregunta_truncada(self, obj):
        return obj.pregunta[:50] + '...' if len(obj.pregunta) > 50 else obj.pregunta
    pregunta_truncada.short_description = 'Pregunta'

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(UserProfile)