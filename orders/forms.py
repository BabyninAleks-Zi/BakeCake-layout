from django import forms

from catalog.models import CakeOption


def get_option_queryset(kind):
    """Возвращает активные опции нужного типа."""
    return CakeOption.objects.filter(
        kind=kind,
        is_active=True,
    ).order_by("sort_order", "id")


class OrderCreateForm(forms.Form):
    level = forms.ModelChoiceField(queryset=get_option_queryset(CakeOption.Kind.LEVEL))
    shape = forms.ModelChoiceField(queryset=get_option_queryset(CakeOption.Kind.SHAPE))
    topping = forms.ModelChoiceField(queryset=get_option_queryset(CakeOption.Kind.TOPPING))
    berry = forms.ModelChoiceField(
        queryset=get_option_queryset(CakeOption.Kind.BERRY),
        required=False,
    )
    decor = forms.ModelChoiceField(
        queryset=get_option_queryset(CakeOption.Kind.DECOR),
        required=False,
    )
    inscription = forms.CharField(required=False, max_length=200)
    order_comment = forms.CharField(required=False)
    customer_name = forms.CharField(max_length=100)
    customer_phone = forms.CharField(max_length=20)
    customer_email = forms.EmailField()
    delivery_address = forms.CharField(max_length=255)
    delivery_date = forms.DateField()
    delivery_time = forms.TimeField()
    delivery_comment = forms.CharField(required=False)
    personal_data_consent = forms.BooleanField(required=True)
