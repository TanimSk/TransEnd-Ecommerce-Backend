# Generated by Django 4.2.4 on 2023-08-27 06:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userAPI', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='consumer',
            name='phone_number',
            field=models.BigIntegerField(),
        ),
    ]
