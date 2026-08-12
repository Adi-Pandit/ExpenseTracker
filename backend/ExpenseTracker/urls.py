from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.core.management import call_command
from django.http import JsonResponse
from django.urls import include, path
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)


def health(request):
    return JsonResponse({"status": "ok"})


def _check_cron_secret(request):
    secret = settings.CRON_SECRET
    return secret and request.headers.get("X-Cron-Secret") == secret


@csrf_exempt
@require_POST
def cron_recurring(request):
    if not _check_cron_secret(request):
        return JsonResponse({"error": "Forbidden"}, status=403)
    call_command("generate_recurring_expenses")
    return JsonResponse({"status": "ok"})


@csrf_exempt
@require_POST
def cron_notifications(request):
    if not _check_cron_secret(request):
        return JsonResponse({"error": "Forbidden"}, status=403)
    call_command("generate_notifications")
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("health/", health),
    path("cron/recurring/", cron_recurring),
    path("cron/notifications/", cron_notifications),
    path("admin/", admin.site.urls),
    path("api/", include("expense.urls")),
    path("auth/", include("authentication.urls", namespace="authentication")),
    path("dashboard/", include("overview.api_urls", namespace="dashboard")),
    path("api/schema/", SpectacularAPIView.as_view(), name="api-schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="api-schema"),
        name="api-docs",
    ),
    path(
        "api/redoc/",
        SpectacularRedocView.as_view(url_name="api-schema"),
        name="api-redoc",
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
