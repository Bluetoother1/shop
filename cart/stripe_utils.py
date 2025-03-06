import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_payment_intent(amount):
    try:
        intent = stripe.PaymentIntent.create(
            amount=int(amount * 100),  # Stripe использует центы
            currency='usd',
            metadata={'integration_check': 'accept_a_payment'},
        )
        return intent
    except Exception as e:
        print(f"Error creating payment intent: {e}")
        return None
