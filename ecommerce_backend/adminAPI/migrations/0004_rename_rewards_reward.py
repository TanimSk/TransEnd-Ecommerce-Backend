# Generated by Django 4.2.4 on 2023-09-16 05:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('adminAPI', '0003_alter_moderator_phone_number'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='rewards',
            new_name='Reward',
        ),
    ]
