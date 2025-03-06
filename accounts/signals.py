from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from bonussystem.models import UserProfile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Автоматически создает профиль пользователя при создании нового пользователя.
    """
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Автоматически сохраняет профиль пользователя при сохранении пользователя.
    """
    instance.userprofile.save()
