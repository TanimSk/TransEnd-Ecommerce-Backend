# Generated by Django 4.2.4 on 2023-08-30 10:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('userAPI', '0008_orderedproduct_dispatched_orderedproduct_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderedproduct',
            name='used_coupon',
        ),
    ]