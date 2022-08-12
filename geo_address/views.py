from geo_address.models import GeoAddress
from geo_address.yandex_geocoder import fetch_coordinates


def get_coordinates(address):
    try:
        return GeoAddress.objects.values_list('lat', 'lon').get(address=address)
    except GeoAddress.DoesNotExist:
        return fetch_coordinates(address)
