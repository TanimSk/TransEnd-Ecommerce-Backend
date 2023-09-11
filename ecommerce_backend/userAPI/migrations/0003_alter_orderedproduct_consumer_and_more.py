# Generated by Django 4.2.4 on 2023-09-11 06:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('userAPI', '0002_orderedproduct_price_bought_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderedproduct',
            name='consumer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_consumer', to='userAPI.consumer'),
        ),
        migrations.AlterField(
            model_name='wishlist',
            name='consumer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='wishlist_consumer', to='userAPI.consumer'),
        ),
    ]
