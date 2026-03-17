from typing import List, Optional, Dict, Any
from .models import Motorcycle
from infrastructure.db import get_db_connection


class MotorcycleService:
    """
    Application Layer: Casos de uso de la entidad Motorcycle (Integration w/ SQLite).
    """

    def create(self, data: Dict[str, Any]) -> Motorcycle:
        """Crea y registra una nueva motocicleta."""
        new_moto = Motorcycle(
            make=data.get("make", ""),
            model=data.get("model", ""),
            year=data.get("year", 0),
            vin=data.get("vin", ""),
            current_mileage=data.get("current_mileage", 0),
            oil_change_interval=data.get("oil_change_interval", 5000),
        )

        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO motorcycles (id, make, model, year, vin, current_mileage, oil_change_interval)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    new_moto.id,
                    new_moto.make,
                    new_moto.model,
                    new_moto.year,
                    new_moto.vin,
                    new_moto.current_mileage,
                    new_moto.oil_change_interval,
                ),
            )
            conn.commit()
        finally:
            conn.close()

        return new_moto

    def get_all(self) -> List[Motorcycle]:
        """Obtiene el listado completo de motocicletas."""
        conn = get_db_connection()
        motos = []
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM motorcycles")
            rows = cursor.fetchall()
            for row in rows:
                moto = Motorcycle(
                    make=row["make"],
                    model=row["model"],
                    year=row["year"],
                    vin=row["vin"],
                    current_mileage=row["current_mileage"],
                    oil_change_interval=row["oil_change_interval"],
                )
                moto.id = row["id"]
                motos.append(moto)
        finally:
            conn.close()
        return motos

    def get_by_id(self, moto_id: str) -> Optional[Motorcycle]:
        """Obtiene el detalle de una motocicleta específica."""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM motorcycles WHERE id = ?", (moto_id,))
            row = cursor.fetchone()
            if row:
                moto = Motorcycle(
                    make=row["make"],
                    model=row["model"],
                    year=row["year"],
                    vin=row["vin"],
                    current_mileage=row["current_mileage"],
                    oil_change_interval=row["oil_change_interval"],
                )
                moto.id = row["id"]
                return moto
        finally:
            conn.close()
        return None

    def update_by_id(self, moto_id: str, data: dict) -> bool:
        """Actualiza los datos de una motocicleta por su ID."""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE motorcycles
                SET make = ?, model = ?, year = ?, vin = ?, current_mileage = ?, oil_change_interval = ?
                WHERE id = ?
            """,
                (
                    data.get("make", ""),
                    data.get("model", ""),
                    int(data.get("year", 0)),
                    data.get("vin", ""),
                    int(data.get("current_mileage", 0)),
                    int(data.get("oil_change_interval", 5000)),
                    moto_id,
                ),
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()


# Singleton de la capa de servicio
motorcycle_service = MotorcycleService()
