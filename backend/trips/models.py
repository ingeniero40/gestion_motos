import uuid
from typing import Dict, Any
from datetime import datetime


class Trip:
    """
    Domain Model: Entidad principal de Viaje (Trip).
    """

    def __init__(
        self,
        motorcycle_id: str,
        distance_km: float,
        max_speed_kmh: float = 0.0,
        date: str = None,
        title: str = "",
        description: str = "",
    ):
        self.id = str(uuid.uuid4())
        self.motorcycle_id = motorcycle_id
        self.distance_km = distance_km
        self.max_speed_kmh = max_speed_kmh
        self.date = date if date else datetime.now().isoformat()
        self.title = title
        self.description = description

    def to_dict(self) -> Dict[str, Any]:
        """Convierte la entidad a un formato serializable."""
        return {
            "id": self.id,
            "motorcycle_id": self.motorcycle_id,
            "distance_km": self.distance_km,
            "max_speed_kmh": self.max_speed_kmh,
            "date": self.date,
            "title": self.title,
            "description": self.description,
        }
