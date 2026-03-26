from django.contrib import admin

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
        ("Прочее", {
            "fields": (
                "personal_data_consent",
                "created_at",
                "updated_at",
            )
        }),
    )
