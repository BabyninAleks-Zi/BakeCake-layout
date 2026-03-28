from django.urls import path

from .views import catalog_list

app_name = "catalog"

urlpatterns = [
    path("", catalog_list, name="list"),
]
