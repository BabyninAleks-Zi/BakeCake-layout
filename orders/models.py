from django.conf import settings
from django.db import models

from catalog.models import CakeOption


class Order(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "Новый"
        ACCEPTED = "accepted", "Принят"
        IN_PROGRESS = "in_progress", "Готовится"
        DELIVERING = "delivering", "В доставке"
        COMPLETED = "completed", "Выполнен"
        CANCELLED = "cancelled", "Отменён"

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Пользователь",
    )
    level = models.ForeignKey(
        CakeOption,
        on_delete=models.PROTECT,
        related_name="level_orders",
        limit_choices_to={"kind": CakeOption.Kind.LEVEL},
        verbose_name="Количество уровней",
    )
    shape = models.ForeignKey(
        CakeOption,
        on_delete=models.PROTECT,
        related_name="shape_orders",
        limit_choices_to={"kind": CakeOption.Kind.SHAPE},
        verbose_name="Форма",
    )
    topping = models.ForeignKey(
        CakeOption,
        on_delete=models.PROTECT,
        related_name="topping_orders",
        limit_choices_to={"kind": CakeOption.Kind.TOPPING},
        verbose_name="Топпинг",
    )
    berry = models.ForeignKey(
        CakeOption,
        on_delete=models.PROTECT,
        related_name="berry_orders",
        limit_choices_to={"kind": CakeOption.Kind.BERRY},
        null=True,
        blank=True,
        verbose_name="Ягоды",
    )
    decor = models.ForeignKey(
        CakeOption,
        on_delete=models.PROTECT,
        related_name="decor_orders",
        limit_choices_to={"kind": CakeOption.Kind.DECOR},
        null=True,
        blank=True,
        verbose_name="Декор",
    )
    customer_name = models.CharField(
        max_length=100,
        verbose_name="Имя клиента",
    )
    customer_phone = models.CharField(
        max_length=20,
        verbose_name="Телефон",
    )
    customer_email = models.EmailField(
        verbose_name="Email",
    )
    delivery_address = models.CharField(
        max_length=255,
        verbose_name="Адрес доставки",
    )
    delivery_date = models.DateField(
        verbose_name="Дата доставки",
    )
    delivery_time = models.TimeField(
        verbose_name="Время доставки",
    )
    inscription = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Надпись",
    )
    order_comment = models.TextField(
        blank=True,
        verbose_name="Комментарий к заказу",
    )
    delivery_comment = models.TextField(
        blank=True,
        verbose_name="Комментарий для курьера",
    )
    utm_source = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="UTM source",
    )
    utm_medium = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="UTM medium",
    )
    utm_campaign = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="UTM campaign",
    )
    utm_content = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="UTM content",
    )
    utm_term = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="UTM term",
    )
    referrer = models.URLField(
        blank=True,
        verbose_name="Источник перехода",
    )
    landing_path = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Страница входа",
    )
    personal_data_consent = models.BooleanField(
        default=False,
        verbose_name="Согласие на обработку ПД",
    )
    options_total = models.PositiveIntegerField(
        default=0,
        verbose_name="Стоимость опций",
    )
    inscription_price = models.PositiveIntegerField(
        default=0,
        verbose_name="Стоимость надписи",
    )
    rush_fee = models.PositiveIntegerField(
        default=0,
        verbose_name="Наценка за срочность",
    )
    total_price = models.PositiveIntegerField(
        default=0,
        verbose_name="Итоговая стоимость",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
        verbose_name="Статус",
    )
    payment_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="ID платежа в YooKassa",
    )
    payment_status = models.CharField(
        max_length=50,
        blank=True,
        default="",
        verbose_name="Статус оплаты YooKassa",
    )
    is_paid = models.BooleanField(
        default=False,
        verbose_name="Оплачено",
    )
    paid_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Дата оплаты",
    )
    confirmation_url = models.URLField(
        blank=True,
        null=True,
        verbose_name="Ссылка на оплату",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Создан",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Обновлён",
    )

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ("-created_at",)

    def __str__(self):
        return f"Заказ #{self.pk} - {self.customer_name}"
