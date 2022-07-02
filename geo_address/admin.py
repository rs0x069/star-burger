from django.contrib import admin

from geo_address.models import GeoAddress


@admin.register(GeoAddress)
class GeoAddressAdmin(admin.ModelAdmin):
    readonly_fields = ('update_date',)

