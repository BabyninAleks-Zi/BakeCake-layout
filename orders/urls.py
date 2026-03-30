from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path("create/", views.create_order, name="create"),
    path("promo-preview/", views.promo_preview, name="promo_preview"),
    path("report/", views.orders_report, name="report"),
    path("<int:order_id>/complaint/", views.create_complaint, name="complaint"),
    path("success/<int:order_id>/", views.order_success, name="success"),
    path("payment/create/", views.payment_create, name="payment_create"),
    path("payment/callback/", views.payment_callback, name="payment_callback"),
]
