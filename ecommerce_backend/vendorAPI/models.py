from django.db import models


class Vendor(models.Model):
    name = models.CharField(max_length=200, blank=True)
    phone_number = models.CharField(max_length=100, unique=True)
    address = models.TextField()
    total_received_money = models.IntegerField(default=0)

    def __str__(self) -> str:
        return self.name
