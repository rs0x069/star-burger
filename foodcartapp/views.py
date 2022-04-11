from django.http import JsonResponse
from django.templatetags.static import static
from phonenumber_field.phonenumber import PhoneNumber
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

    required_keys = ['products', 'firstname', 'lastname', 'phonenumber', 'address']
    for key in required_keys:
        if key not in new_order:
            return Response({'error': f'Key \'{key}\' must be presented'}, status=status.HTTP_406_NOT_ACCEPTABLE)

    for key, value in new_order.items():
        if not value:
            return Response({'error': f'The field of key \'{key}\' cannot be empty or null'},
                            status=status.HTTP_406_NOT_ACCEPTABLE)

    new_order_address = new_order['address']
    new_order_firstname = new_order['firstname']
    new_order_lastname = new_order['lastname']
    new_order_phonenumber = new_order['phonenumber']
    new_order_products = new_order['products']

    if not isinstance(new_order_products, list):
        return Response({'error': 'The key \'products\' is not type of list'}, status=status.HTTP_406_NOT_ACCEPTABLE)
    if not isinstance(new_order_firstname, str):
        return Response({'error': 'The key \'firstname\' is not type of str'}, status=status.HTTP_406_NOT_ACCEPTABLE)
    if not isinstance(new_order_lastname, str):
        return Response({'error': 'The key \'lastname\' is not type of str'}, status=status.HTTP_406_NOT_ACCEPTABLE)
    if not isinstance(new_order_phonenumber, str):
        return Response({'error': 'The key \'phonenumber\' is not type of str'}, status=status.HTTP_406_NOT_ACCEPTABLE)
    if not isinstance(new_order_address, str):
        return Response({'error': 'The key \'address\' is not type of str'}, status=status.HTTP_406_NOT_ACCEPTABLE)

    is_phonenumber_valid = PhoneNumber.from_string(phone_number=new_order_phonenumber).is_valid()
    if not is_phonenumber_valid:
        return Response({'error': 'Phonenumber is not valid'}, status=status.HTTP_406_NOT_ACCEPTABLE)

    for new_order_product in new_order_products:
        try:
            Product.objects.get(pk=new_order_product['product'])
        except Product.DoesNotExist:
            return Response({'error': 'The product could not be found'}, status=status.HTTP_404_NOT_FOUND)

    order = Order.objects.create(
        address=new_order_address,
        firstname=new_order_firstname,
        lastname=new_order_lastname,
        phonenumber=new_order_phonenumber
    )

    for new_order_product in new_order_products:
        product = Product.objects.get(pk=new_order_product['product'])

        order_product = OrderProduct(order=order)
        order_product.product = product
        order_product.quantity = new_order_product['quantity']

        order_product.save()

    return Response({'status': 'Order is added'})
