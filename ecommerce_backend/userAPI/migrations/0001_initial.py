# Generated by Django 4.2.4 on 2023-08-24 07:37

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=200)),
                ('phone_number', models.IntegerField()),
                ('address', models.TextField()),
                ('payment_method', models.CharField(choices=[('cod', 'cod'), ('mobile', 'mobile')], max_length=50)),
                ('inside_dhaka', models.BooleanField(default=False)),
                ('user_type', models.CharField(choices=[('user', 'user'), ('admin', 'admin')], max_length=20)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
