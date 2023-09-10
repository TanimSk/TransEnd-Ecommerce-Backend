from django.db import models


class Vendor(models.Model):
    name = models.CharField(max_length=200, blank=True)
    phone_number = models.BigIntegerField()
    address = models.TextField()

    def __str__(self) -> str:
        return self.name
