import requests
import os
import json
from dotenv import load_dotenv
import base64

# Cargar variables de entorno
load_dotenv()

# Credenciales exactas
PAYPAL_CLIENT_ID = 'ARN_0c5kwagyFzXN1WKhOXNhfQtVcbe2MaoX2uGebPvPjQHlpkDcnKUAv41_oL66oY-7dpDdhrbEqVrZ'
PAYPAL_CLIENT_SECRET = 'EP_SNfrG0LeKh8VZYTSMWoJaNQ3CUA7J2S8DQtaAJ-EY4r0Th6TYjn5y27fhl2vgfvw3rT6OquY1h0Gr'
PAYPAL_API_BASE = 'https://api-m.paypal.com'

def get_access_token():
    auth_url = f"{PAYPAL_API_BASE}/v1/oauth2/token"
    
    # Crear la cadena de autenticación Basic
    auth_string = f"{PAYPAL_CLIENT_ID}:{PAYPAL_CLIENT_SECRET}"
    auth_bytes = auth_string.encode('ascii')
    auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
    
    headers = {
        'Authorization': f'Basic {auth_b64}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    data = 'grant_type=client_credentials'
    
    print(f"Using Client ID: {PAYPAL_CLIENT_ID}")
    print(f"Using API Base: {PAYPAL_API_BASE}")
    print(f"Auth string (before encoding): {auth_string}")
    
    try:
        response = requests.post(auth_url, headers=headers, data=data)
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        print(f"Request headers: {headers}")
        
        if response.ok:
            return response.json()['access_token']
        raise Exception(f'Failed to get access token. Status: {response.status_code}, Response: {response.text}')
    except Exception as e:
        print(f"Exception details: {str(e)}")
        raise

def create_product():
    url = f"{PAYPAL_API_BASE}/v1/catalogs/products"
    headers = {
        'Authorization': f'Bearer {get_access_token()}',
        'Content-Type': 'application/json',
    }
    
    product_data = {
        'name': 'TarotNautica Premium',
        'description': 'Suscripción mensual a TarotNautica',
        'type': 'SERVICE',
        'category': 'SOFTWARE',
    }
    
    response = requests.post(url, headers=headers, json=product_data)
    if response.ok:
        return response.json()['id']
    raise Exception(f'Failed to create product: {response.text}')

def create_plan(product_id):
    url = f"{PAYPAL_API_BASE}/v1/billing/plans"
    headers = {
        'Authorization': f'Bearer {get_access_token()}',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }
    
    plan_data = {
        'product_id': product_id,
        'name': 'TarotNautica Premium Mensual',
        'description': 'Suscripción mensual a TarotNautica',
        'status': 'ACTIVE',
        'billing_cycles': [
            {
                'frequency': {
                    'interval_unit': 'MONTH',
                    'interval_count': 1
                },
                'tenure_type': 'REGULAR',
                'sequence': 1,
                'total_cycles': 0,
                'pricing_scheme': {
                    'fixed_price': {
                        'value': '9.99',
                        'currency_code': 'USD'
                    }
                }
            }
        ],
        'payment_preferences': {
            'auto_bill_outstanding': True,
            'setup_fee': {
                'value': '0',
                'currency_code': 'USD'
            },
            'setup_fee_failure_action': 'CONTINUE',
            'payment_failure_threshold': 3
        }
    }
    
    response = requests.post(url, headers=headers, json=plan_data)
    if response.ok:
        return response.json()['id']
    raise Exception(f'Failed to create plan: {response.text}')

def main():
    try:
        print("Creando producto en PayPal...")
        product_id = create_product()
        print(f"Producto creado con ID: {product_id}")
        
        print("\nCreando plan de suscripción...")
        plan_id = create_plan(product_id)
        print(f"Plan creado con ID: {plan_id}")
        
        print("\nGuarda estos IDs en tu archivo .env:")
        print(f"PAYPAL_PRODUCT_ID={product_id}")
        print(f"PAYPAL_SUBSCRIPTION_PLAN_ID={plan_id}")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == '__main__':
    main() 