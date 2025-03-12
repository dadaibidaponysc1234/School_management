from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import School, Subscription
from datetime import date, timedelta

@receiver(post_save, sender=School)
def create_subscription_for_new_school(sender, instance, created, **kwargs):
    """
    Automatically create a subscription when a new school is added, with dynamic dates.
    Prevent duplicate subscriptions.
    """
    if created and not Subscription.objects.filter(school=instance).exists():
        today = date.today()
        Subscription.objects.create(
            school=instance,
            amount_per_student=0,  # Default value; can be updated later
            amount_paid=0,  # Default value; can be updated later
            active_date=today,
            expired_date=today + timedelta(days=365),  # Default 1-year subscription
        )
