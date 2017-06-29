# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-06-29 08:13
from __future__ import unicode_literals

from decimal import Decimal
import django.core.validators
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PurchaseItems',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.IntegerField(default=Decimal('1'))),
                ('sku', models.CharField(max_length=32, verbose_name='SKU')),
                ('quantity', models.IntegerField(default=Decimal('1'), validators=[django.core.validators.MinValueValidator(0)], verbose_name='quantity')),
                ('product_name', models.CharField(max_length=128, verbose_name='product name')),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='PurchaseOrder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[(b'pending', 'Processing'), (b'cancelled', 'Cancelled'), (b'shipped', 'sent'), (b'payment-pending', 'Payment pending'), (b'fully-paid', 'Fully paid')], default=b'pending', max_length=32, verbose_name='purchase order status')),
                ('created', models.DateTimeField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('last_status_change', models.DateTimeField(default=django.utils.timezone.now, editable=False, verbose_name='last status change')),
                ('language_code', models.CharField(default='en-us', max_length=35)),
                ('user_email', models.EmailField(blank=True, default='', editable=False, max_length=254, verbose_name='user email')),
                ('lfo_number', models.CharField(max_length=36, null=True, verbose_name='local purchase order number')),
            ],
            options={
                'ordering': ('-last_status_change',),
                'verbose_name': 'PurchaseOrder',
                'verbose_name_plural': 'PurchaseOrder',
            },
        ),
    ]
