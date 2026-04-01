from typing import List, Optional, Dict, Any
from .models import MaintenanceRecord
from infrastructure.db import get_db_connection
from psycopg2.extras import RealDictCursor


class MaintenanceService:
    """
    Application Layer: Casos de uso de la entidad MaintenanceRecord (Integration w/ SQLite).
    """

    def create(self, data: Dict[str, Any]) -> MaintenanceRecord:
        """Registra un nuevo mantenimiento."""
        new_record = MaintenanceRecord(
            motorcycle_id=data.get("motorcycle_id", ""),
            service_type=data.get("service_type", ""),
            date=data.get("date", None),
            mileage_at_service=data.get("mileage_at_service", 0),
            cost=data.get("cost", 0.0),
            notes=data.get("notes", ""),
        )

        conn = get_db_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(
                """
                INSERT INTO maintenance (id, motorcycle_id, service_type, date, mileage_at_service, cost, notes)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
                (
                    new_record.id,
                    new_record.motorcycle_id,
                    new_record.service_type,
                    new_record.date,
                    new_record.mileage_at_service,
                    new_record.cost,
                    new_record.notes,
                ),
            )
            conn.commit()
        finally:
            conn.close()

        return new_record

    def get_all(self) -> List[MaintenanceRecord]:
        """Obtiene el histórico de todos los mantenimientos."""
        conn = get_db_connection()
        records = []
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM maintenance")
            rows = cursor.fetchall()
            for row in rows:
                record = MaintenanceRecord(
                    motorcycle_id=row["motorcycle_id"],
                    service_type=row["service_type"],
                    date=row["date"],
                    mileage_at_service=row["mileage_at_service"],
                    cost=row["cost"],
                    notes=row["notes"],
                )
                record.id = row["id"]
                records.append(record)
        finally:
            conn.close()
        return records

    def get_by_motorcycle_id(self, motorcycle_id: str) -> List[MaintenanceRecord]:
        """Obtiene los mantenimientos filtrados por motocicleta."""
        conn = get_db_connection()
        records = []
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(
                "SELECT * FROM maintenance WHERE motorcycle_id = %s", (motorcycle_id,)
            )
            rows = cursor.fetchall()
            for row in rows:
                record = MaintenanceRecord(
                    motorcycle_id=row["motorcycle_id"],
                    service_type=row["service_type"],
                    date=row["date"],
                    mileage_at_service=row["mileage_at_service"],
                    cost=row["cost"],
                    notes=row["notes"],
                )
                record.id = row["id"]
                records.append(record)
        finally:
            conn.close()
        return records

    def get_by_id(self, record_id: str):
        """Obtiene un registro de mantenimiento por su ID."""
        conn = get_db_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("SELECT * FROM maintenance WHERE id = %s", (record_id,))
            row = cursor.fetchone()
            if row:
                from .models import MaintenanceRecord

                record = MaintenanceRecord(
                    motorcycle_id=row["motorcycle_id"],
                    service_type=row["service_type"],
                    date=row["date"],
                    mileage_at_service=row["mileage_at_service"],
                    cost=row["cost"],
                    notes=row["notes"],
                )
                record.id = row["id"]
                return record
        finally:
            conn.close()
        return None

    def update_by_id(self, record_id: str, data: dict) -> bool:
        """Actualiza un registro de mantenimiento por su ID."""
        conn = get_db_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(
                """
                UPDATE maintenance
                SET service_type = %s, date = %s, mileage_at_service = %s, cost = %s, notes = %s
                WHERE id = %s
            """,
                (
                    data.get("service_type", ""),
                    data.get("date", ""),
                    int(data.get("mileage", 0)),
                    float(data.get("cost", 0)),
                    data.get("notes", ""),
                    record_id,
                ),
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def delete_by_id(self, record_id: str) -> bool:
        """Elimina un registro de mantenimiento por su ID."""
        conn = get_db_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("DELETE FROM maintenance WHERE id = %s", (record_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()


maintenance_service = MaintenanceService()
