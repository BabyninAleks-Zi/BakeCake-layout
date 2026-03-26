from django.db import migrations


def seed_cake_options(apps, schema_editor):
    CakeOption = apps.get_model("catalog", "CakeOption")

    options = [
        ("level", "1 уровень", 400, 10),
        ("level", "2 уровня", 750, 20),
        ("level", "3 уровня", 1100, 30),
        ("shape", "Квадрат", 600, 10),
        ("shape", "Круг", 400, 20),
        ("shape", "Прямоугольник", 1000, 30),
        ("topping", "Без топпинга", 0, 10),
        ("topping", "Белый соус", 200, 20),
        ("topping", "Карамельный сироп", 180, 30),
        ("topping", "Кленовый сироп", 200, 40),
        ("topping", "Клубничный сироп", 300, 50),
        ("topping", "Черничный сироп", 350, 60),
        ("topping", "Молочный шоколад", 200, 70),
        ("berry", "Нет", 0, 10),
        ("berry", "Ежевика", 400, 20),
        ("berry", "Малина", 300, 30),
        ("berry", "Голубика", 450, 40),
        ("berry", "Клубника", 500, 50),
        ("decor", "Нет", 0, 10),
        ("decor", "Фисташки", 300, 20),
        ("decor", "Безе", 400, 30),
        ("decor", "Фундук", 350, 40),
        ("decor", "Пекан", 300, 50),
        ("decor", "Маршмеллоу", 200, 60),
        ("decor", "Марципан", 280, 70),
    ]

    for kind, name, price, sort_order in options:
        CakeOption.objects.update_or_create(
            kind=kind,
            name=name,
            defaults={
                "price": price,
                "is_active": True,
                "sort_order": sort_order,
            },
        )


def unseed_cake_options(apps, schema_editor):
    CakeOption = apps.get_model("catalog", "CakeOption")
    CakeOption.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_cake_options, reverse_code=unseed_cake_options),
    ]
