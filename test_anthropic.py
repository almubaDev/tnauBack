import os
import anthropic
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

def test_anthropic_api():
    print("\n=== TEST DE CONEXIÓN A ANTHROPIC API ===\n")
    
    # Obtener la clave API de las variables de entorno
    api_key = os.getenv('ANTHROPIC_API_KEY')
    
    if not api_key:
        print("Error: No se encontró ANTHROPIC_API_KEY en las variables de entorno")
        return
    
    print(f"API Key encontrada: {api_key[:10]}...{api_key[-5:]}")
    
    try:
        # Crear un cliente de Anthropic
        client = anthropic.Anthropic(api_key=api_key)
        
        # Realizar una solicitud simple
        print("\nRealizando solicitud a la API...")
        
        response = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=150,
            temperature=0.7,
            system="Eres un tarotista experto.",
            messages=[
                {"role": "user", "content": "Describe brevemente el significado de la carta 'El Loco' en el tarot."}
            ]
        )
        
        # Mostrar la respuesta
        print("\n=== RESPUESTA RECIBIDA ===")
        print(f"Contenido: {response.content[0].text}")
        print("\n=== TEST COMPLETADO EXITOSAMENTE ===")
        
    except anthropic.APIError as api_error:
        print(f"\nError de API Anthropic: {str(api_error)}")
    except anthropic.RateLimitError as rate_error:
        print(f"\nError de límite de velocidad: {str(rate_error)}")
    except anthropic.APIConnectionError as conn_error:
        print(f"\nError de conexión a API: {str(conn_error)}")
    except Exception as e:
        print(f"\nError inesperado: {str(e)}")

if __name__ == "__main__":
    test_anthropic_api()
