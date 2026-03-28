from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    path('lk/', views.lk_view, name='lk'),
    path('lk/orders/', views.orders_view, name='lk_orders'),
    path('api/auth/request-code/', views.send_code, name='api_request_code'),
    path('api/auth/verify-code/', views.verify_code, name='api_verify_code'),
    path('api/profile/update/', views.update_profile, name='api_profile_update'),
    path('logout/', views.custom_logout, name='logout'),
]
