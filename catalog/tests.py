from django.test import TestCase
from django.urls import reverse

from .models import CatalogCake


class CatalogViewsTests(TestCase):
    def test_catalog_page_opens(self):
        response = self.client.get(reverse("catalog:list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Каталог готовых тортов")
        self.assertGreaterEqual(len(response.context["cakes"]), 1)

    def test_catalog_filters_by_occasion(self):
        response = self.client.get(reverse("catalog:list"), {"occasion": "wedding"})

        self.assertEqual(response.status_code, 200)
        self.assertTrue(all(cake.occasion == "wedding" for cake in response.context["cakes"]))
        self.assertFalse(CatalogCake.objects.filter(is_active=True).count() == 0)

    def test_catalog_order_button_links_to_checkout(self):
        cake = CatalogCake.objects.filter(is_active=True).first()

        response = self.client.get(reverse("catalog:list"))

        self.assertContains(
            response,
            f'?catalog_cake={cake.slug}#step4',
        )
