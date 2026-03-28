from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from accounts.models import Profile
from catalog.models import CakeOption
from orders.models import Order


User = get_user_model()


class AccountsViewsTests(TestCase):
    def test_anonymous_user_is_redirected_from_lk(self):
        response = self.client.get(reverse("accounts:lk"))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"{reverse('core:index')}?next={reverse('accounts:lk')}")

    def test_authenticated_user_can_open_lk(self):
        user = User.objects.create_user(username="+79990000000", password="test-pass")
        self.client.force_login(user)

        response = self.client.get(reverse("accounts:lk"))

        self.assertEqual(response.status_code, 200)

    def test_orders_page_shows_only_current_user_orders(self):
        user = User.objects.create_user(username="+79990000001", password="test-pass", first_name="Ирина")
        other_user = User.objects.create_user(username="+79990000002", password="test-pass", first_name="Ольга")
        Profile.objects.create(user=user, phone=user.username, address="Москва")
        Profile.objects.create(user=other_user, phone=other_user.username, address="Тверь")

        level = CakeOption.objects.get(kind=CakeOption.Kind.LEVEL, name="1 уровень")
        shape = CakeOption.objects.get(kind=CakeOption.Kind.SHAPE, name="Квадрат")
        topping = CakeOption.objects.get(kind=CakeOption.Kind.TOPPING, name="Белый соус")

        Order.objects.create(
            customer=user,
            level=level,
            shape=shape,
            topping=topping,
            customer_name="Ирина",
            customer_phone=user.username,
            customer_email="irina@example.com",
            delivery_address="Москва",
            delivery_date="2026-03-30",
            delivery_time="12:00",
            personal_data_consent=True,
            total_price=1200,
        )
        Order.objects.create(
            customer=other_user,
            level=level,
            shape=shape,
            topping=topping,
            customer_name="Ольга",
            customer_phone=other_user.username,
            customer_email="olga@example.com",
            delivery_address="Тверь",
            delivery_date="2026-03-31",
            delivery_time="13:00",
            personal_data_consent=True,
            total_price=1200,
        )

        self.client.force_login(user)
        response = self.client.get(reverse("accounts:lk_orders"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ирина")
        self.assertNotContains(response, "Ольга")
