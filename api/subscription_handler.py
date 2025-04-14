"""
Subscription handler module for TarotNautica
"""
from django.utils import timezone

def reset_subscription_benefits(user_profile):
    """
    Reset subscription benefits when a user subscribes.
    This resets tirada counters and adds complimentary gemas (if applicable).
    
    Args:
        user_profile: UserProfile instance to update
    """
    # Reset tirada counters to 0
    user_profile.tiradas_basicas_usadas = 0
    user_profile.tiradas_claridad_usadas = 0
    user_profile.tiradas_profundas_usadas = 0
    
    # Update reset date to today
    user_profile.fecha_reset = timezone.now().date()
    
    # Add complimentary gemas for new/renewed subscriptions
    # We're adding 20 complimentary gemas for subscription
    user_profile.gemas += 30
    
    # Save the profile changes
    user_profile.save()
    
    return user_profile
