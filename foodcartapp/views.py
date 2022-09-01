from django.db import transaction
from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer, ListField

from foodcartapp.models import Product, Order, OrderProduct
from geo_address.models import GeoAddress
from geo_address.yandex_geocoder import fetch_coordinates


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


class OrderProductSerializer(ModelSerializer):
    class Meta:
        model = OrderProduct
        fields = ['product', 'quantity']


class OrderSerializer(ModelSerializer):
    products = ListField(child=OrderProductSerializer(), allow_empty=False, write_only=True)

    class Meta:
        model = Order
        fields = ['id', 'products', 'firstname', 'lastname', 'phonenumber', 'address']

    def create(self, validated_data):

        order_address = validated_data.get('address')
        coordinates = fetch_coordinates(order_address)
        if coordinates:
            order_address_lat, order_address_lon = coordinates
            GeoAddress.objects.get_or_create(address=order_address, lat=order_address_lat, lon=order_address_lon)

        products = validated_data.pop('products')
        with transaction.atomic():
            order = Order.objects.create(**validated_data)
            order_content = [
                OrderProduct(
                    order=order,
                    product=product['product'],
                    quantity=product['quantity'],
                    cost=product['product'].price * product['quantity']
                ) for product in products
            ]
            OrderProduct.objects.bulk_create(order_content)
            return order


@api_view(['POST'])
def register_order(request):
    new_order = OrderSerializer(data=request.data)
    if new_order.is_valid(raise_exception=True):
        new_order.save()
        return Response(new_order.data, status=status.HTTP_200_OK)
    return Response(new_order.errors, status=status.HTTP_400_BAD_REQUEST)
