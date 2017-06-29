# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-06-29 08:13
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('cart', '0002_cartline_variant'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('discount', '0002_auto_20170629_1113'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='carts', to=settings.AUTH_USER_MODEL, verbose_name='user'),
        ),
        migrations.AddField(
            model_name='cart',
            name='voucher',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='discount.Voucher', verbose_name='token'),
        ),
        migrations.AlterUniqueTogether(
            name='cartline',
            unique_together=set([('cart', 'variant', 'data')]),
        ),
    ]
