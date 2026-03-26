from django.contrib import admin

from .models import CakeOption, CatalogCake


@admin.register(CakeOption)
class CakeOptionAdmin(admin.ModelAdmin):
    list_display = ("name", "kind", "price", "is_active", "sort_order")
    list_filter = ("kind", "is_active")
    list_editable = ("price", "is_active", "sort_order")
    search_fields = ("name",)
    ordering = ("kind", "sort_order", "id")


@admin.register(CatalogCake)
class CatalogCakeAdmin(admin.ModelAdmin):
    list_display = ("name", "occasion", "base_price", "is_active", "sort_order")
    list_filter = ("occasion", "is_active")
    list_editable = ("base_price", "is_active", "sort_order")
    search_fields = ("name", "occasion", "description")
    prepopulated_fields = {"slug": ("name",)}
