from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Count, Sum
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from accounts.models import Profile
from .forms import OrderComplaintForm, OrderCreateForm
from .models import Order
from .services import PricingError, PaymentError, calculate_custom_cake_price, calculate_discount_amount, calculate_rush_fee, \
    create_payment, get_active_promo_code, get_payment_info, recalculate_order_pricing, update_order_from_payment


def build_payment_return_url(order_id):
    """Собирает URL возврата после оплаты."""
    separator = "&" if "?" in settings.YOOKASSA_RETURN_URL else "?"
    return f"{settings.YOOKASSA_RETURN_URL}{separator}order_id={order_id}"


def get_payment_order_id(request):
    """Возвращает id заказа из сессии или query-параметра."""
    return request.session.get("pending_order_id") or request.GET.get("order_id")


def get_utm_data(request):
    """Возвращает UTM-данные из сессии."""
    return request.session.get("utm_data", {})


def sync_user_profile_from_checkout(user, cleaned_data):
    """Сохраняет данные из checkout в профиль пользователя."""
    if not user or not user.is_authenticated:
        return

    user_changed = False
    profile, _ = Profile.objects.get_or_create(
        user=user,
        defaults={"phone": user.username},
    )

    customer_name = cleaned_data.get("customer_name", "").strip()
    customer_email = cleaned_data.get("customer_email", "").strip()
    delivery_address = cleaned_data.get("delivery_address", "").strip()

    if customer_name and user.first_name != customer_name:
        user.first_name = customer_name
        user_changed = True

    if customer_email and user.email != customer_email:
        user.email = customer_email
        user_changed = True

    if user_changed:
        user.save(update_fields=["first_name", "email"])

    if delivery_address and profile.address != delivery_address:
        profile.address = delivery_address
        profile.save(update_fields=["address"])


def payment_amount_matches_order(order):
    """Проверяет, совпадает ли сумма платежа с суммой заказа."""
    if not order.payment_id:
        return False

    try:
        payment_info = get_payment_info(order.payment_id)
    except PaymentError:
        return False

    amount_text = payment_info.get("amount")
    if amount_text is None:
        return False

    try:
        payment_amount = int(float(amount_text))
    except (TypeError, ValueError):
        return False

    return payment_amount == order.total_price


@require_POST
def create_order(request):
    """Создаёт заказ из checkout-формы."""
    form = OrderCreateForm(request.POST)

    if not form.is_valid():
        messages.error(request, "Не удалось оформить заказ. Проверьте поля формы.")
        return redirect("core:index")

    cleaned = form.cleaned_data
    utm_data = get_utm_data(request)
    catalog_cake = cleaned["catalog_cake"]
    promo_code_text = cleaned["promo_code"]

    try:
        promo_code = get_active_promo_code(promo_code_text)
    except PricingError as exc:
        messages.error(request, str(exc))
        return redirect("core:index")

    order_data = {
        "catalog_cake": catalog_cake,
        "promo_code": promo_code,
        "customer": request.user if request.user.is_authenticated else None,
        "berry": cleaned["berry"],
        "decor": cleaned["decor"],
        "customer_name": cleaned["customer_name"],
        "customer_phone": cleaned["customer_phone"],
        "customer_email": cleaned["customer_email"],
        "delivery_address": cleaned["delivery_address"],
        "delivery_date": cleaned["delivery_date"],
        "delivery_time": cleaned["delivery_time"],
        "inscription": cleaned["inscription"],
        "order_comment": cleaned["order_comment"],
        "delivery_comment": cleaned["delivery_comment"],
        "utm_source": utm_data.get("utm_source", ""),
        "utm_medium": utm_data.get("utm_medium", ""),
        "utm_campaign": utm_data.get("utm_campaign", ""),
        "utm_content": utm_data.get("utm_content", ""),
        "utm_term": utm_data.get("utm_term", ""),
        "referrer": utm_data.get("referrer", ""),
        "landing_path": utm_data.get("landing_path", ""),
        "personal_data_consent": cleaned["personal_data_consent"],
    }

    if catalog_cake:
        try:
            rush_fee = calculate_rush_fee(
                subtotal=catalog_cake.base_price,
                delivery_date=cleaned["delivery_date"],
                delivery_time=cleaned["delivery_time"],
            )
        except PricingError as exc:
            messages.error(request, str(exc))
            return redirect("core:index")

        pricing = {
            "options_total": catalog_cake.base_price,
            "inscription_price": 0,
            "rush_fee": rush_fee,
            "total": catalog_cake.base_price + rush_fee,
        }
        order_data["level"] = None
        order_data["shape"] = None
        order_data["topping"] = None
        order_data["berry"] = None
        order_data["decor"] = None
        order_data["inscription"] = ""
    else:
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

        order_data["level"] = cleaned["level"]
        order_data["shape"] = cleaned["shape"]
        order_data["topping"] = cleaned["topping"]

    discount_amount = calculate_discount_amount(
        pricing["total"],
        promo_code,
    )
    final_total = pricing["total"] - discount_amount

    sync_user_profile_from_checkout(request.user, cleaned)

    order = Order.objects.create(
        options_total=pricing["options_total"],
        inscription_price=pricing["inscription_price"],
        rush_fee=pricing["rush_fee"],
        discount_amount=discount_amount,
        total_price=final_total,
        **order_data,
    )

    request.session["pending_order_id"] = order.id
    return redirect("orders:payment_create")


@require_GET
def order_success(request, order_id):
    """Показывает страницу успешного оформления заказа."""
    order = get_object_or_404(Order, id=order_id)
    context = {
        "order": order,
        "can_retry_payment": (
            not order.is_paid
            and request.session.get("pending_order_id") == order.id
        ),
    }
    return render(request, "orders_success.html", context)


@require_GET
def payment_create(request):
    """Создаёт платёж в YooKassa и перенаправляет на оплату."""
    order_id = get_payment_order_id(request)

    if not order_id:
        messages.error(request, "Заказ не найден. Оформите заказ заново.")
        return redirect("core:index")

    order = get_object_or_404(Order, id=order_id)

    if order.is_paid:
        if "pending_order_id" in request.session:
            del request.session["pending_order_id"]
        return redirect("orders:success", order_id=order.id)

    try:
        order = recalculate_order_pricing(order)
    except PricingError as exc:
        messages.error(request, str(exc))
        return redirect("orders:success", order_id=order.id)

    if order.payment_status in ("pending", "waiting_for_capture") and order.confirmation_url:
        if payment_amount_matches_order(order):
            return redirect(order.confirmation_url)

        order.payment_id = None
        order.payment_status = ""
        order.confirmation_url = ""
        order.save(update_fields=["payment_id", "payment_status", "confirmation_url", "updated_at"])

    if order.payment_status in ("pending", "waiting_for_capture") and order.confirmation_url:
        return redirect(order.confirmation_url)

    try:
        payment_info = create_payment(
            order,
            return_url=build_payment_return_url(order.id),
        )
    except PaymentError as exc:
        messages.error(request, f"Ошибка оплаты: {exc}")
        return redirect("core:index")

    return redirect(payment_info["confirmation_url"])


@require_GET
def payment_callback(request):
    """Обрабатывает возврат пользователя после оплаты."""
    order_id = get_payment_order_id(request)

    if not order_id:
        messages.warning(request, "Заказ не найден в сессии.")
        return redirect("core:index")

    order = get_object_or_404(Order, id=order_id)

    if not order.payment_id:
        messages.error(request, "Платёж не найден.")
        if "pending_order_id" in request.session:
            del request.session["pending_order_id"]
        return redirect("orders:success", order_id=order.id)

    try:
        payment_info = get_payment_info(order.payment_id)
    except PaymentError as exc:
        messages.error(request, f"Ошибка проверки платежа: {exc}")
        return redirect("orders:success", order_id=order.id)

    update_order_from_payment(order, payment_info)

    if order.is_paid:
        if "pending_order_id" in request.session:
            del request.session["pending_order_id"]
        return redirect("orders:success", order_id=order.id)

    messages.info(request, f"Платёж в обработке. Статус: {order.payment_status}")
    request.session["pending_order_id"] = order.id
    return redirect("orders:success", order_id=order.id)


@require_GET
def promo_preview(request):
    """Возвращает предпросмотр скидки по промокоду."""
    promo_code_text = request.GET.get("promo_code", "").strip()
    subtotal_text = request.GET.get("subtotal", "0").strip()

    if not promo_code_text:
        return JsonResponse({
            "ok": True,
            "discount_amount": 0,
            "total_amount": max(int(subtotal_text or 0), 0),
            "message": "",
        })

    try:
        subtotal = max(int(subtotal_text), 0)
    except ValueError:
        return JsonResponse({
            "ok": False,
            "discount_amount": 0,
            "total_amount": 0,
            "message": "Не удалось посчитать скидку.",
        }, status=400)

    try:
        promo_code = get_active_promo_code(promo_code_text)
    except PricingError as exc:
        return JsonResponse({
            "ok": False,
            "discount_amount": 0,
            "total_amount": subtotal,
            "message": str(exc),
        }, status=404)

    discount_amount = calculate_discount_amount(subtotal, promo_code)

    return JsonResponse({
        "ok": True,
        "discount_amount": discount_amount,
        "total_amount": subtotal - discount_amount,
        "message": f"Промокод {promo_code.code} применен.",
    })


@require_POST
def create_complaint(request, order_id):
    """Сохраняет жалобу пользователя по заказу."""
    if not request.user.is_authenticated:
        messages.error(request, "Нужно войти в личный кабинет.")
        return redirect("core:index")

    order = get_object_or_404(Order, id=order_id, customer=request.user)
    form = OrderComplaintForm(request.POST)

    if not form.is_valid():
        messages.error(request, "Не удалось сохранить жалобу.")
        return redirect("accounts:lk_orders")

    if order.customer_complaint:
        messages.info(request, "Жалоба по этому заказу уже сохранена.")
        return redirect("accounts:lk_orders")

    order.customer_complaint = form.cleaned_data["complaint"]
    order.complaint_created_at = timezone.now()
    order.save(update_fields=["customer_complaint", "complaint_created_at"])

    messages.success(request, "Жалоба сохранена. Менеджер увидит её в админке.")
    return redirect("accounts:lk_orders")


@staff_member_required
@require_GET
def orders_report(request):
    """Показывает простой отчёт по заказам и рекламе."""
    by_source = list(
        Order.objects.values("utm_source")
        .annotate(
            orders_count=Count("id"),
            revenue=Sum("total_price"),
        )
        .order_by("-orders_count", "utm_source")
    )
    by_campaign = list(
        Order.objects.values("utm_campaign")
        .annotate(
            orders_count=Count("id"),
            revenue=Sum("total_price"),
        )
        .order_by("-orders_count", "utm_campaign")
    )
    totals = Order.objects.aggregate(
        orders_count=Count("id"),
        revenue=Sum("total_price"),
    )

    context = {
        "totals": totals,
        "by_source": by_source,
        "by_campaign": by_campaign,
    }
    return render(request, "orders_report.html", context)
