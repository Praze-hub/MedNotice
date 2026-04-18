from core.utils.utils import CustomEnum


class UserRole(CustomEnum):
    PATIENT = 'patient'
    DOCTOR = 'doctor'
    ADMIN = 'admin'
