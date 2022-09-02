import copy
from collections import defaultdict

from django.core.validators import MinValueValidator, MaxValueValidator, DecimalValidator
from django.db import models
from django.db.models import Sum, F, Prefetch
from geopy import distance
from phonenumber_field.modelfields import PhoneNumberField

from geo_address.views import get_coordinates


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class OrderQuerySet(models.QuerySet):
    def with_orders_sum(self):
        orders = self.annotate(cost=Sum(F('items__cost') * F('items__quantity')))
        return orders

    def with_suitable_restaurants(self):
        orders = self.prefetch_related(Prefetch('items', queryset=OrderProduct.objects.select_related('product')))

        ### Better way, requests to db is less ###
        # orders = self.prefetch_related(
        #     Prefetch('items', queryset=OrderProduct.objects.select_related('product'))
        # )
        # menu_items = RestaurantMenuItem.objects.select_related('restaurant', 'product').filter(availability=True)
        #
        # restaurants_by_items = defaultdict(list)
        # for menu_item in menu_items:
        #     restaurants_by_items[menu_item.product.id].append(menu_item.restaurant)

        for order in orders:
            ## Better way, requests to db is less ###
            # order_restaurants_by_items = [
            #     copy.deepcopy(restaurants_by_items[order_item.product.id])
            #     for order_item in order.items.all()
            # ]
            # order.suitable_restaurants = list(set.intersection(*[set(list) for list in order_restaurants_by_items]))

            product_in_restaurants = defaultdict(list)
            for order_item in order.items.all():
                # Похоже здесь можно использовать prefetch_related от модели Product к модели RestaurantMenuItem
                for menu_item in order_item.product.menu_items.filter(availability=True).select_related('restaurant'):
                    product_in_restaurants[order_item.product.id].append(menu_item.restaurant)
            order.suitable_restaurants = list(
                set.intersection(*[set(restaurant) for key, restaurant in product_in_restaurants.items()])
            )

            # coordinates = fetch_coordinates(order.address)
            # if coordinates:
            #     order_address_lat, order_address_lon = coordinates
            #     GeoAddress.objects.get_or_create(address=order.address, lat=order_address_lat, lon=order_address_lon)

            order_geocode_address = get_coordinates(order.address)
            for restaurant in order.suitable_restaurants:
                restaurant_geocode_address = get_coordinates(restaurant.address)
                restaurant.distance = round(distance.distance(restaurant_geocode_address, order_geocode_address).km, 2)
            order.suitable_restaurants = sorted(order.suitable_restaurants, key=lambda restaurant: restaurant.distance)

        return orders


class Order(models.Model):
    STATUS = (
        ('NEW', 'Необработанный'),
        ('COOKING', 'Готовится'),
        ('CLOSED', 'Закрыт')
    )
    PAYMENT_TYPE = (
        ('NOTSET', 'Не установлено'),
        ('CASH', 'Наличными'),
        ('ELECTRONIC', 'Электронно')
    )

    address = models.CharField(max_length=128, verbose_name='Адрес', db_index=True)
    firstname = models.CharField(max_length=64, verbose_name='Имя', db_index=True)
    lastname = models.CharField(max_length=64, verbose_name='Фамилия', db_index=True)
    phonenumber = PhoneNumberField(max_length=12, verbose_name='Мобильный телефон', db_index=True)
    status = models.CharField(max_length=7, choices=STATUS, default='NEW', verbose_name='Статус', db_index=True)
    comment = models.TextField(blank=True, verbose_name='Комментарий')
    registered_datetime = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время создания', db_index=True)
    called_datetime = models.DateTimeField(blank=True, null=True, verbose_name='Дата и время звонка', db_index=True)
    delivered_datetime = models.DateTimeField(blank=True, null=True, verbose_name='Дата и время доставки',
                                              db_index=True)
    payment_type = models.CharField(max_length=10, choices=PAYMENT_TYPE, default='NOTSET', verbose_name='Способ оплаты',
                                    db_index=True)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.SET_NULL, blank=True, null=True, related_name='orders',
                                   verbose_name='Ресторан')

    objects = OrderQuerySet.as_manager()

    class Meta:
        verbose_name_plural = 'Заказы'
        verbose_name = 'Заказ'

    def __str__(self):
        return f'{self.firstname} {self.lastname}, {self.address}'


class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name='Заказ')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_items',
                                verbose_name='Товар')
    quantity = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(100)], default=1,
                                   verbose_name='Количество')
    cost = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(0)],
                                verbose_name='Стоимость')

    class Meta:
        verbose_name_plural = 'Элементы заказа'
        verbose_name = 'Элемент заказа'

    def __str__(self):
        return f'{self.order} - {self.product} - {self.quantity}'

    def calculate_cost(self):
        self.cost = self.product.price * self.quantity
