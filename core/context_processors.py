from django.conf import settings


def project_settings(request):
    """Возвращает настройки проекта для шаблонов."""
    return {
        "jivosite_widget_id": settings.JIVOSITE_WIDGET_ID,
    }
