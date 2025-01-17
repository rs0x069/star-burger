# Generated by Django 3.2 on 2022-05-22 10:44

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='GeoAddress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(max_length=128, unique=True, verbose_name='Адрес')),
                ('lat', models.DecimalField(decimal_places=15, help_text='latitude, lat', max_digits=17, verbose_name='Координаты: широта')),
                ('lng', models.DecimalField(decimal_places=15, help_text='longitude, lng', max_digits=17, verbose_name='Координаты: долгота')),
                ('update_date', models.DateField(blank=True, db_index=True, null=True, verbose_name='Дата обновления координат')),
            ],
        ),
    ]
