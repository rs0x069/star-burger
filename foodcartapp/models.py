from django.core.validators import MinValueValidator, MaxValueValidator, DecimalValidator
from django.db import models
from django.db.models import Sum, F
from phonenumber_field.modelfields import PhoneNumberField


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
    def all_with_costs(self):
        order_cost = self.annotate(cost=Sum(F('order_products__product__price') * F('order_products__quantity')))
        return order_cost


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

    objects = OrderQuerySet.as_manager()

    class Meta:
        verbose_name_plural = 'Заказы'
        verbose_name = 'Заказ'

    def __str__(self):
        return f'{self.firstname} {self.lastname}, {self.address}'


class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_products', verbose_name='Заказ')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='products_in_order',
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
