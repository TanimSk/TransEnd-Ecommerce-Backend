# Generated by Django 4.2.4 on 2023-09-10 11:39

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('productsAPI', '0004_alter_product_grant_alter_product_rewards'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='tags',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=500), blank=True, default=list, size=None),
        ),
    ]
