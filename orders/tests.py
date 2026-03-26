from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from catalog.models import CakeOption
from orders.models import Order
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


class OrderCreateViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.level = CakeOption.objects.get(kind=CakeOption.Kind.LEVEL, name="1 уровень")
        cls.shape = CakeOption.objects.get(kind=CakeOption.Kind.SHAPE, name="Квадрат")
        cls.topping = CakeOption.objects.get(kind=CakeOption.Kind.TOPPING, name="Белый соус")
        cls.berry = CakeOption.objects.get(kind=CakeOption.Kind.BERRY, name="Малина")
        cls.decor = CakeOption.objects.get(kind=CakeOption.Kind.DECOR, name="Марципан")

    def test_creates_order_and_redirects_to_success_page(self):
        delivery_dt = timezone.localtime() + timedelta(days=2)

        response = self.client.post(
            reverse("orders:create"),
            data={
                "level": self.level.id,
                "shape": self.shape.id,
                "topping": self.topping.id,
                "berry": self.berry.id,
                "decor": self.decor.id,
                "inscription": "С днем рождения!",
                "order_comment": "Без орехов",
                "customer_name": "Ирина",
                "customer_phone": "+79990000000",
                "customer_email": "irina@example.com",
                "delivery_address": "Москва, Тверская 1",
                "delivery_date": delivery_dt.date(),
                "delivery_time": delivery_dt.time().replace(second=0, microsecond=0),
                "delivery_comment": "Позвонить за 10 минут",
                "personal_data_consent": "on",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Order.objects.count(), 1)

        order = Order.objects.first()
        self.assertEqual(order.customer_name, "Ирина")
        self.assertEqual(order.total_price, 2280)
        self.assertRedirects(response, reverse("orders:success", kwargs={"order_id": order.id}))

    def test_does_not_create_order_when_required_data_is_missing(self):
        response = self.client.post(
            reverse("orders:create"),
            data={
                "shape": self.shape.id,
                "topping": self.topping.id,
                "customer_name": "Ирина",
                "customer_phone": "+79990000000",
                "customer_email": "irina@example.com",
                "delivery_address": "Москва, Тверская 1",
                "delivery_date": "2026-03-30",
                "delivery_time": "12:00",
                "personal_data_consent": "on",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Order.objects.count(), 0)
        self.assertRedirects(response, reverse("core:index"))
