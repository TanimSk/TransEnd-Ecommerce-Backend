# Generated by Django 4.2.4 on 2023-10-10 18:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminAPI', '0005_alter_moderator_admin_roles'),
    ]

    operations = [
        migrations.AddField(
            model_name='moderator',
            name='password_text',
            field=models.CharField(default='', max_length=200),
        ),
    ]
