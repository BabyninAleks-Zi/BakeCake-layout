from django.test import TestCase
from django.urls import reverse

from catalog.models import CakeOption


class CoreViewsTests(TestCase):
    def test_index_shows_new_active_berry_from_database(self):
        CakeOption.objects.create(
            kind=CakeOption.Kind.BERRY,
            name="Вишня",
            price=250,
            is_active=True,
            sort_order=99,
        )

        response = self.client.get(reverse("core:index"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Вишня")
