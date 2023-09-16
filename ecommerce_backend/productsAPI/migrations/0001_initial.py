# Generated by Django 4.2.4 on 2023-09-16 04:41

import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('vendorAPI', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('images', django.contrib.postgres.fields.ArrayField(base_field=models.URLField(), blank=True, default=list, size=None)),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('details', models.TextField(blank=True)),
                ('tags', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=500), blank=True, default=list, size=None)),
                ('price_bdt', models.IntegerField()),
                ('price_usd', models.FloatField(default=0)),
                ('price_gbp', models.FloatField(default=0)),
                ('price_eur', models.FloatField(default=0)),
                ('price_cad', models.FloatField(default=0)),
                ('images', django.contrib.postgres.fields.ArrayField(base_field=models.URLField(), blank=True, default=list, size=None)),
                ('quantity', models.IntegerField()),
                ('rewards', models.IntegerField(default=0)),
                ('grant', models.IntegerField(default=0)),
                ('discount_percent', models.IntegerField(default=0)),
                ('discount_max_bdt', models.IntegerField(default=0)),
                ('product_added_date', models.DateTimeField(auto_now=True)),
                ('quantity_sold', models.IntegerField(default=0)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='category', to='productsAPI.category')),
                ('vendor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vendor', to='vendorAPI.vendor')),
            ],
        ),
        migrations.CreateModel(
            name='FeaturedProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('section', models.CharField(choices=[('home', 'home'), ('category', 'category')], max_length=20)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='featured_products', to='productsAPI.product')),
            ],
        ),
    ]
