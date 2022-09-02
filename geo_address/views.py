from geo_address.models import GeoAddress
from geo_address.yandex_geocoder import fetch_coordinates


def get_coordinates(address):
    try:
        return GeoAddress.objects.values_list('lat', 'lon').get(address=address)
    except GeoAddress.DoesNotExist:
        coordinates = fetch_coordinates(address)
        if coordinates:
            order_address_lat, order_address_lon = coordinates
            GeoAddress.objects.get_or_create(address=address, lat=order_address_lat, lon=order_address_lon)

        return coordinates
