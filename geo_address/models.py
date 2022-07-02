from django.db import models


class GeoAddress(models.Model):
    address = models.CharField(max_length=128, verbose_name='Адрес', unique=True)
    lat = models.DecimalField(max_digits=17, decimal_places=15, verbose_name="Координаты: широта",
                              help_text="latitude, lat")
    lon = models.DecimalField(max_digits=17, decimal_places=15, verbose_name="Координаты: долгота",
                              help_text="longitude, lon")
    update_date = models.DateField(auto_now=True, verbose_name='Дата обновления координат', db_index=True)

    class Meta:
        verbose_name_plural = 'Координаты адресов'
        verbose_name = 'Координаты адресов'

    def __str__(self):
        return f'{self.address} - lat: {self.lat}, lng: {self.lon}'
