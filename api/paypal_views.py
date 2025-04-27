import json
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import requests
from .models import UserProfile, PayPalPayment, PayPalSubscription

PAYPAL_BASE_URL = 'https://api-m.sandbox.paypal.com' if settings.DEBUG else 'https://api-m.paypal.com'

def get_access_token():
    auth_url = f"{PAYPAL_BASE_URL}/v1/oauth2/token"
    headers = {
        'Accept': 'application/json',
        'Accept-Language': 'en_US'
    }
    data = {'grant_type': 'client_credentials'}
    auth = (settings.PAYPAL_CLIENT_ID, settings.PAYPAL_CLIENT_SECRET)
    
    response = requests.post(auth_url, headers=headers, data=data, auth=auth)
    return response.json()['access_token']

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crear_orden_paypal(request):
    try:
        amount = request.data.get('amount')
        payment_type = request.data.get('payment_type')
        gems_amount = request.data.get('gems_amount', 0)
        currency = request.data.get('currency', 'USD')

        access_token = get_access_token()
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}',
        }
        
        payload = {
            'intent': 'CAPTURE',
            'purchase_units': [{
                'amount': {
                    'currency_code': currency,
                    'value': str(amount)
                },
                'description': f'Compra de {gems_amount} gemas en TarotNautica'
            }],
            'application_context': {
                'brand_name': 'TarotNautica',
                'landing_page': 'NO_PREFERENCE',
                'user_action': 'PAY_NOW',
                'return_url': 'https://tarotnautica.com/success',
                'cancel_url': 'https://tarotnautica.com/cancel'
            }
        }

        response = requests.post(
            f"{PAYPAL_BASE_URL}/v2/checkout/orders",
            headers=headers,
            json=payload
        )

        if response.ok:
            order_data = response.json()
            
            # Guardar la orden en la base de datos
            PayPalPayment.objects.create(
                user=request.user,
                order_id=order_data['id'],
                amount=amount,
                currency=currency,
                status='CREATED',
                payment_type=payment_type,
                gems_amount=gems_amount
            )
            
            return Response({
                'orderID': order_data['id']
            })
        else:
            return Response(
                {'error': 'Error al crear la orden'},
                status=status.HTTP_400_BAD_REQUEST
            )

    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def capturar_pago_paypal(request):
    try:
        order_id = request.data.get('orderID')
        access_token = get_access_token()
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}',
        }

        response = requests.post(
            f"{PAYPAL_BASE_URL}/v2/checkout/orders/{order_id}/capture",
            headers=headers
        )

        if response.ok:
            capture_data = response.json()
            
            # Actualizar el pago en la base de datos
            payment = PayPalPayment.objects.get(order_id=order_id)
            payment.status = 'COMPLETED'
            payment.save()
            
            # Acreditar gemas si es una compra de gemas
            if payment.payment_type == 'gems':
                profile = UserProfile.objects.get(user=request.user)
                profile.gemas += payment.gems_amount
                profile.save()
            
            return Response(capture_data)
        else:
            return Response(
                {'error': 'Error al capturar el pago'},
                status=status.HTTP_400_BAD_REQUEST
            )

    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crear_suscripcion_paypal(request):
    try:
        access_token = get_access_token()
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}',
        }
        
        payload = {
            'plan_id': settings.PAYPAL_SUBSCRIPTION_PLAN_ID,
            'subscriber': {
                'name': {
                    'given_name': request.user.first_name,
                    'surname': request.user.last_name
                },
                'email_address': request.user.email
            },
            'application_context': {
                'brand_name': 'TarotNautica',
                'user_action': 'SUBSCRIBE_NOW',
                'return_url': 'https://tarotnautica.com/subscription/success',
                'cancel_url': 'https://tarotnautica.com/subscription/cancel'
            }
        }

        response = requests.post(
            f"{PAYPAL_BASE_URL}/v1/billing/subscriptions",
            headers=headers,
            json=payload
        )

        if response.ok:
            subscription_data = response.json()
            
            # Guardar la suscripción en la base de datos
            PayPalSubscription.objects.create(
                user=request.user,
                subscription_id=subscription_data['id'],
                status='APPROVAL_PENDING'
            )
            
            return Response(subscription_data)
        else:
            return Response(
                {'error': 'Error al crear la suscripción'},
                status=status.HTTP_400_BAD_REQUEST
            )

    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancelar_suscripcion_paypal(request):
    try:
        subscription_id = request.data.get('subscriptionId')
        access_token = get_access_token()
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}',
        }

        response = requests.post(
            f"{PAYPAL_BASE_URL}/v1/billing/subscriptions/{subscription_id}/cancel",
            headers=headers
        )

        if response.ok:
            # Actualizar la suscripción en la base de datos
            subscription = PayPalSubscription.objects.get(subscription_id=subscription_id)
            subscription.status = 'CANCELLED'
            subscription.save()
            
            # Actualizar el perfil del usuario
            profile = UserProfile.objects.get(user=request.user)
            profile.tiene_suscripcion = False
            profile.save()
            
            return Response({'status': 'Subscription cancelled'})
        else:
            return Response(
                {'error': 'Error al cancelar la suscripción'},
                status=status.HTTP_400_BAD_REQUEST
            )

    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        ) 