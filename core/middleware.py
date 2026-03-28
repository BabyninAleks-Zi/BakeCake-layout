UTM_KEYS = (
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_content",
    "utm_term",
)


class UtmMiddleware:
    """Сохраняет UTM-метки первого захода в сессию."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == "GET":
            utm_data = request.session.get("utm_data", {})

            if not utm_data.get("landing_path"):
                utm_data["landing_path"] = request.get_full_path()

            if not utm_data.get("referrer") and request.META.get("HTTP_REFERER"):
                utm_data["referrer"] = request.META["HTTP_REFERER"]

            for key in UTM_KEYS:
                value = request.GET.get(key, "").strip()
                if value and not utm_data.get(key):
                    utm_data[key] = value

            request.session["utm_data"] = utm_data

        return self.get_response(request)
