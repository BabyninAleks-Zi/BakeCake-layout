from django.shortcuts import render

from .models import CatalogCake


OCCASION_LABELS = {
    "tea": "На чаепитие",
    "birthday": "На день рождения",
    "wedding": "На свадьбу",
}


def catalog_list(request):
    """Показывает страницу каталога готовых тортов."""
    selected_occasion = request.GET.get("occasion", "").strip()
    cakes = CatalogCake.objects.filter(is_active=True)

    if selected_occasion in OCCASION_LABELS:
        cakes = cakes.filter(occasion=selected_occasion)
    else:
        selected_occasion = ""

    cakes = list(cakes)
    for cake in cakes:
        cake.occasion_label = OCCASION_LABELS.get(cake.occasion, "Готовый торт")

    context = {
        "cakes": cakes,
        "selected_occasion": selected_occasion,
        "occasion_labels": OCCASION_LABELS,
    }
    return render(request, "catalog.html", context)
