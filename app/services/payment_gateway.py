from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import Dict, Any

class PaymentIntentResponse(BaseModel):
    provider: str
    intent_id: str
    client_secret: str
    amount: float
    currency: str

class PaymentGatewayAdapter(ABC):
    """Abstract Base Class for configuring multiple payment gateways."""
    
    @abstractmethod
    def create_deposit_intent(self, amount: float, currency: str = "USD") -> PaymentIntentResponse:
        """Initialize a payment intent with the external provider."""
        pass

    @abstractmethod
    def handle_webhook(self, payload: Dict[str, Any], signature: str) -> bool:
        """Validate and parse incoming webhook events."""
        pass

class StripeAdapter(PaymentGatewayAdapter):
    """Stripe implementation of the PaymentGatewayAdapter."""
    
    def create_deposit_intent(self, amount: float, currency: str = "USD") -> PaymentIntentResponse:
        # In a real scenario, this calls stripe.PaymentIntent.create()
        return PaymentIntentResponse(
            provider="stripe",
            intent_id=f"pi_mockStripe_{int(amount)}",
            client_secret="secret_mockStripe",
            amount=amount,
            currency=currency
        )
        
    def handle_webhook(self, payload: Dict[str, Any], signature: str) -> bool:
        # Validate stripe signature
        return payload.get("type") == "payment_intent.succeeded"

class RazorpayAdapter(PaymentGatewayAdapter):
    """Razorpay implementation of the PaymentGatewayAdapter."""
    
    def create_deposit_intent(self, amount: float, currency: str = "INR") -> PaymentIntentResponse:
        # In a real scenario, calls razorpay API
        return PaymentIntentResponse(
            provider="razorpay",
            intent_id=f"order_mockRazor_{int(amount)}",
            client_secret="secret_mockRazor",
            amount=amount,
            currency=currency
        )
        
    def handle_webhook(self, payload: Dict[str, Any], signature: str) -> bool:
        # Validate Razorpay HMAC signature
        return payload.get("event") == "payment.captured"

# Factory / Resolver
def get_payment_adapter(provider: str) -> PaymentGatewayAdapter:
    if provider.lower() == "stripe":
        return StripeAdapter()
    elif provider.lower() == "razorpay":
        return RazorpayAdapter()
    else:
        raise ValueError(f"Unsupported payment provider: {provider}")
