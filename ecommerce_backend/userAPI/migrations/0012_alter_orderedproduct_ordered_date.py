# Generated by Django 4.2.4 on 2023-08-31 07:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userAPI', '0011_alter_orderedproduct_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderedproduct',
            name='ordered_date',
            field=models.DateTimeField(blank=True),
        ),
    ]