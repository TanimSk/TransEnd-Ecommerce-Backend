# Generated by Django 4.2.4 on 2023-12-23 07:23

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminAPI', '0007_alter_notice_notice'),
    ]

    operations = [
        migrations.CreateModel(
            name='HeroContent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('images', django.contrib.postgres.fields.ArrayField(base_field=models.URLField(), blank=True, default=list, size=None)),
                ('main_heading', models.CharField(max_length=100)),
                ('primary_heading', models.CharField(max_length=200)),
                ('secondary_heading', models.CharField(max_length=200)),
            ],
        ),
    ]