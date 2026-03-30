from datetime import date, time

from django.conf import settings
from django.db import models

from catalog.models import CakeOption, CatalogCake


class PromoCode(models.Model):
    class DiscountType(models.TextChoices):
        FIXED = "fixed", "Фиксированная скидка"
        PERCENT = "percent", "Скидка в процентах"

    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Промокод",
    )
    discount_type = models.CharField(
        max_length=20,
        choices=DiscountType.choices,
        default=DiscountType.FIXED,
        verbose_name="Тип скидки",
    )
    discount_value = models.PositiveIntegerField(
        verbose_name="Размер скидки",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активен",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Создан",
    )

    class Meta:
        verbose_name = "Промокод"
        verbose_name_plural = "Промокоды"
        ordering = ("code",)

    def __str__(self):
        return self.code


class Order(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "Новый"
        ACCEPTED = "accepted", "Принят"
        IN_PROGRESS = "in_progress", "Готовится"
        DELIVERING = "delivering", "В доставке"
        COMPLETED = "completed", "Выполнен"
        CANCELLED = "cancelled", "Отменён"

    PAYMENT_STATUS_LABELS = {
        "": "Оплата не начата",
        "pending": "Ожидает оплату",
        "waiting_for_capture": "Оплата подтверждается",
        "succeeded": "Оплата получена",
        "canceled": "Оплата отменена",
    }

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Пользователь",
    )
    promo_code = models.ForeignKey(
        PromoCode,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
        verbose_name="Промокод",
    )
    catalog_cake = models.ForeignKey(
        CatalogCake,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="orders",
        verbose_name="Торт из каталога",
    )
    level = models.ForeignKey(
        CakeOption,
        on_delete=models.PROTECT,
        related_name="level_orders",
        limit_choices_to={"kind": CakeOption.Kind.LEVEL},
        null=True,
        blank=True,
        verbose_name="Количество уровней",
    )
    shape = models.ForeignKey(
        CakeOption,
        on_delete=models.PROTECT,
        related_name="shape_orders",
        limit_choices_to={"kind": CakeOption.Kind.SHAPE},
        null=True,
        blank=True,
        verbose_name="Форма",
    )
    topping = models.ForeignKey(
        CakeOption,
        on_delete=models.PROTECT,
        related_name="topping_orders",
        limit_choices_to={"kind": CakeOption.Kind.TOPPING},
        null=True,
        blank=True,
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
    delivery_eta = models.CharField(
        max_length=120,
        blank=True,
        verbose_name="Интервал доставки",
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
    discount_amount = models.PositiveIntegerField(
        default=0,
        verbose_name="Сумма скидки",
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
    customer_complaint = models.TextField(
        blank=True,
        verbose_name="Жалоба клиента",
    )
    complaint_created_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Жалоба создана",
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

    def cake_name(self):
        """Возвращает краткое название торта."""
        if self.catalog_cake:
            return self.catalog_cake.name

        if self.level and self.shape:
            return f"{self.level.name}, {self.shape.name}"

        return "Торт не указан"

    def status_text(self):
        """Возвращает понятный статус заказа."""
        return self.get_status_display()

    def payment_status_text(self):
        """Возвращает понятный статус оплаты."""
        return self.PAYMENT_STATUS_LABELS.get(
            self.payment_status,
            "Статус оплаты уточняется",
        )

    def delivery_eta_text(self):
        """Возвращает текст по сроку доставки."""
        if self.delivery_eta:
            return self.delivery_eta

        if isinstance(self.delivery_date, str):
            delivery_date_value = date.fromisoformat(self.delivery_date)
        else:
            delivery_date_value = self.delivery_date

        if isinstance(self.delivery_time, str):
            delivery_time_value = time.fromisoformat(self.delivery_time)
        else:
            delivery_time_value = self.delivery_time

        if hasattr(delivery_date_value, "strftime"):
            delivery_date = delivery_date_value.strftime("%d.%m.%Y")
        else:
            delivery_date = str(delivery_date_value)

        if hasattr(delivery_time_value, "strftime"):
            delivery_time = delivery_time_value.strftime("%H:%M")
        else:
            delivery_time = str(delivery_time_value)[:5]

        return f"{delivery_date} к {delivery_time}"

    def can_repeat(self):
        """Показывает, можно ли повторить заказ."""
        return bool(self.catalog_cake or (self.level and self.shape and self.topping))

    def can_complain(self):
        """Показывает, можно ли оставить жалобу по заказу."""
        return not bool(self.customer_complaint)
