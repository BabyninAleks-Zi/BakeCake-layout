from django.db import models
from django.utils.text import slugify


class CakeOption(models.Model):
    class Kind(models.TextChoices):
        LEVEL = "level", "Количество уровней"
        SHAPE = "shape", "Форма"
        TOPPING = "topping", "Топпинг"
        BERRY = "berry", "Ягоды"
        DECOR = "decor", "Декор"

    kind = models.CharField(
        max_length=20,
        choices=Kind.choices,
        verbose_name="Тип опции",
    )
    name = models.CharField(
        max_length=100,
        verbose_name="Название",
    )
    price = models.PositiveIntegerField(
        verbose_name="Стоимость",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активна",
    )
    sort_order = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="Порядок сортировки",
    )

    class Meta:
        verbose_name = "Опция торта"
        verbose_name_plural = "Опции торта"
        ordering = ("kind", "sort_order", "id")
        constraints = [
            models.UniqueConstraint(
                fields=("kind", "name"),
                name="catalog_cakeoption_kind_name_unique",
            )
        ]

    def __str__(self):
        return f"{self.get_kind_display()}: {self.name}"


class CatalogCake(models.Model):
    name = models.CharField(
        max_length=150,
        verbose_name="Название",
    )
    slug = models.SlugField(
        max_length=160,
        unique=True,
        verbose_name="URL-имя",
    )
    occasion = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Повод",
    )
    description = models.TextField(
        blank=True,
        verbose_name="Описание",
    )
    image = models.ImageField(
        upload_to="catalog/cakes/",
        blank=True,
        verbose_name="Изображение",
    )
    base_price = models.PositiveIntegerField(
        verbose_name="Базовая цена",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активен",
    )
    sort_order = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="Порядок сортировки",
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
        verbose_name = "Торт из каталога"
        verbose_name_plural = "Торты из каталога"
        ordering = ("sort_order", "id")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
