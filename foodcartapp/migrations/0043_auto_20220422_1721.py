# Generated by Django 3.2 on 2022-04-22 17:21

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0042_auto_20220407_1841'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderproduct',
            name='price',
            field=models.DecimalField(decimal_places=2, default=1, max_digits=8, validators=[django.core.validators.DecimalValidator], verbose_name='Стоимость'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='orderproduct',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_products', to='foodcartapp.order', verbose_name='Заказ'),
        ),
    ]
