from __future__ import annotations
import uuid
from datetime import datetime, timedelta
from django.utils import timezone
from django.conf import settings
from catalog.models import CakeOption
from .models import Order, PromoCode


INSCRIPTION_PRICE = 500
RUSH_FEE_PERCENT = 20
REQUIRED_KINDS = (
    CakeOption.Kind.LEVEL,
    CakeOption.Kind.SHAPE,
    CakeOption.Kind.TOPPING,
)


class PricingError(ValueError):
    pass


class PaymentError(ValueError):
    pass


def get_active_promo_code(code: str):
    """Возвращает активный промокод по строке."""
    normalized_code = code.strip().upper()
    if not normalized_code:
        return None

    try:
        return PromoCode.objects.get(code=normalized_code, is_active=True)
    except PromoCode.DoesNotExist as exc:
        raise PricingError("Промокод не найден или отключен") from exc


def calculate_discount_amount(subtotal: int, promo_code: PromoCode | None) -> int:
    """Считает скидку по промокоду."""
    if not promo_code:
        return 0

    if promo_code.discount_type == PromoCode.DiscountType.PERCENT:
        discount = subtotal * promo_code.discount_value // 100
    else:
        discount = promo_code.discount_value

    if discount > subtotal:
        return subtotal

    return discount


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


def create_payment(order: Order, return_url: str | None = None) -> dict:
    """Создаёт платёж в YooKassa для заказа."""
    from yookassa import Configuration, Payment

    if not order.total_price:
        raise PaymentError("Сумма заказа не указана")

    Configuration.account_id = settings.YOOKASSA_SHOP_ID
    Configuration.secret_key = settings.YOOKASSA_SECRET_KEY

    description = f"Оплата заказа №{order.id} от {order.customer_name}"
    idempotence_key = f"order_{order.id}_{uuid.uuid4().hex[:16]}"

    payment_data = {
        "amount": {
            "value": str(order.total_price),
            "currency": "RUB",
        },
        "capture": True,
        "description": description,
        "confirmation": {
            "type": "redirect",
            "return_url": return_url or settings.YOOKASSA_RETURN_URL,
        },
        "metadata": {
            "order_id": order.id,
        },
    }

    try:
        payment = Payment.create(payment_data, idempotency_key=idempotence_key)
    except TypeError:
        payment = Payment.create(payment_data)
    except Exception as exc:
        raise PaymentError(f"Ошибка создания платежа: {exc}") from exc

    order.payment_id = payment.id
    order.payment_status = payment.status
    order.confirmation_url = payment.confirmation.confirmation_url
    order.save(update_fields=["payment_id", "payment_status", "confirmation_url"])

    return {
        "payment_id": payment.id,
        "confirmation_url": payment.confirmation.confirmation_url,
        "status": payment.status,
    }


def get_payment_info(payment_id: str) -> dict:
    """Получает информацию о платеже из YooKassa."""
    from yookassa import Configuration, Payment

    Configuration.account_id = settings.YOOKASSA_SHOP_ID
    Configuration.secret_key = settings.YOOKASSA_SECRET_KEY

    try:
        payment = Payment.find_one(payment_id)
    except Exception as exc:
        raise PaymentError(f"Ошибка получения платежа: {exc}") from exc

    if not payment:
        raise PaymentError("Платёж не найден")

    return {
        "id": payment.id,
        "status": payment.status,
        "paid": payment.paid,
        "amount": payment.amount.value if payment.amount else None,
    }


def update_order_from_payment(order: Order, payment_info: dict) -> None:
    """Обновляет заказ на основе информации о платеже."""
    order.payment_status = payment_info.get("status", "")

    paid_statuses = ("succeeded", "waiting_for_capture")
    order.is_paid = payment_info.get("paid", False) or order.payment_status in paid_statuses

    if order.is_paid and not order.paid_at:
        order.paid_at = timezone.now()

    order.save(update_fields=["payment_status", "is_paid", "paid_at"])
