# Generated by Django 4.2.4 on 2023-09-25 17:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminAPI', '0009_rename_discount_couponcode_discount_bdt_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='BookedCall',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(blank=True, max_length=50, null=True)),
                ('last_name', models.CharField(blank=True, max_length=50, null=True)),
                ('phone_number', models.CharField(max_length=100)),
                ('details', models.TextField(blank=True, null=True)),
                ('book_on', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.DeleteModel(
            name='BookedCalls',
        ),
    ]
