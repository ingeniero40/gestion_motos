import uuid
from typing import Dict, Any
from datetime import datetime


class MaintenanceRecord:
    """
    Domain Model: Entidad principal de Mantenimiento.
    """

    def __init__(
        self,
        motorcycle_id: str,
        service_type: str,
        date: str = None,
        mileage_at_service: int = 0,
        cost: float = 0.0,
        notes: str = "",
    ):
        self.id = str(uuid.uuid4())
        self.motorcycle_id = motorcycle_id
        self.service_type = service_type
        self.date = date if date else datetime.now().isoformat()
        self.mileage_at_service = mileage_at_service
        self.cost = cost
        self.notes = notes

    def to_dict(self) -> Dict[str, Any]:
        """Convierte la entidad a un formato serializable."""
        return {
            "id": self.id,
            "motorcycle_id": self.motorcycle_id,
            "service_type": self.service_type,
            "date": self.date,
            "mileage_at_service": self.mileage_at_service,
            "cost": self.cost,
            "notes": self.notes,
        }
