from django.db import models


class Vendor(models.Model):
    name = models.CharField(max_length=200, blank=True)
    phone_number = models.IntegerField()
    address = models.TextField()
