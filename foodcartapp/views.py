from django.http import JsonResponse
from django.templatetags.static import static
from phonenumber_field.phonenumber import PhoneNumber
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.serializers import ValidationError, Serializer, ModelSerializer, ListField

from .models import Product, Order, OrderProduct


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
    products = ListField(child=OrderProductSerializer(), allow_empty=False)

    class Meta:
        model = Order
        fields = ['products', 'address', 'firstname', 'lastname', 'phonenumber']


@api_view(['POST'])
def register_order(request):
    new_order = OrderSerializer(data=request.data)
    new_order.is_valid(raise_exception=True)

    order = Order.objects.create(
        address=new_order.validated_data['address'],
        firstname=new_order.validated_data['firstname'],
        lastname=new_order.validated_data['lastname'],
        phonenumber=new_order.validated_data['phonenumber']
    )

    new_order_products = new_order.validated_data['products']
    order_products = [OrderProduct(order=order, **fields) for fields in new_order_products]
    OrderProduct.objects.bulk_create(order_products)

    return Response({'status': 'Order is added'})
