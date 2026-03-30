from django import forms

from catalog.models import CakeOption, CatalogCake


def get_option_queryset(kind):
    """Возвращает активные опции нужного типа."""
    return CakeOption.objects.filter(
        kind=kind,
        is_active=True,
    ).order_by("sort_order", "id")


def get_catalog_cake_queryset():
    """Возвращает активные торты из каталога."""
    return CatalogCake.objects.filter(is_active=True).order_by("sort_order", "id")


class OrderCreateForm(forms.Form):
    catalog_cake = forms.ModelChoiceField(
        queryset=get_catalog_cake_queryset(),
        required=False,
    )
    level = forms.ModelChoiceField(
        queryset=get_option_queryset(CakeOption.Kind.LEVEL),
        required=False,
    )
    shape = forms.ModelChoiceField(
        queryset=get_option_queryset(CakeOption.Kind.SHAPE),
        required=False,
    )
    topping = forms.ModelChoiceField(
        queryset=get_option_queryset(CakeOption.Kind.TOPPING),
        required=False,
    )
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
    promo_code = forms.CharField(required=False, max_length=50)
    personal_data_consent = forms.BooleanField(required=True)

    def clean(self):
        """Проверяет, что выбран либо готовый торт, либо кастомный торт."""
        cleaned_data = super().clean()

        if cleaned_data.get("catalog_cake"):
            return cleaned_data

        required_fields = {
            "level": "Выберите количество уровней.",
            "shape": "Выберите форму торта.",
            "topping": "Выберите топпинг.",
        }

        for field_name, error_text in required_fields.items():
            if not cleaned_data.get(field_name):
                self.add_error(field_name, error_text)

        return cleaned_data


class OrderComplaintForm(forms.Form):
    complaint = forms.CharField(max_length=1000)
