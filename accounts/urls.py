from django.urls import path
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    path('lk/', TemplateView.as_view(template_name='lk.html'), name='lk'),
    # path('lk/orders/', TemplateView.as_view(template_name='lk-order.html'), name='lk_orders'),
    path('lk/orders', views.orders_view, name='lk_orders'),
    
    path('api/auth/request-code/', views.send_code, name='api_request_code'),
    path('api/auth/verify-code/', views.verify_code, name='api_verify_code'),
    path('api/profile/update/', views.update_profile, name='api_profile_update'),
    path('logout/', views.custom_logout, name='logout'),
]
