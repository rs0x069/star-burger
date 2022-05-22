from django import forms
from django.conf import settings
from django.db.models import F, Sum
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from geopy import distance

from foodcartapp.models import Product, Restaurant, Order, OrderProduct
from restaurateur.yandex_geocoder import fetch_coordinates


class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={
            'form': form
        })

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(request, "login.html", context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = list(Restaurant.objects.order_by('name'))
    products = list(Product.objects.prefetch_related('menu_items'))

    default_availability = {restaurant.id: False for restaurant in restaurants}
    products_with_restaurants = []
    for product in products:

        availability = {
            **default_availability,
            **{item.restaurant_id: item.availability for item in product.menu_items.all()},
        }
        orderer_availability = [availability[restaurant.id] for restaurant in restaurants]

        products_with_restaurants.append(
            (product, orderer_availability)
        )

    return render(request, template_name="products_list.html", context={
        'products_with_restaurants': products_with_restaurants,
        'restaurants': restaurants,
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name="restaurants_list.html", context={
        'restaurants': Restaurant.objects.all(),
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    yandex_api = settings.YANDEX_API

    orders = Order.objects.all_with_costs().exclude(status='CLOSED')

    orders_with_restaurants = []
    for order in orders:
        # \\TODO: Make suitable restaurants than can make whole order
        suitable_restaurants = []
        product_in_restaurants = []
        for order_products in order.order_products.all():
            product_in_restaurants.append(order_products.product.menu_items.filter(availability=True))
        # for restaurant in product_restaurants:
        #     if restaurant not in suitable_restaurants:
        #         suitable_restaurants.append(restaurant)
        for i in range(len(product_in_restaurants)):
            for j in range(len(product_in_restaurants[i])):
                order_distance = None
                restaurant = product_in_restaurants[i][j].restaurant

                restaurant_geocode = fetch_coordinates(yandex_api, restaurant.address)
                order_geocode = fetch_coordinates(yandex_api, order.address)
                if restaurant_geocode is not None and order_geocode is not None:
                    order_distance = distance.distance(restaurant_geocode, order_geocode).km

                suitable_restaurants.append({'name': restaurant.name, 'distance': str(order_distance)})

        orders_with_restaurants.append(
            (order, sorted(suitable_restaurants, key=lambda d: d['distance']))
        )

    context = {
        'orders': orders_with_restaurants,
    }

    return render(request, template_name='order_items.html', context=context)
