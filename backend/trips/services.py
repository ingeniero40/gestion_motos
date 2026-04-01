from typing import List, Optional, Dict, Any
from datetime import datetime
from .models import Trip
from infrastructure.db import get_db_connection
from psycopg2.extras import RealDictCursor


def _parse_date(value: Optional[str]) -> Optional[datetime.date]:
    """Parsea una fecha en varios formatos comunes y normaliza a datetime.date."""
    if not value:
        return None

    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, str):
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S.%f"):
            try:
                return datetime.strptime(value[:19] if fmt != "%d/%m/%Y" else value, fmt).date()
            except (ValueError, TypeError):
                continue

    return None


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
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(
                """
                INSERT INTO trips (id, motorcycle_id, distance_km, max_speed_kmh, date, title, description)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
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
            cursor = conn.cursor(cursor_factory=RealDictCursor)
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
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("SELECT * FROM trips WHERE id = %s", (trip_id,))
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
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(
                "SELECT * FROM trips WHERE motorcycle_id = %s", (motorcycle_id,)
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

    def get_trips_by_motorcycle_and_date_range(
        self,
        motorcycle_id: str,
        start_date: Optional[str],
        end_date: Optional[str],
    ) -> List[Trip]:
        """Retorna viajes de una motocicleta en un rango de fechas, con parseo robusto."""
        parsed_start = _parse_date(start_date)
        parsed_end = _parse_date(end_date)

        all_trips = self.get_by_motorcycle_id(motorcycle_id)
        if parsed_start is None or parsed_end is None:
            return all_trips

        return [
            t
            for t in all_trips
            if (trip_date := _parse_date(t.date)) is not None
            and parsed_start <= trip_date <= parsed_end
        ]

    def get_total_distance_by_date_range(
        self,
        motorcycle_id: str,
        start_date: Optional[str],
        end_date: Optional[str],
    ) -> float:
        """Suma distancia_km de los viajes en un rango de fechas dado."""
        trips = self.get_trips_by_motorcycle_and_date_range(motorcycle_id, start_date, end_date)
        return sum(float(getattr(t, "distance_km", 0) or 0) for t in trips)

    def get_last_by_motorcycle_id(self, motorcycle_id: str) -> Optional[Trip]:
        """Obtiene el último viaje registrado para una motocicleta."""
        conn = get_db_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(
                "SELECT * FROM trips WHERE motorcycle_id = %s ORDER BY id DESC LIMIT 1",
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
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(
                """
                UPDATE trips 
                SET title = %s, date = %s, distance_km = %s, max_speed_kmh = %s, description = %s
                WHERE id = %s
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
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("DELETE FROM trips WHERE id = %s", (trip_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()


trip_service = TripService()
