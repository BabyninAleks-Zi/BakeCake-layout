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
        "created_at",
    )
    list_filter = ("status", "delivery_date", "created_at")
    search_fields = ("customer_name", "customer_phone", "customer_email")
    readonly_fields = ("created_at", "updated_at")
