import json
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from catalog.models import CakeOption, CatalogCake
from orders.models import Order
from orders.services import INSCRIPTION_PRICE


CATALOG_OCCASION_LABELS = {
    "tea": "На чаепитие",
    "birthday": "На день рождения",
    "wedding": "На свадьбу",
}


def get_builder_options(kind):
    """Возвращает все активные опции конструктора по типу."""
    return list(
        CakeOption.objects.filter(
        kind=kind,
        is_active=True,
        ).order_by("sort_order", "id")
    )


def index(request):
    """Показывает главную страницу с данными конструктора."""
    selected_catalog_cake = None
    reorder_data = None
    selected_catalog_slug = request.GET.get("catalog_cake", "").strip()
    if selected_catalog_slug:
        selected_catalog_cake = get_object_or_404(
            CatalogCake,
            slug=selected_catalog_slug,
            is_active=True,
        )

    repeat_order_id = request.GET.get("repeat_order", "").strip()
    if repeat_order_id and request.user.is_authenticated:
        repeat_order = get_object_or_404(
            Order,
            id=repeat_order_id,
            customer=request.user,
        )
        selected_catalog_cake = repeat_order.catalog_cake or selected_catalog_cake
        profile = getattr(request.user, "profile", None)
        reorder_data = {
            "level": repeat_order.level_id or "",
            "shape": repeat_order.shape_id or "",
            "topping": repeat_order.topping_id or "",
            "berry": repeat_order.berry_id or "",
            "decor": repeat_order.decor_id or "",
            "inscription": repeat_order.inscription,
            "order_comment": repeat_order.order_comment,
            "customer_name": request.user.first_name or repeat_order.customer_name,
            "customer_phone": getattr(profile, "phone", "") or repeat_order.customer_phone,
            "customer_email": request.user.email or repeat_order.customer_email,
            "delivery_address": getattr(profile, "address", "") or repeat_order.delivery_address,
            "delivery_comment": repeat_order.delivery_comment,
        }

    level_options = get_builder_options("level")
    shape_options = get_builder_options("shape")
    topping_options = get_builder_options("topping")
    berry_options = get_builder_options("berry")
    decor_options = get_builder_options("decor")

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
        "level_options": level_options,
        "shape_options": shape_options,
        "topping_options": topping_options,
        "berry_options": berry_options,
        "decor_options": decor_options,
        "builder_data_json": json.dumps(builder_data, ensure_ascii=False),
        "selected_catalog_cake_json": json.dumps(
            {
                "id": selected_catalog_cake.id,
                "name": selected_catalog_cake.name,
                "occasion": CATALOG_OCCASION_LABELS.get(
                    selected_catalog_cake.occasion,
                    selected_catalog_cake.occasion,
                ),
                "price": selected_catalog_cake.base_price,
                "description": selected_catalog_cake.description,
            } if selected_catalog_cake else None,
            ensure_ascii=False,
        ),
        "reorder_data_json": json.dumps(reorder_data, ensure_ascii=False),
    }
    return render(request, "index.html", context)


def privacy_policy(request):
    return render(request, 'privacy.html')
    
