import csv

from django.contrib import admin
from django.http import HttpResponse
from django.urls import reverse

from .models import Order, PromoCode


@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ("code", "discount_type", "discount_value", "is_active", "created_at")
    list_filter = ("discount_type", "is_active", "created_at")
    search_fields = ("code",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    change_list_template = "admin/orders/order/change_list.html"
    list_display = (
        "id",
        "cake_name",
        "customer_name",
        "customer_phone",
        "delivery_date",
        "delivery_eta_display",
        "total_price",
        "status_display",
        "is_paid",
        "payment_status_display",
        "complaint_status",
        "created_at",
    )
    list_filter = ("status", "is_paid", "payment_status", "delivery_date", "created_at")
    search_fields = ("customer_name", "customer_phone", "customer_email", "payment_id")
    actions = (
        "export_to_csv",
        "mark_as_accepted",
        "mark_as_in_progress",
        "mark_as_delivering",
        "mark_as_completed",
    )
    fieldsets = (
        ("Основная информация", {
            "fields": (
                "customer",
                "customer_name",
                "customer_phone",
                "customer_email",
                "status",
                "status_display",
            )
        }),
        ("Параметры торта", {
            "fields": (
                "catalog_cake",
                "level",
                "shape",
                "topping",
                "berry",
                "decor",
                "inscription",
            )
        }),
        ("Доставка", {
            "fields": (
                "delivery_address",
                "delivery_date",
                "delivery_time",
                "delivery_eta",
                "order_comment",
                "delivery_comment",
            )
        }),
        ("Стоимость", {
            "fields": (
                "options_total",
                "inscription_price",
                "rush_fee",
                "total_price",
            )
        }),
        ("Оплата", {
            "fields": (
                "payment_id",
                "payment_status",
                "payment_status_display",
                "is_paid",
                "paid_at",
                "confirmation_url",
            )
        }),
        ("Маркетинг", {
            "fields": (
                "utm_source",
                "utm_medium",
                "utm_campaign",
                "utm_content",
                "utm_term",
                "referrer",
                "landing_path",
            )
        }),
        ("Прочее", {
            "fields": (
                "promo_code",
                "personal_data_consent",
                "customer_complaint",
                "complaint_created_at",
                "created_at",
                "updated_at",
            )
        }),
    )
    readonly_fields = (
        "created_at",
        "updated_at",
        "payment_id",
        "payment_status",
        "payment_status_display",
        "status_display",
        "is_paid",
        "paid_at",
        "confirmation_url",
        "complaint_created_at",
    )

    def cake_name(self, obj):
        """Показывает название торта в списке."""
        return obj.cake_name()

    cake_name.short_description = "Торт"

    def delivery_eta_display(self, obj):
        """Показывает ETA в списке заказов."""
        return obj.delivery_eta_text()

    delivery_eta_display.short_description = "ETA доставки"

    def status_display(self, obj):
        """Показывает понятный статус заказа."""
        return obj.status_text()

    status_display.short_description = "Статус заказа"

    def payment_status_display(self, obj):
        """Показывает понятный статус оплаты."""
        return obj.payment_status_text()

    payment_status_display.short_description = "Статус оплаты"

    def complaint_status(self, obj):
        """Показывает, есть ли жалоба по заказу."""
        if obj.customer_complaint:
            return "Есть жалоба"
        return "Без жалобы"

    complaint_status.short_description = "Жалоба"

    def mark_as_accepted(self, request, queryset):
        """Переводит заказы в статус Принят."""
        queryset.update(status=Order.Status.ACCEPTED)

    mark_as_accepted.short_description = "Пометить как принятые"

    def mark_as_in_progress(self, request, queryset):
        """Переводит заказы в статус Готовится."""
        queryset.update(status=Order.Status.IN_PROGRESS)

    mark_as_in_progress.short_description = "Пометить как готовится"

    def mark_as_delivering(self, request, queryset):
        """Переводит заказы в статус В доставке."""
        queryset.update(status=Order.Status.DELIVERING)

    mark_as_delivering.short_description = "Пометить как в доставке"

    def mark_as_completed(self, request, queryset):
        """Переводит заказы в статус Выполнен."""
        queryset.update(status=Order.Status.COMPLETED)

    mark_as_completed.short_description = "Пометить как выполненные"

    def changelist_view(self, request, extra_context=None):
        """Добавляет ссылку на отчёт по заказам."""
        extra_context = extra_context or {}
        extra_context["orders_report_url"] = reverse("orders:report")
        return super().changelist_view(request, extra_context=extra_context)

    def export_to_csv(self, request, queryset):
        """Выгружает выбранные заказы в CSV."""
        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = 'attachment; filename="orders.csv"'

        writer = csv.writer(response)
        writer.writerow([
            "id",
            "customer_name",
            "customer_phone",
            "customer_email",
            "catalog_cake",
            "promo_code",
            "status",
            "payment_status",
            "is_paid",
            "total_price",
            "discount_amount",
            "delivery_date",
            "delivery_time",
            "delivery_eta",
            "delivery_address",
            "customer_complaint",
            "utm_source",
            "utm_medium",
            "utm_campaign",
            "utm_content",
            "utm_term",
            "referrer",
            "landing_path",
            "created_at",
        ])

        for order in queryset:
            writer.writerow([
                order.id,
                order.customer_name,
                order.customer_phone,
                order.customer_email,
                order.cake_name(),
                order.promo_code.code if order.promo_code else "",
                order.status_text(),
                order.payment_status_text(),
                order.is_paid,
                order.total_price,
                order.discount_amount,
                order.delivery_date,
                order.delivery_time,
                order.delivery_eta_text(),
                order.delivery_address,
                order.customer_complaint,
                order.utm_source,
                order.utm_medium,
                order.utm_campaign,
                order.utm_content,
                order.utm_term,
                order.referrer,
                order.landing_path,
                order.created_at,
            ])

        return response

    export_to_csv.short_description = "Выгрузить выбранные заказы в CSV"
