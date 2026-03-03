from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import AdminAppointmentViewSet, DoctorAppointmentViewSet, PatientAppointmentViewSet

router = DefaultRouter()
# router.register('appointments', AppointmentViewSet, basename = 'appointments')
router.register("patient/appointments", PatientAppointmentViewSet, basename="patient-appointments")
router.register("doctor/appointments", DoctorAppointmentViewSet, basename="doctor-appointments")
router.register("admin/appointments", AdminAppointmentViewSet, basename="admin-appointments")

urlpatterns = [
    path('', include(router.urls)),
]