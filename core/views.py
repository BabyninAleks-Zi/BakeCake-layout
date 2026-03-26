import json
from django.shortcuts import render
from catalog.models import CakeOption
from orders.services import INSCRIPTION_PRICE


BUILDER_OPTION_NAMES = {
    "level": ["1 уровень", "2 уровня", "3 уровня"],
    "shape": ["Круг", "Квадрат", "Прямоугольник"],
    "topping": [
        "Без топпинга",
        "Белый соус",
        "Карамельный сироп",
        "Кленовый сироп",
        "Черничный сироп",
        "Молочный шоколад",
        "Клубничный сироп",
    ],
    "berry": ["Ежевика", "Малина", "Голубика", "Клубника"],
    "decor": ["Фисташки", "Безе", "Фундук", "Пекан", "Маршмеллоу", "Марципан"],
}


def get_builder_options(kind):
    """Возвращает опции конструктора в нужном порядке."""
    names = BUILDER_OPTION_NAMES[kind]
    options = CakeOption.objects.filter(
        kind=kind,
        name__in=names,
        is_active=True,
    )
    options_by_name = {option.name: option for option in options}

    missing_names = [name for name in names if name not in options_by_name]
    if missing_names:
        missing_list = ", ".join(missing_names)
        raise CakeOption.DoesNotExist(f"Не найдены опции {kind}: {missing_list}")

    return [options_by_name[name] for name in names]


def index(request):
    """Показывает главную страницу с данными конструктора."""
    level_options = get_builder_options("level")
    shape_options = get_builder_options("shape")
    topping_options = get_builder_options("topping")
    berry_options = get_builder_options("berry")
    decor_options = get_builder_options("decor")

    builder_values = {
        "level_1": level_options[0].id,
        "level_2": level_options[1].id,
        "level_3": level_options[2].id,
        "shape_round": shape_options[0].id,
        "shape_square": shape_options[1].id,
        "shape_rectangle": shape_options[2].id,
        "topping_none": topping_options[0].id,
        "topping_white": topping_options[1].id,
        "topping_caramel": topping_options[2].id,
        "topping_maple": topping_options[3].id,
        "topping_blueberry": topping_options[4].id,
        "topping_milk": topping_options[5].id,
        "topping_strawberry": topping_options[6].id,
        "berry_blackberry": berry_options[0].id,
        "berry_raspberry": berry_options[1].id,
        "berry_blueberry": berry_options[2].id,
        "berry_strawberry": berry_options[3].id,
        "decor_pistachio": decor_options[0].id,
        "decor_meringue": decor_options[1].id,
        "decor_hazelnut": decor_options[2].id,
        "decor_pecan": decor_options[3].id,
        "decor_marshmallow": decor_options[4].id,
        "decor_marzipan": decor_options[5].id,
    }

    builder_data = {
        "labels": {
            "Levels": {str(option.id): option.name for option in level_options},
            "Forms": {str(option.id): option.name for option in shape_options},
            "Toppings": {str(option.id): option.name for option in topping_options},
            "Berries": {str(option.id): option.name for option in berry_options},
            "Decors": {str(option.id): option.name for option in decor_options},
        },
        "costs": {
            "Levels": {str(option.id): option.price for option in level_options},
            "Forms": {str(option.id): option.price for option in shape_options},
            "Toppings": {str(option.id): option.price for option in topping_options},
            "Berries": {str(option.id): option.price for option in berry_options},
            "Decors": {str(option.id): option.price for option in decor_options},
            "Words": INSCRIPTION_PRICE,
        },
    }

    context = {
        "builder_values": builder_values,
        "builder_data_json": json.dumps(builder_data, ensure_ascii=False),
    }
    return render(request, "index.html", context)
