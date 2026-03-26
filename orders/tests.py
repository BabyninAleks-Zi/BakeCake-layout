from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from catalog.models import CakeOption
from orders.services import PricingError, calculate_custom_cake_price


class PricingServiceTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.level = CakeOption.objects.get(kind=CakeOption.Kind.LEVEL, name="1 уровень")
        cls.shape = CakeOption.objects.get(kind=CakeOption.Kind.SHAPE, name="Квадрат")
        cls.topping = CakeOption.objects.get(kind=CakeOption.Kind.TOPPING, name="Белый соус")
        cls.berry = CakeOption.objects.get(kind=CakeOption.Kind.BERRY, name="Малина")
        cls.decor = CakeOption.objects.get(kind=CakeOption.Kind.DECOR, name="Марципан")

    def test_calculates_price_without_optional_fields(self):
        result = calculate_custom_cake_price(
            level_id=self.level.id,
            shape_id=self.shape.id,
            topping_id=self.topping.id,
        )

        self.assertEqual(result["options_total"], 1200)
        self.assertEqual(result["inscription_price"], 0)
        self.assertEqual(result["rush_fee"], 0)
        self.assertEqual(result["total"], 1200)

    def test_adds_optional_options_and_inscription_price(self):
        result = calculate_custom_cake_price(
            level_id=self.level.id,
            shape_id=self.shape.id,
            topping_id=self.topping.id,
            berry_id=self.berry.id,
            decor_id=self.decor.id,
            inscription="С днем рождения!",
        )

        self.assertEqual(result["options_total"], 1780)
        self.assertEqual(result["inscription_price"], 500)
        self.assertEqual(result["rush_fee"], 0)
        self.assertEqual(result["total"], 2280)

    def test_adds_rush_fee_for_delivery_less_than_24_hours(self):
        delivery_dt = timezone.localtime() + timedelta(hours=6)

        result = calculate_custom_cake_price(
            level_id=self.level.id,
            shape_id=self.shape.id,
            topping_id=self.topping.id,
            inscription="Тест",
            delivery_date=delivery_dt.date(),
            delivery_time=delivery_dt.time().replace(second=0, microsecond=0),
        )

        self.assertEqual(result["total"], 2040)
        self.assertEqual(result["rush_fee"], 340)

    def test_raises_error_when_required_option_is_missing(self):
        with self.assertRaises(PricingError):
            calculate_custom_cake_price(
                level_id=None,
                shape_id=self.shape.id,
                topping_id=self.topping.id,
            )

    def test_raises_error_for_past_delivery_datetime(self):
        past_dt = timezone.localtime() - timedelta(hours=2)

        with self.assertRaises(PricingError):
            calculate_custom_cake_price(
                level_id=self.level.id,
                shape_id=self.shape.id,
                topping_id=self.topping.id,
                delivery_date=past_dt.date(),
                delivery_time=past_dt.time().replace(second=0, microsecond=0),
            )
