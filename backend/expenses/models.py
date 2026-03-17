import uuid
from typing import Dict, Any
from datetime import datetime


class Expense:
    """
    Domain Model: Entidad principal de Gastos (Expenses).
    """

    def __init__(
        self,
        motorcycle_id: str,
        amount: float,
        category: str,
        date: str = None,
        description: str = "",
        liters: float = 0.0,
    ):
        self.id = str(uuid.uuid4())
        self.motorcycle_id = motorcycle_id
        self.amount = amount
        self.category = (
            category  # e.g., 'Fuel', 'Repair', 'Parts', 'Accessories', 'Insurance'
        )
        self.date = date if date else datetime.now().isoformat()
        self.description = description
        self.liters = liters

    def to_dict(self) -> Dict[str, Any]:
        """Convierte la entidad a un formato serializable."""
        return {
            "id": self.id,
            "motorcycle_id": self.motorcycle_id,
            "amount": self.amount,
            "category": self.category,
            "date": self.date,
            "description": self.description,
            "liters": self.liters,
        }
