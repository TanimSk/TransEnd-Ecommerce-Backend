# Generated by Django 4.2.4 on 2023-12-23 07:23

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('productsAPI', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='colors',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=500), blank=True, default=list, size=None),
        ),
        migrations.AddField(
            model_name='product',
            name='product_sku',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='sizes',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=500), blank=True, default=list, size=None),
        ),
    ]