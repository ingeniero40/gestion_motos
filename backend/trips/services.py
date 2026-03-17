from typing import List, Optional, Dict, Any
from .models import Trip
from infrastructure.db import get_db_connection


class TripService:
    """
    Application Layer: Casos de uso de la entidad Trip (Integration w/ SQLite).
    """

    def create(self, data: Dict[str, Any]) -> Trip:
        """Registra un nuevo viaje."""
        new_trip = Trip(
            motorcycle_id=data.get("motorcycle_id", ""),
            distance_km=data.get("distance_km", 0.0),
            max_speed_kmh=data.get("max_speed_kmh", 0.0),
            date=data.get("date", None),
            title=data.get("title", ""),
            description=data.get("description", ""),
        )

        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO trips (id, motorcycle_id, distance_km, max_speed_kmh, date, title, description)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    new_trip.id,
                    new_trip.motorcycle_id,
                    new_trip.distance_km,
                    new_trip.max_speed_kmh,
                    new_trip.date,
                    new_trip.title,
                    new_trip.description,
                ),
            )
            conn.commit()
        finally:
            conn.close()

        return new_trip

    def get_all(self) -> List[Trip]:
        """Obtiene el histórico de todos los viajes."""
        conn = get_db_connection()
        trips = []
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM trips")
            rows = cursor.fetchall()
            for row in rows:
                trip = Trip(
                    motorcycle_id=row["motorcycle_id"],
                    distance_km=row["distance_km"],
                    max_speed_kmh=row["max_speed_kmh"],
                    date=row["date"],
                    title=row["title"],
                    description=row["description"],
                )
                trip.id = row["id"]
                trips.append(trip)
        finally:
            conn.close()
        return trips

    def get_by_id(self, trip_id: str) -> Optional[Trip]:
        """Obtiene el detalle de un viaje específico."""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM trips WHERE id = ?", (trip_id,))
            row = cursor.fetchone()
            if row:
                trip = Trip(
                    motorcycle_id=row["motorcycle_id"],
                    distance_km=row["distance_km"],
                    max_speed_kmh=row["max_speed_kmh"],
                    date=row["date"],
                    title=row["title"],
                    description=row["description"],
                )
                trip.id = row["id"]
                return trip
        finally:
            conn.close()
        return None

    def get_by_motorcycle_id(self, motorcycle_id: str) -> List[Trip]:
        """Obtiene los viajes filtrados por motocicleta."""
        conn = get_db_connection()
        trips = []
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM trips WHERE motorcycle_id = ?", (motorcycle_id,)
            )
            rows = cursor.fetchall()
            for row in rows:
                trip = Trip(
                    motorcycle_id=row["motorcycle_id"],
                    distance_km=row["distance_km"],
                    max_speed_kmh=row["max_speed_kmh"],
                    date=row["date"],
                    title=row["title"],
                    description=row["description"],
                )
                trip.id = row["id"]
                trips.append(trip)
        finally:
            conn.close()
        return trips

    def get_last_by_motorcycle_id(self, motorcycle_id: str) -> Optional[Trip]:
        """Obtiene el último viaje registrado para una motocicleta."""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM trips WHERE motorcycle_id = ? ORDER BY ROWID DESC LIMIT 1",
                (motorcycle_id,),
            )
            row = cursor.fetchone()
            if row:
                trip = Trip(
                    motorcycle_id=row["motorcycle_id"],
                    distance_km=row["distance_km"],
                    max_speed_kmh=row["max_speed_kmh"],
                    date=row["date"],
                    title=row["title"],
                    description=row["description"],
                )
                trip.id = row["id"]
                return trip
        finally:
            conn.close()
        return None

    def update(self, trip_id: str, data: Dict[str, Any]) -> bool:
        """Actualiza un viaje existente."""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE trips 
                SET title = ?, date = ?, distance_km = ?, max_speed_kmh = ?, description = ?
                WHERE id = ?
            """,
                (
                    data.get("title"),
                    data.get("date"),
                    data.get("distance_km"),
                    data.get("max_speed_kmh"),
                    data.get("description"),
                    trip_id,
                ),
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def delete(self, trip_id: str) -> bool:
        """Elimina un viaje por ID."""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM trips WHERE id = ?", (trip_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()


trip_service = TripService()
