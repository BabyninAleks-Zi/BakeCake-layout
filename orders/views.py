from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST

from .forms import OrderCreateForm
from .models import Order
from .services import PricingError, PaymentError, calculate_custom_cake_price, \
    create_payment, get_payment_info, update_order_from_payment


@require_POST
def create_order(request):
    """Создаёт заказ из checkout-формы."""
    form = OrderCreateForm(request.POST)

    if not form.is_valid():
        messages.error(request, "Не удалось оформить заказ. Проверьте поля формы.")
        return redirect("core:index")

    cleaned = form.cleaned_data

    try:
        pricing = calculate_custom_cake_price(
            level_id=cleaned["level"].id,
            shape_id=cleaned["shape"].id,
            topping_id=cleaned["topping"].id,
            berry_id=cleaned["berry"].id if cleaned["berry"] else None,
            decor_id=cleaned["decor"].id if cleaned["decor"] else None,
            inscription=cleaned["inscription"],
            delivery_date=cleaned["delivery_date"],
            delivery_time=cleaned["delivery_time"],
        )
    except PricingError as exc:
        messages.error(request, str(exc))
        return redirect("core:index")

    order = Order.objects.create(
        customer=request.user if request.user.is_authenticated else None,
        level=cleaned["level"],
        shape=cleaned["shape"],
        topping=cleaned["topping"],
        berry=cleaned["berry"],
        decor=cleaned["decor"],
        customer_name=cleaned["customer_name"],
        customer_phone=cleaned["customer_phone"],
        customer_email=cleaned["customer_email"],
        delivery_address=cleaned["delivery_address"],
        delivery_date=cleaned["delivery_date"],
        delivery_time=cleaned["delivery_time"],
        inscription=cleaned["inscription"],
        order_comment=cleaned["order_comment"],
        delivery_comment=cleaned["delivery_comment"],
        personal_data_consent=cleaned["personal_data_consent"],
        options_total=pricing["options_total"],
        inscription_price=pricing["inscription_price"],
        rush_fee=pricing["rush_fee"],
        total_price=pricing["total"],
    )

    request.session["pending_order_id"] = order.id
    return redirect("orders:payment_create")


@require_GET
def order_success(request, order_id):
    """Показывает страницу успешного оформления заказа."""
    order = get_object_or_404(Order, id=order_id)
    return render(request, "orders_success.html", {"order": order})


@require_GET
def payment_create(request):
    """Создаёт платёж в YooKassa и перенаправляет на оплату."""
    order_id = request.session.get("pending_order_id")

    if not order_id:
        messages.error(request, "Заказ не найден. Оформите заказ заново.")
        return redirect("core:index")

    order = get_object_or_404(Order, id=order_id)

    if order.is_paid:
        del request.session["pending_order_id"]
        return redirect("orders:success", order_id=order.id)

    try:
        payment_info = create_payment(order)
    except PaymentError as exc:
        messages.error(request, f"Ошибка оплаты: {exc}")
        return redirect("core:index")

    return redirect(payment_info["confirmation_url"])


@require_GET
def payment_callback(request):
    """Обрабатывает возврат пользователя после оплаты."""
    order_id = request.session.get("pending_order_id")

    if not order_id:
        messages.warning(request, "Заказ не найден в сессии.")
        return redirect("core:index")

    order = get_object_or_404(Order, id=order_id)

    if not order.payment_id:
        messages.error(request, "Платёж не найден.")
        del request.session["pending_order_id"]
        return redirect("orders:success", order_id=order.id)

    try:
        payment_info = get_payment_info(order.payment_id)
    except PaymentError as exc:
        messages.error(request, f"Ошибка проверки платежа: {exc}")
        return redirect("orders:success", order_id=order.id)

    update_order_from_payment(order, payment_info)
    del request.session["pending_order_id"]

    if order.is_paid:
        return redirect("orders:success", order_id=order.id)

    messages.info(request, f"Платёж в обработке. Статус: {order.payment_status}")
    return redirect("orders:success", order_id=order.id)
