from django.db import models
from django.contrib.auth.models import User


class User(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="user")
    name = models.CharField(max_length=200, blank=True)
    phone_number = models.IntegerField()
    address = models.TextField()
    METHODS = (
        ("cod", "cod"),
        ("mobile", "mobile"),
    )
    payment_method = models.CharField(max_length=50, choices=METHODS)
    inside_dhaka = models.BooleanField(default=False)
    TYPES = (("user", "user"), ("admin", "admin"))
    user_type = models.CharField(max_length=20, choices=TYPES)
