# Generated by Django 3.2 on 2022-05-06 18:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0046_auto_20220423_1024'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('NEW', 'Необработанный'), ('CLOSED', 'Обработанный')], db_index=True, default='NEW', max_length=6),
        ),
    ]
