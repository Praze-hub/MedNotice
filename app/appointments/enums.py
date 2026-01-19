from core.utils.utils import CustomEnum

class Status(CustomEnum):
      SCHEDULED = "scheduled"
      CONFIRMED = "confirmed"
      COMPLETED = "completed"
      CANCELLED = "cancelled"