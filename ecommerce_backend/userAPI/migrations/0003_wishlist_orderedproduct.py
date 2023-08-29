# Generated by Django 4.2.4 on 2023-08-27 08:10

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('productsAPI', '0002_remove_wishlist_product_delete_orderedproduct_and_more'),
        ('userAPI', '0002_alter_consumer_phone_number'),
    ]

    operations = [
        migrations.CreateModel(
            name='Wishlist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('wishlisted_date', models.DateTimeField(auto_now=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='wishlist_product', to='productsAPI.product')),
            ],
        ),
        migrations.CreateModel(
            name='OrderedProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField()),
                ('used_coupon', models.BooleanField(default=False)),
                ('ordered_date', models.DateTimeField(auto_now=True)),
                ('tracking_id', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ordered_product', to='productsAPI.product')),
            ],
        ),
    ]