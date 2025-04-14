#!/usr/bin/env python
import os
import traceback
import sys
import anthropic
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def print_debug_info():
    """Print detailed debug information"""
    print("\n=== ENTORNO DE EJECUCIÓN ===")
    print(f"Python version: {sys.version}")
    print(f"Directorio actual: {os.getcwd()}")
    
    anthropic_key = os.getenv('ANTHROPIC_API_KEY', 'No encontrada')
    print(f"ANTHROPIC_API_KEY: {'Configurada' if anthropic_key != 'No encontrada' else 'No encontrada'}")
    
    # Mostrar primeros y últimos caracteres de la clave para verificar formato sin exponer la clave completa
    if anthropic_key != 'No encontrada':
        key_prefix = anthropic_key[:8]
        key_suffix = anthropic_key[-4:]
        print(f"Formato de clave: {key_prefix}...{key_suffix}")

def test_anthropic_connection():
    """Test connection to Anthropic API"""
    print("\n=== TEST DE CONEXIÓN A ANTHROPIC API ===")
    
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("Error: No se encontró ANTHROPIC_API_KEY en las variables de entorno")
        return False
    
    print(f"Usando API key que comienza con: {api_key[:8]}...")
    
    try:
        # Crear cliente Anthropic con timeout explícito
        client = anthropic.Anthropic(
            api_key=api_key,
            # Configuración detallada de timeouts para mejor diagnóstico
            http_client=anthropic.AnthropicHTTPClient(
                timeout=60.0,  # Timeout global de 60 segundos
            )
        )
        
        # Realizar solicitud simple
        print("Enviando solicitud a la API...")
        
        message = client.messages.create(
            model="claude-3-haiku-20240307",  # Modelo más pequeño/rápido para pruebas
            max_tokens=100,
            temperature=0.0,  # Sin creatividad para respuestas consistentes
            system="Responde de manera concisa y directa.",
            messages=[
                {"role": "user", "content": "Responde solo con la frase 'La conexión a Anthropic funciona correctamente'."}
            ]
        )
        
        # Verificar respuesta
        response_text = message.content[0].text
        print(f"\nRespuesta recibida: {response_text}")
        
        # Éxito si la respuesta contiene el texto esperado
        success = "funciona correctamente" in response_text
        print(f"Test resultado: {'ÉXITO ✅' if success else 'FALLO ❌'}")
        return success
        
    except Exception as e:
        print(f"\nError al conectar con Anthropic: {str(e)}")
        print("\nDetalles del error:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== DIAGNÓSTICO DE ANTHROPIC API ===")
    print_debug_info()
    
    success = test_anthropic_connection()
    
    if success:
        print("\n✅ La conexión a Anthropic funciona correctamente.")
        sys.exit(0)
    else:
        print("\n❌ La conexión a Anthropic falló. Revise los mensajes de error anteriores.")
        sys.exit(1)
