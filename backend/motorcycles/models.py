import uuid
from typing import Dict, Any


class Motorcycle:
    """
    Domain Model: Entidad principal de Motocicleta.
    """

    def __init__(
        self,
        make: str,
        model: str,
        year: int,
        vin: str = "",
        current_mileage: int = 0,
        oil_change_interval: int = 5000,
    ):
        self.id = str(uuid.uuid4())
        self.make = make
        self.model = model
        self.year = year
        self.vin = vin
        self.current_mileage = current_mileage
        self.oil_change_interval = oil_change_interval

    def to_dict(self) -> Dict[str, Any]:
        """Convierte la entidad a un formato serializable."""
        return {
            "id": self.id,
            "make": self.make,
            "model": self.model,
            "year": self.year,
            "vin": self.vin,
            "current_mileage": self.current_mileage,
            "oil_change_interval": self.oil_change_interval,
        }
