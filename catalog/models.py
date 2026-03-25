from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy

class CakeLevel(models.Model):
    level_count = models.IntegerField(
        verbose_name='Количество уровней',
        validators=[
            MinValueValidator(1)
        ]
    )
    price = models.IntegerField(
        verbose_name='Стоимость',
    )

    class Meta:
        verbose_name = 'Уровень торта'
        verbose_name_plural = 'Уровни торта'

    def __str__(self):
        return f'{self.level_count}'


class CakeShape(models.Model):
    shape = models.CharField(
        max_length=50,
        verbose_name='Форма',
    )
    price = models.IntegerField(
        verbose_name='Стоимость',
    )

    class Meta:
        verbose_name = 'Форма торта'
        verbose_name_plural = 'Формы торта'

    def __str__(self):
        return self.shape


class CakeTopping(models.Model):
    cake_topping = models.CharField(
        max_length=50,
        verbose_name='Топпинг',
    )
    price = models.IntegerField(
        verbose_name='Стоимость',
    )

    class Meta:
        verbose_name = 'Топпинг'
        verbose_name_plural = 'Топпинги'

    def __str__(self):
        return self.cake_topping


class CakeBerry(models.Model):
    cake_berry = models.CharField(
        max_length=15,
        verbose_name='Ягоды',
    )
    price = models.IntegerField(
        verbose_name='Стоимость',
    )

    class Meta:
        verbose_name = 'Ягода'
        verbose_name_plural = 'Ягоды'

    def __str__(self):
        return self.cake_berry


class CakeDecor(models.Model):
    cake_decor = models.CharField(
        max_length=15,
        verbose_name='Декор'
    )
    price = models.IntegerField(
        verbose_name='Стоимость',
    )

    class Meta:
        verbose_name = 'Декор'
        verbose_name_plural = 'Декор'

    def __str__(self):
        return self.cake_decor


class Cake(models.Model):
    level_count = models.ForeignKey(
        CakeLevel,
        verbose_name='Количество уровней торта',
        related_name='levels',
        on_delete=models.CASCADE
    )
    shape = models.ForeignKey(
        CakeShape,
        verbose_name='Форма торта',
        related_name='shapes',
        on_delete=models.CASCADE
    )
    topping = models.ForeignKey(
        CakeTopping,
        verbose_name='Топпинг',
        related_name='toppings',
        on_delete=models.CASCADE
    )
    berry = models.ForeignKey(
        CakeBerry,
        verbose_name='Ягоды',
        related_name='berries',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    decor = models.ForeignKey(
        CakeDecor,
        verbose_name='Декор',
        related_name='decors',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    inscription = models.CharField(
        max_length=200,
        verbose_name='Надпись на торте',
        blank=True
    )
    comment = models.TextField(
        verbose_name='Комментарий',
        blank=True
    )

    class Meta:
        verbose_name = 'Торт'
        verbose_name_plural = 'Торты'

    def __str__(self):
        return f'Торт {self.level_count} уровневый - форма {self.shape}'

# Create your models here.
