from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

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


@api_view(['POST'])
def register_order(request):
    new_order = request.data

    if 'products' not in new_order:
        return Response({'error': 'Key \'products\' must be presented'}, status=status.HTTP_406_NOT_ACCEPTABLE)

    if not isinstance(new_order['products'], list):
        return Response({'error': 'Product key is not type of list'}, status=status.HTTP_406_NOT_ACCEPTABLE)

    if not new_order['products']:
        return Response({'error': 'List of products must be presented'}, status=status.HTTP_406_NOT_ACCEPTABLE)

    order = Order.objects.create(
        address=new_order['address'],
        firstname=new_order['firstname'],
        lastname=new_order['lastname'],
        phonenumber=new_order['phonenumber']
    )

    for new_order_product in new_order['products']:
        product = Product.objects.get(pk=new_order_product['product'])

        order_product = OrderProduct(order=order)
        order_product.product = product
        order_product.quantity = new_order_product['quantity']

        order_product.save()

    return Response({'status': 'Order is added'})
