import csv

from django.contrib import admin
from django.http import HttpResponse

from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "customer_name",
        "customer_phone",
        "delivery_date",
        "delivery_time",
        "total_price",
        "status",
        "is_paid",
        "payment_status",
        "created_at",
    )
    list_filter = ("status", "is_paid", "payment_status", "delivery_date", "created_at")
    search_fields = ("customer_name", "customer_phone", "customer_email", "payment_id")
    readonly_fields = ("created_at", "updated_at", "payment_id", "payment_status", "is_paid", "paid_at", "confirmation_url")
    actions = ("export_to_csv",)
    fieldsets = (
        ("Основная информация", {
            "fields": (
                "customer",
                "customer_name",
                "customer_phone",
                "customer_email",
                "status",
            )
        }),
        ("Параметры торта", {
            "fields": (
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
                "personal_data_consent",
                "created_at",
                "updated_at",
            )
        }),
    )

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
            "status",
            "payment_status",
            "is_paid",
            "total_price",
            "delivery_date",
            "delivery_time",
            "delivery_address",
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
                order.status,
                order.payment_status,
                order.is_paid,
                order.total_price,
                order.delivery_date,
                order.delivery_time,
                order.delivery_address,
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
