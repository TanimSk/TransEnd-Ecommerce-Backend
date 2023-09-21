# Generated by Django 4.2.4 on 2023-09-21 07:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('productsAPI', '0001_initial'),
        ('userAPI', '0004_orderedproduct_coupon_bdt'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wishlist',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='wishlist_product', to='productsAPI.product'),
        ),
    ]
