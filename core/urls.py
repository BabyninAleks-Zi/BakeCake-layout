from django.urls import path
from .views import index, privacy_policy

app_name = 'core'

urlpatterns = [
    path('', index, name='index'),
    path('privacy-policy/', privacy_policy, name='privacy_policy'),
]
