# Generated by Django 4.2.4 on 2023-08-29 14:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('productsAPI', '0004_remove_product_discount_product_discount_bdt_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='coupon_code',
        ),
    ]