from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import DoctorViewSet

router = DefaultRouter()
router.register('doctor', DoctorViewSet, basename = 'doctor')


urlpatterns = [
    path('', include(router.urls)),
]