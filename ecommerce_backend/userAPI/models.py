from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

# Signals
from django.db.models.signals import post_delete
from django.dispatch import receiver


class User(AbstractUser):
    # Boolean fields to select the type of account.
    is_admin = models.BooleanField(default=False)
    is_consumer = models.BooleanField(default=False)


class Consumer(models.Model):
    consumer = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="consumer"
    )
    name = models.CharField(max_length=200, blank=True)
    phone_number = models.BigIntegerField()
    address = models.TextField()
    METHODS = (
        ("cod", "cod"),
        ("mobile", "mobile"),
    )
    payment_method = models.CharField(max_length=50, choices=METHODS)
    inside_dhaka = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.consumer.email


@receiver(post_delete, sender=Consumer)
def delete_consumer_user(sender, instance, **kwargs):
    # User = get_user_model()
    user = instance.consumer
    user.delete()
