# Generated by Django 4.2.4 on 2023-08-28 05:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('productsAPI', '0002_remove_wishlist_product_delete_orderedproduct_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='price',
            new_name='price_bdt',
        ),
        migrations.AddField(
            model_name='product',
            name='price_cad',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='product',
            name='price_eur',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='product',
            name='price_gbp',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='product',
            name='price_usd',
            field=models.IntegerField(default=0),
        ),
    ]
