# Generated by Django 4.2.4 on 2023-08-24 07:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('adminAPI', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='admin',
            old_name='mobile_number',
            new_name='phone_number',
        ),
    ]
