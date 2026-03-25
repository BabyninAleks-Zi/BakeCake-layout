from django.urls import path
from django.views.generic import TemplateView

app_name = 'accounts'

urlpatterns = [
    path('lk/', TemplateView.as_view(template_name='lk.html'), name='lk'),  # для теста просмотра страницы
    path('lk/orders/', TemplateView.as_view(template_name='lk-order.html'), name='lk_orders'),  # для теста просмотра страницы
]
