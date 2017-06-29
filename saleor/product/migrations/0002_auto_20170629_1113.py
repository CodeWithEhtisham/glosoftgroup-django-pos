# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-06-29 08:13
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('product', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('supplier', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='stockhistoryentry',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='user'),
        ),
        migrations.AddField(
            model_name='stock',
            name='location',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='product.StockLocation'),
        ),
        migrations.AddField(
            model_name='stock',
            name='variant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stock', to='product.ProductVariant', verbose_name='variant'),
        ),
        migrations.AddField(
            model_name='productvariant',
            name='images',
            field=models.ManyToManyField(through='product.VariantImage', to='product.ProductImage', verbose_name='images'),
        ),
        migrations.AddField(
            model_name='productvariant',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='variants', to='product.Product'),
        ),
        migrations.AddField(
            model_name='productimage',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='product.Product', verbose_name='product'),
        ),
        migrations.AddField(
            model_name='productclass',
            name='product_attributes',
            field=models.ManyToManyField(blank=True, related_name='products_class', to='product.ProductAttribute', verbose_name='product attributes'),
        ),
        migrations.AddField(
            model_name='productclass',
            name='variant_attributes',
            field=models.ManyToManyField(blank=True, related_name='product_variants_class', to='product.ProductAttribute', verbose_name='variant attributes'),
        ),
        migrations.AddField(
            model_name='product',
            name='categories',
            field=models.ManyToManyField(related_name='products', to='product.Category', verbose_name='categories'),
        ),
        migrations.AddField(
            model_name='product',
            name='product_class',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='product.ProductClass', verbose_name='product class'),
        ),
        migrations.AddField(
            model_name='product',
            name='product_supplier',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='suppliers', to='supplier.Supplier', verbose_name='product supplier'),
        ),
        migrations.AddField(
            model_name='product',
            name='product_tax',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='producttax', to='product.ProductTax', verbose_name='product class'),
        ),
        migrations.AddField(
            model_name='category',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='product.Category', verbose_name='parent'),
        ),
        migrations.AddField(
            model_name='attributechoicevalue',
            name='attribute',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='values', to='product.ProductAttribute'),
        ),
        migrations.AlterUniqueTogether(
            name='stock',
            unique_together=set([('variant', 'location')]),
        ),
        migrations.AlterUniqueTogether(
            name='attributechoicevalue',
            unique_together=set([('name', 'attribute')]),
        ),
    ]
