import uuid
from typing import List, Dict, Any
from infrastructure.db import get_db_connection
from psycopg2.extras import RealDictCursor


class IncomeService:
    def create(self, data: Dict[str, Any]):
        conn = get_db_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            id = str(uuid.uuid4())
            cursor.execute(
                """
                INSERT INTO incomes (id, motorcycle_id, amount, date, description, platform, hours_worked)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    id,
                    data.get("motorcycle_id"),
                    data.get("amount", 0.0),
                    data.get("date"),
                    data.get("description", ""),
                    data.get("platform", ""),
                    data.get("hours_worked", 0.0),
                ),
            )
            conn.commit()
        finally:
            conn.close()

    def get_by_motorcycle_id(self, motorcycle_id: str) -> List[Dict[str, Any]]:
        conn = get_db_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(
                "SELECT * FROM incomes WHERE motorcycle_id = %s", (motorcycle_id,)
            )
            rows = [dict(row) for row in cursor.fetchall()]
            return rows
        finally:
            conn.close()


income_service = IncomeService()
