from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils import timezone
from django.urls import reverse

User = get_user_model()

def get_product_url(obj, viewname):
    ct_model = obj.__class__._meta.model_name
    return reverse(viewname, kwargs={'ct_model': ct_model, 'slug': obj.slug})


class CategoryManager(models.Manager):

    CATEGORY_NAME_COUNT_NAME = {
        'notebooks': 'notebook__count',
        'smartphones': 'smartphone__count'
    }
    
    def get_queryset(self):
        return super().get_queryset()

    def get_models_for_count(self, *model_names):
        return [models.Count(model_name) for model_name in model_names]

    def get_categories_for_left_sidebar(self):
        models = self.get_models_for_count('notebook', 'smartphone')
        qs = list(self.get_queryset().annotate(*models))
        data = [
            dict(name=c.name, url=c.get_url(), count=getattr(c, self.CATEGORY_NAME_COUNT_NAME[c.name]))
            for c in qs
        ]
        return data

        
class Category(models.Model):
    
    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    name = models.CharField(max_length=200, verbose_name='Название')
    slug = models.SlugField(unique=True)
    objects = CategoryManager()

    def __str__(self):
        return self.name

    def get_url(self):
        return reverse('category_detail', kwargs={'slug': self.slug})


class Product(models.Model):

    MIN_RESOLUTION = (400, 400)
    MAX_RESOLUTION = (800, 800)
    MAX_IMAGE_SIZE = 3145728

    class Meta:
        abstract = True

    category = models.ForeignKey(Category, verbose_name='Категория', on_delete=models.CASCADE)
    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=250, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Цена')
    image = models.ImageField(verbose_name='Изображение')

    def __str__(self):
        return self.title

    def get_url(self):
        return get_product_url(self, 'product_detail')

    def get_model_name(self):
        return self.__class__.__name__.lower()
        #return get_product_url(self, 'product_detail')


class Notebook(Product):

    class Meta:
        verbose_name = 'ноутбук' 
        verbose_name_plural = 'Ноутбуки'

    diagonal = models.CharField(max_length=250, verbose_name='Диагональ')
    display_type = models.CharField(max_length=250, verbose_name='Тип дисплея')
    ram = models.CharField(max_length=250, verbose_name='Оперативная память')
    processor_freq = models.CharField(max_length=250, verbose_name='Частота процессора')
    video = models.CharField(max_length=250, verbose_name='Видеокарта')
    time_without_charge = models.CharField(max_length=250, verbose_name='Время работы аккумулятора')
    os = models.CharField(max_length=250, verbose_name='Операционная система')


class Smartphone(Product):
    
    class Meta:
        verbose_name = 'смартфон' 
        verbose_name_plural = 'Смартфоны'
    
    diagonal = models.CharField(max_length=250, verbose_name='Диагональ')
    display_type = models.CharField(max_length=250, verbose_name='Тип дисплея')
    resolution = models.CharField(max_length=250, verbose_name='Разрешение экрана')
    
    ram = models.CharField(max_length=250, verbose_name='Оперативная память')
    accum_volume = models.CharField(max_length=250, verbose_name='Объем батареи')

    sd = models.BooleanField(default=False, verbose_name='SD карта')
    sd_volume = models.CharField(max_length=250, verbose_name='Максимальный объём sd карты', null=True, blank=True)

    main_cam = models.CharField(max_length=250, verbose_name='Задняя камера')
    frontal_cam = models.CharField(max_length=250, verbose_name='Фронтальная камера')


class Cart(models.Model):

    class Meta:
        verbose_name = 'корзина'
        verbose_name_plural = 'Корзины'

    owner = models.ForeignKey('Customer', verbose_name='Владелец', on_delete=models.CASCADE, null=True, blank=True)
    products = models.ManyToManyField('CartProduct', blank=True, related_name='products')
    #products = models.ManyToManyField(CartProduct, blank=True, related_name='related_cart')
    total_products = models.PositiveIntegerField(default=0)
    
    in_order = models.BooleanField(default=False)
    for_anonymous_user = models.BooleanField(default=False)
    
    final_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Общая цена', default=0)

    
    def __str__(self):
        return 'Корзина №' + str(self.id)


class CartProduct(models.Model):

    class Meta:
        verbose_name = 'продукт'
        verbose_name_plural = 'Продукты корзин'

    user = models.ForeignKey('Customer', verbose_name='Покупатель', on_delete=models.CASCADE)
    cart = models.ForeignKey('Cart', verbose_name='Корзина', on_delete=models.CASCADE)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    quantity = models.PositiveIntegerField(default=1)

    final_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Общая цена', default=0)

    def __str__(self):
        return 'Продукт %d корзины - %s' % (self.cart.id, self.content_object.title)

    def save(self, *args, **kwargs):
        self.final_price =self.quantity * self.content_object.price 
        super().save(*args, **kwargs)


class Customer(models.Model):
    
    class Meta:
        verbose_name = 'покупатель'
        verbose_name_plural = 'Покупатели'

    user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, verbose_name='Номер телефона', null=True, blank=True)
    address = models.CharField(max_length=250, verbose_name='Адрес', null=True, blank=True)
    orders = models.ManyToManyField('Order', verbose_name='Заказы пользователя', related_name='orders', blank=True)

    def __str__(self):
        return 'Покупатель %s %s' % (self.user.first_name, self.user.last_name)


class Order(models.Model):

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'Заказы'

    STATUS_DEFAULT = 'new'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_READY = 'ready'
    STATUS_COMPLETED = 'completed'

    STATUS_CHOICES = (
        (STATUS_DEFAULT, 'Новый'),
        (STATUS_IN_PROGRESS, 'В обработке'), 
        (STATUS_READY, 'Готов'),
        (STATUS_COMPLETED, 'Выполнен'),
    )

    DELIVERY_TYPE_DEFAULT = 'self'
    DELIVERY_TYPE_DELIVERY = 'delivery'

    DELIVERY_TYPE_CHOICES = (
        (DELIVERY_TYPE_DEFAULT, 'Самовывоз'), 
        (DELIVERY_TYPE_DELIVERY, 'Доставка'), 
    )

    customer = models.ForeignKey('Customer', verbose_name='Покупатель', on_delete=models.CASCADE)
    
    first_name = models.CharField(max_length=30, verbose_name='Имя покупателя')
    last_name = models.CharField(max_length=30, verbose_name='Фамилия покупателя')
    phone = models.CharField(max_length=20, verbose_name='Номер телефона', null=True, blank=True)
    address = models.CharField(max_length=255, verbose_name='Адрес', null=True, blank=True)

    cart = models.ForeignKey('Cart', verbose_name='Корзина', on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=100, verbose_name='Статус заказа', choices=STATUS_CHOICES, default=STATUS_DEFAULT)
    delivery_type = models.CharField(max_length=100, verbose_name='Тип доставки', choices=DELIVERY_TYPE_CHOICES, default=DELIVERY_TYPE_DEFAULT)

    created_at = models.DateTimeField(auto_now=True, verbose_name='Дата создания')
    order_date = models.DateField(default=timezone.now, verbose_name='Дата получения заказа')

    def __str__(self):
        return 'Заказ №%d' % (self.id)


class LatestProductsManager:

    @staticmethod
    def get_products_for_main_page(*args, **kwargs):
        with_respect_to = kwargs.get('with_respect_to')
        products = list()

        ct_models = ContentType.objects.filter(model__in=args)

        for ct_model in ct_models:
            model_products = ct_model.model_class()._base_manager.all().order_by('-id')[:5]
            products.extend(model_products)

        if with_respect_to and with_respect_to in args:
            ct_models = ContentType.objects.filter(model=with_respect_to)
            if ct_models.exists():
                products = sorted(
                    products, 
                    key=lambda x: x.__class__._meta.model_name.startswith(with_respect_to), reverse=True
                )

        return products


class LatestProducts:
    objects = LatestProductsManager()