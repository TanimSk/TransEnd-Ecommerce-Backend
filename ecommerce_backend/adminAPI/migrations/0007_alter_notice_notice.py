# Generated by Django 4.2.4 on 2023-10-25 18:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminAPI', '0006_moderator_password_text'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notice',
            name='notice',
            field=models.CharField(default='', max_length=500),
        ),
    ]