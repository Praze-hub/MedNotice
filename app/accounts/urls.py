from django.urls import path
from .views import PatientRegisterView, SetPasswordView, StaffOnboardingView, VerifyEmail, PasswordResetRequestView, PasswordResetConfirmView
from rest_framework_simplejwt.views import(
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework.routers import DefaultRouter
from .views import AdminViewSet


router = DefaultRouter()
router.register('admin/users', AdminViewSet, basename='admin-users')

urlpatterns = [
    path('auth/register/', PatientRegisterView.as_view(), name='register'),
    path('auth/staff/onboard/', StaffOnboardingView.as_view(), name='staff-onboard'),
    path('auth/set-password/', SetPasswordView.as_view(), name='set-password'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('verify-email/', VerifyEmail.as_view(), name='verify-email'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password-reset'),
    path('password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
]

urlpatterns += router.urls