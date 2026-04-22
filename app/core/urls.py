from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)
from django.http import JsonResponse

def health_check(request):
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/appointments/', include('appointments.urls')),
    path('api/v1/patients/', include('patients.urls')),
    path('api/v1/doctor/', include('doctor.urls')),
    path("api/v1/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/v1/docs/", SpectacularSwaggerView.as_view(url_name="schema")),
    path("api/v1/redoc/", SpectacularRedocView.as_view(url_name="schema")),
    path('api/v1/accounts/', include('accounts.urls')),
    path('api/v1/health/', health_check),
  
]
