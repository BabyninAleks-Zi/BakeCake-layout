from datetime import timedelta
from unittest.mock import patch

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

    @patch("orders.views.create_payment")
    def test_creates_order_and_redirects_to_payment(self, create_payment_mock):
        delivery_dt = timezone.localtime() + timedelta(days=2)
        create_payment_mock.return_value = {
            "payment_id": "pay_123",
            "confirmation_url": "https://example.com/pay/123",
            "status": "pending",
        }

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
        self.assertRedirects(
            response,
            reverse("orders:payment_create"),
            fetch_redirect_response=False,
        )

        payment_response = self.client.get(reverse("orders:payment_create"))
        self.assertRedirects(
            payment_response,
            "https://example.com/pay/123",
            fetch_redirect_response=False,
        )

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

    def test_reuses_existing_confirmation_url(self):
        order = Order.objects.create(
            level=self.level,
            shape=self.shape,
            topping=self.topping,
            berry=self.berry,
            decor=self.decor,
            customer_name="Ирина",
            customer_phone="+79990000000",
            customer_email="irina@example.com",
            delivery_address="Москва, Тверская 1",
            delivery_date="2026-03-30",
            delivery_time="12:00",
            personal_data_consent=True,
            options_total=1780,
            inscription_price=500,
            rush_fee=0,
            total_price=2280,
            payment_id="pay_existing",
            payment_status="pending",
            confirmation_url="https://example.com/pay/existing",
        )
        session = self.client.session
        session["pending_order_id"] = order.id
        session.save()

        response = self.client.get(reverse("orders:payment_create"))

        self.assertRedirects(
            response,
            "https://example.com/pay/existing",
            fetch_redirect_response=False,
        )

    def test_create_order_saves_utm_data_from_session(self):
        delivery_dt = timezone.localtime() + timedelta(days=2)

        self.client.get(
            "/",
            {
                "utm_source": "yandex",
                "utm_medium": "cpc",
                "utm_campaign": "cakes_launch",
            },
            HTTP_REFERER="https://example.com/ad/",
        )

        response = self.client.post(
            reverse("orders:create"),
            data={
                "level": self.level.id,
                "shape": self.shape.id,
                "topping": self.topping.id,
                "customer_name": "Ирина",
                "customer_phone": "+79990000000",
                "customer_email": "irina@example.com",
                "delivery_address": "Москва, Тверская 1",
                "delivery_date": delivery_dt.date(),
                "delivery_time": delivery_dt.time().replace(second=0, microsecond=0),
                "personal_data_consent": "on",
            },
        )

        order = Order.objects.latest("id")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(order.utm_source, "yandex")
        self.assertEqual(order.utm_medium, "cpc")
        self.assertEqual(order.utm_campaign, "cakes_launch")
        self.assertEqual(order.referrer, "https://example.com/ad/")
        self.assertIn("utm_source=yandex", order.landing_path)

    @patch("orders.views.get_payment_info")
    def test_callback_marks_order_as_paid_by_order_id(self, get_payment_info_mock):
        order = Order.objects.create(
            level=self.level,
            shape=self.shape,
            topping=self.topping,
            customer_name="Ирина",
            customer_phone="+79990000000",
            customer_email="irina@example.com",
            delivery_address="Москва, Тверская 1",
            delivery_date="2026-03-30",
            delivery_time="12:00",
            personal_data_consent=True,
            options_total=1200,
            inscription_price=0,
            rush_fee=0,
            total_price=1200,
            payment_id="pay_123",
            payment_status="pending",
        )
        get_payment_info_mock.return_value = {
            "id": "pay_123",
            "status": "succeeded",
            "paid": True,
            "amount": "1200.00",
        }

        response = self.client.get(
            reverse("orders:payment_callback"),
            {"order_id": order.id},
        )

        order.refresh_from_db()
        self.assertTrue(order.is_paid)
        self.assertEqual(order.payment_status, "succeeded")
        self.assertRedirects(
            response,
            reverse("orders:success", kwargs={"order_id": order.id}),
            fetch_redirect_response=False,
        )

    @patch("orders.views.get_payment_info")
    def test_callback_keeps_pending_order_for_retry(self, get_payment_info_mock):
        order = Order.objects.create(
            level=self.level,
            shape=self.shape,
            topping=self.topping,
            customer_name="Ирина",
            customer_phone="+79990000000",
            customer_email="irina@example.com",
            delivery_address="Москва, Тверская 1",
            delivery_date="2026-03-30",
            delivery_time="12:00",
            personal_data_consent=True,
            options_total=1200,
            inscription_price=0,
            rush_fee=0,
            total_price=1200,
            payment_id="pay_124",
            payment_status="pending",
        )
        get_payment_info_mock.return_value = {
            "id": "pay_124",
            "status": "pending",
            "paid": False,
            "amount": "1200.00",
        }

        response = self.client.get(
            reverse("orders:payment_callback"),
            {"order_id": order.id},
        )

        order.refresh_from_db()
        self.assertFalse(order.is_paid)
        self.assertEqual(order.payment_status, "pending")
        self.assertEqual(self.client.session.get("pending_order_id"), order.id)
        self.assertRedirects(
            response,
            reverse("orders:success", kwargs={"order_id": order.id}),
            fetch_redirect_response=False,
        )
