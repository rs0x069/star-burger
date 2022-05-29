# Generated by Django 3.2 on 2022-05-06 20:15

import datetime
from django.db import migrations, models
import django.utils.timezone
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0050_order_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='called_datetime',
            field=models.DateTimeField(blank=True, db_index=True, default=django.utils.timezone.now, verbose_name='Дата и время звонка'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='order',
            name='delivered_datetime',
            field=models.DateTimeField(blank=True, db_index=True, default=django.utils.timezone.now, verbose_name='Дата и время доставки'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='order',
            name='registered_datetime',
            field=models.DateTimeField(auto_now_add=True, db_index=True, default=django.utils.timezone.now, verbose_name='Дата и время создания'),
            preserve_default=False,
        ),
    ]