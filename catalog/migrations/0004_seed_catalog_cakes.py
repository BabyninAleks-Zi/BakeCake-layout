from django.db import migrations


CATALOG_CAKES = [
    {
        "name": "Торт для чаепития 1",
        "slug": "tea-cake-1",
        "occasion": "tea",
        "description": "Лёгкий готовый торт для уютного чаепития.",
        "image": "catalog/cakes/Cake_to_tea_1.jpg",
        "base_price": 2400,
        "sort_order": 10,
    },
    {
        "name": "Торт для чаепития 2",
        "slug": "tea-cake-2",
        "occasion": "tea",
        "description": "Нежный торт для домашнего десерта и встречи с близкими.",
        "image": "catalog/cakes/Cake_to_tea_2.jpg",
        "base_price": 2600,
        "sort_order": 20,
    },
    {
        "name": "Торт для чаепития 3",
        "slug": "tea-cake-3",
        "occasion": "tea",
        "description": "Готовый торт с мягким вкусом для спокойного вечера.",
        "image": "catalog/cakes/Cake_to_tea_3.jpg",
        "base_price": 2800,
        "sort_order": 30,
    },
    {
        "name": "Торт для чаепития 4",
        "slug": "tea-cake-4",
        "occasion": "tea",
        "description": "Компактный торт для камерного праздника и чаепития.",
        "image": "catalog/cakes/Cake_to_tea_4.jpg",
        "base_price": 3000,
        "sort_order": 40,
    },
    {
        "name": "Торт для чаепития 5",
        "slug": "tea-cake-5",
        "occasion": "tea",
        "description": "Готовый торт с акцентом на подачу и нежный декор.",
        "image": "catalog/cakes/Cake_to_tea_5.jpg",
        "base_price": 3200,
        "sort_order": 50,
    },
    {
        "name": "Торт для чаепития 6",
        "slug": "tea-cake-6",
        "occasion": "tea",
        "description": "Нарядный торт для сладкого перерыва и семейной встречи.",
        "image": "catalog/cakes/Cake_to_tea_6.jpg",
        "base_price": 3400,
        "sort_order": 60,
    },
    {
        "name": "Торт на день рождения 1",
        "slug": "birthday-cake-1",
        "occasion": "birthday",
        "description": "Яркий готовый торт для дня рождения.",
        "image": "catalog/cakes/Cake_to_BD_1.png",
        "base_price": 3200,
        "sort_order": 110,
    },
    {
        "name": "Торт на день рождения 2",
        "slug": "birthday-cake-2",
        "occasion": "birthday",
        "description": "Праздничный торт для подарка и семейного торжества.",
        "image": "catalog/cakes/Cake_to_BD_2.jpg",
        "base_price": 3500,
        "sort_order": 120,
    },
    {
        "name": "Торт на день рождения 3",
        "slug": "birthday-cake-3",
        "occasion": "birthday",
        "description": "Готовый торт для детского и взрослого праздника.",
        "image": "catalog/cakes/Cake_to_BD_3.jpg",
        "base_price": 3700,
        "sort_order": 130,
    },
    {
        "name": "Торт на день рождения 4",
        "slug": "birthday-cake-4",
        "occasion": "birthday",
        "description": "Нарядный торт с выразительной подачей для гостей.",
        "image": "catalog/cakes/Cake_to_BD_4.jpg",
        "base_price": 3900,
        "sort_order": 140,
    },
    {
        "name": "Торт на день рождения 5",
        "slug": "birthday-cake-5",
        "occasion": "birthday",
        "description": "Готовый праздничный торт с акцентом на оформление.",
        "image": "catalog/cakes/Cake_to_BD_5.jpg",
        "base_price": 4200,
        "sort_order": 150,
    },
    {
        "name": "Торт на день рождения 6",
        "slug": "birthday-cake-6",
        "occasion": "birthday",
        "description": "Торт для большого праздника и эффектной подачи.",
        "image": "catalog/cakes/Cake_to_BD_6.jpg",
        "base_price": 4500,
        "sort_order": 160,
    },
    {
        "name": "Свадебный торт 1",
        "slug": "wedding-cake-1",
        "occasion": "wedding",
        "description": "Элегантный готовый торт для свадебного торжества.",
        "image": "catalog/cakes/Cake_to_Wedding_1.jpeg",
        "base_price": 4800,
        "sort_order": 210,
    },
    {
        "name": "Свадебный торт 2",
        "slug": "wedding-cake-2",
        "occasion": "wedding",
        "description": "Нежный торт для свадебной подачи и фотозоны.",
        "image": "catalog/cakes/Cake_to_Wedding_2.jpeg",
        "base_price": 5200,
        "sort_order": 220,
    },
    {
        "name": "Свадебный торт 3",
        "slug": "wedding-cake-3",
        "occasion": "wedding",
        "description": "Готовый торт для камерной свадьбы и особого вечера.",
        "image": "catalog/cakes/Cake_to_Wedding_3.jpg",
        "base_price": 5600,
        "sort_order": 230,
    },
    {
        "name": "Свадебный торт 4",
        "slug": "wedding-cake-4",
        "occasion": "wedding",
        "description": "Нарядный многоярусный торт для праздничного стола.",
        "image": "catalog/cakes/Cake_to_Wedding_4.jpg",
        "base_price": 6000,
        "sort_order": 240,
    },
    {
        "name": "Свадебный торт 5",
        "slug": "wedding-cake-5",
        "occasion": "wedding",
        "description": "Торт для классической свадьбы с мягким декором.",
        "image": "catalog/cakes/Cake_to_Wedding_5.jpeg",
        "base_price": 6400,
        "sort_order": 250,
    },
    {
        "name": "Свадебный торт 6",
        "slug": "wedding-cake-6",
        "occasion": "wedding",
        "description": "Праздничный торт для большого свадебного банкета.",
        "image": "catalog/cakes/Cake_to_Wedding_6.jpg",
        "base_price": 6800,
        "sort_order": 260,
    },
]


def seed_catalog_cakes(apps, schema_editor):
    """Заполняет каталог стартовыми тортами."""
    CatalogCake = apps.get_model("catalog", "CatalogCake")

    for cake_data in CATALOG_CAKES:
        CatalogCake.objects.update_or_create(
            slug=cake_data["slug"],
            defaults=cake_data,
        )


def unseed_catalog_cakes(apps, schema_editor):
    """Удаляет стартовые торты каталога."""
    CatalogCake = apps.get_model("catalog", "CatalogCake")
    slugs = [cake["slug"] for cake in CATALOG_CAKES]
    CatalogCake.objects.filter(slug__in=slugs).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0003_alter_catalogcake_slug"),
    ]

    operations = [
        migrations.RunPython(seed_catalog_cakes, reverse_code=unseed_catalog_cakes),
    ]
