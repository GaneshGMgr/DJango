# ecommerceApp/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Refund
import stripe  # Example payment gateway

@receiver(post_save, sender=Refund)
def process_refund(sender, instance, **kwargs):
    """
    Automatically processes payment refund when status changes to 'approved'
    """
    if instance.status == 'approved':
        try:
            # 1. Call payment gateway API
            payment_intent_id = instance.order.payment.transaction_id  # Assuming you store this
            refund = stripe.Refund.create(
                payment_intent=payment_intent_id,
                amount=int(instance.order.total * 100)  # Convert to cents
            )
            
            # 2. Update refund status
            instance.status = 'processed'
            instance.admin_notes = f"Refund processed via Stripe: {refund.id}"
            instance.save()
            
        except Exception as e:
            instance.admin_notes = f"Refund failed: {str(e)}"
            instance.save()