from core.utils.utils import CustomEnum

class Status(CustomEnum):
      PENDING = "pending"
      SCHEDULED = "scheduled"
      CONFIRMED = "confirmed"
      COMPLETED = "completed"
      CANCELLED = "cancelled"
      DECLINED = "declined"