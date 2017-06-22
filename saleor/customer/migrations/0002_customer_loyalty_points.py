# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-06-22 13:13
from __future__ import unicode_literals

from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='loyalty_points',
            field=models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=100, verbose_name='loyalty points'),
        ),
    ]
