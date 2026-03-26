from __future__ import annotations
from datetime import datetime, timedelta
from django.utils import timezone
from catalog.models import CakeOption


INSCRIPTION_PRICE = 500
RUSH_FEE_PERCENT = 20
REQUIRED_KINDS = (
    CakeOption.Kind.LEVEL,
    CakeOption.Kind.SHAPE,
    CakeOption.Kind.TOPPING,
)


class PricingError(ValueError):
    pass


def calculate_custom_cake_price(
    *,
    level_id: int | None,
    shape_id: int | None,
    topping_id: int | None,
    berry_id: int | None = None,
    decor_id: int | None = None,
    inscription: str = "",
    delivery_date=None,
    delivery_time=None,
) -> dict:
    """Считает итоговую цену кастомного торта."""
    level_price = get_option_price(CakeOption.Kind.LEVEL, level_id)
    shape_price = get_option_price(CakeOption.Kind.SHAPE, shape_id)
    topping_price = get_option_price(CakeOption.Kind.TOPPING, topping_id)
    berry_price = get_option_price(CakeOption.Kind.BERRY, berry_id)
    decor_price = get_option_price(CakeOption.Kind.DECOR, decor_id)

    options_total = (
        level_price
        + shape_price
        + topping_price
        + berry_price
        + decor_price
    )
    inscription_price = calculate_inscription_price(inscription)
    subtotal = options_total + inscription_price
    rush_fee = calculate_rush_fee(
        subtotal=subtotal,
        delivery_date=delivery_date,
        delivery_time=delivery_time,
    )

    return {
        "options_total": options_total,
        "inscription_price": inscription_price,
        "rush_fee": rush_fee,
        "total": subtotal + rush_fee,
    }


def get_option_price(kind: str, option_id: int | None) -> int:
    """Возвращает цену выбранной опции из базы."""
    if option_id in (None, "", 0, "0"):
        if kind in REQUIRED_KINDS:
            raise PricingError(f"Не выбрана обязательная опция: {kind}")
        return 0

    try:
        option = CakeOption.objects.get(
            id=option_id,
            kind=kind,
            is_active=True,
        )
    except CakeOption.DoesNotExist as exc:
        raise PricingError(f"Недопустимая опция: {kind}") from exc

    return option.price


def calculate_inscription_price(inscription: str) -> int:
    """Возвращает цену надписи."""
    if inscription.strip():
        return INSCRIPTION_PRICE
    return 0


def calculate_rush_fee(*, subtotal: int, delivery_date=None, delivery_time=None) -> int:
    """Считает наценку за срочную доставку."""
    if not delivery_date or not delivery_time:
        return 0

    delivery_dt = build_delivery_datetime(delivery_date, delivery_time)
    now = timezone.localtime()

    if delivery_dt <= now:
        raise PricingError("Дата и время доставки должны быть в будущем")

    if delivery_dt - now < timedelta(hours=24):
        return subtotal * RUSH_FEE_PERCENT // 100

    return 0


def build_delivery_datetime(delivery_date, delivery_time):
    """Собирает дату и время доставки в один datetime."""
    if isinstance(delivery_date, datetime):
        combined = delivery_date
    else:
        combined = datetime.combine(delivery_date, delivery_time)

    if timezone.is_naive(combined):
        return timezone.make_aware(combined, timezone.get_current_timezone())

    return timezone.localtime(combined)
