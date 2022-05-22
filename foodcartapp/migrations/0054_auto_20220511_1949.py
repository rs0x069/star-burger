# Generated by Django 3.2 on 2022-05-11 19:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0053_order_payment_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='payment_type',
            field=models.CharField(choices=[('NOTSET', 'Не установлено'), ('CASH', 'Наличными'), ('ELECTRONIC', 'Электронно')], db_index=True, default='NOTSET', max_length=10, verbose_name='Способ оплаты'),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('NEW', 'Необработанный'), ('COOKING', 'Готовится'), ('CLOSED', 'Закрыт')], db_index=True, default='NEW', max_length=7, verbose_name='Статус'),
        ),
    ]
