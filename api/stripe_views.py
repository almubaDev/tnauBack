import stripe
from django.conf import settings
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import StripeCustomer, StripeSubscription, StripePayment, UserProfile

stripe.api_key = settings.STRIPE_SECRET_KEY

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_payment_intent(request):
    try:
        # Obtener el tipo de compra y cantidad
        payment_type = request.data.get('payment_type')
        amount = request.data.get('amount')

        # Validar los datos
        if not payment_type or not amount:
            return Response(
                {'error': 'Faltan datos requeridos'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Crear o obtener el cliente de Stripe
        stripe_customer, created = StripeCustomer.objects.get_or_create(
            user=request.user,
            defaults={'stripe_customer_id': None}
        )

        if not stripe_customer.stripe_customer_id:
            stripe_customer_data = stripe.Customer.create(
                email=request.user.email,
                metadata={'user_id': request.user.id}
            )
            stripe_customer.stripe_customer_id = stripe_customer_data.id
            stripe_customer.save()

        # Crear el PaymentIntent
        intent = stripe.PaymentIntent.create(
            amount=int(float(amount) * 100),  # Convertir a centavos
            currency='usd',
            customer=stripe_customer.stripe_customer_id,
            metadata={
                'payment_type': payment_type,
                'user_id': request.user.id
            }
        )

        # Registrar el intento de pago
        StripePayment.objects.create(
            user=request.user,
            stripe_payment_intent_id=intent.id,
            amount=amount,
            status='pending',
            payment_type=payment_type,
            gems_amount=request.data.get('gems_amount')
        )

        return Response({
            'clientSecret': intent.client_secret
        })

    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_subscription(request):
    try:
        # Crear o obtener el cliente de Stripe
        stripe_customer, created = StripeCustomer.objects.get_or_create(
            user=request.user,
            defaults={'stripe_customer_id': None}
        )

        if not stripe_customer.stripe_customer_id:
            stripe_customer_data = stripe.Customer.create(
                email=request.user.email,
                metadata={'user_id': request.user.id}
            )
            stripe_customer.stripe_customer_id = stripe_customer_data.id
            stripe_customer.save()

        # Crear la suscripción
        subscription = stripe.Subscription.create(
            customer=stripe_customer.stripe_customer_id,
            items=[{'price': settings.STRIPE_SUBSCRIPTION_PRICE_ID}],
            payment_behavior='default_incomplete',
            expand=['latest_invoice.payment_intent'],
            metadata={'user_id': request.user.id}
        )

        # Registrar la suscripción
        StripeSubscription.objects.create(
            user=request.user,
            stripe_subscription_id=subscription.id,
            status=subscription.status,
            current_period_end=subscription.current_period_end
        )

        return Response({
            'subscriptionId': subscription.id,
            'clientSecret': subscription.latest_invoice.payment_intent.client_secret
        })

    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_subscription(request):
    try:
        # Obtener la suscripción del usuario
        subscription = StripeSubscription.objects.get(
            user=request.user,
            status='active'
        )

        # Cancelar la suscripción en Stripe
        stripe_subscription = stripe.Subscription.modify(
            subscription.stripe_subscription_id,
            cancel_at_period_end=True
        )

        # Actualizar el estado en la base de datos
        subscription.cancel_at_period_end = True
        subscription.save()

        return Response({
            'message': 'Suscripción cancelada exitosamente',
            'cancel_at': stripe_subscription.cancel_at
        })

    except StripeSubscription.DoesNotExist:
        return Response(
            {'error': 'No se encontró una suscripción activa'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    except stripe.error.SignatureVerificationError as e:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        handle_successful_payment(payment_intent)
    elif event['type'] == 'invoice.paid':
        invoice = event['data']['object']
        handle_successful_subscription(invoice)
    elif event['type'] == 'customer.subscription.deleted':
        subscription = event['data']['object']
        handle_subscription_cancelled(subscription)

    return Response(status=status.HTTP_200_OK)

def handle_successful_payment(payment_intent):
    try:
        payment = StripePayment.objects.get(
            stripe_payment_intent_id=payment_intent.id
        )
        payment.status = 'completed'
        payment.save()

        if payment.payment_type == 'gems':
            profile = UserProfile.objects.get(user=payment.user)
            profile.gemas += payment.gems_amount
            profile.save()

    except StripePayment.DoesNotExist:
        pass

def handle_successful_subscription(invoice):
    try:
        subscription_id = invoice.subscription
        subscription = StripeSubscription.objects.get(
            stripe_subscription_id=subscription_id
        )
        subscription.status = 'active'
        subscription.save()

        profile = UserProfile.objects.get(user=subscription.user)
        profile.tiene_suscripcion = True
        profile.gemas += 30  # Bonus de gemas por suscripción
        profile.save()

    except StripeSubscription.DoesNotExist:
        pass

def handle_subscription_cancelled(subscription_data):
    try:
        subscription = StripeSubscription.objects.get(
            stripe_subscription_id=subscription_data.id
        )
        subscription.status = 'canceled'
        subscription.save()

        profile = UserProfile.objects.get(user=subscription.user)
        profile.tiene_suscripcion = False
        profile.save()

    except StripeSubscription.DoesNotExist:
        pass 