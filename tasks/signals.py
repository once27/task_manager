from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        # Only create if it doesn't already exist
        if not hasattr(instance, 'profile'):
            UserProfile.objects.create(user=instance)
    else:
        # Save profile only if it exists
        if hasattr(instance, 'profile'):
            instance.profile.save()


# @receiver(post_save, sender=User)
# def create_or_update_user_profile(sender, instance, created, **kwargs):
#     if created:
#         UserProfile.objects.create(user=instance)
#     else:
#         instance.profile.save()
