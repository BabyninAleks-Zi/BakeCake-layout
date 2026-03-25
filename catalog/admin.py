from django.contrib import admin

from .models import Cake
from .models import (CakeDecor, CakeBerry, CakeShape, CakeTopping, CakeLevel)


@admin.register(Cake)
class CakeAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'topping', 'berry', 'decor', 'inscription', 'comment')


@admin.register(CakeDecor, CakeBerry, CakeShape, CakeTopping, CakeLevel)
class CakePartsAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'price')
    list_editable = ['price']
