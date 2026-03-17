from typing import List, Optional, Dict, Any
from .models import Expense
from infrastructure.db import get_db_connection


class ExpenseService:
    """
    Application Layer: Casos de uso de la entidad Expense (Integration w/ SQLite).
    """

    def create(self, data: Dict[str, Any]) -> Expense:
        """Registra un nuevo gasto."""
        new_expense = Expense(
            motorcycle_id=data.get("motorcycle_id", ""),
            amount=float(data.get("amount", 0.0)),
            category=data.get("category", "Uncategorized"),
            date=data.get("date", None),
            description=data.get("description", ""),
            liters=float(data.get("liters", 0.0) if data.get("liters") else 0.0),
        )

        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO expenses (id, motorcycle_id, amount, category, date, description, liters)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    new_expense.id,
                    new_expense.motorcycle_id,
                    new_expense.amount,
                    new_expense.category,
                    new_expense.date,
                    new_expense.description,
                    new_expense.liters,
                ),
            )
            conn.commit()
        finally:
            conn.close()

        return new_expense

    def get_all(self) -> List[Expense]:
        """Obtiene el histórico de todos los gastos."""
        conn = get_db_connection()
        expenses = []
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM expenses")
            rows = cursor.fetchall()
            for row in rows:
                expense = Expense(
                    motorcycle_id=row["motorcycle_id"],
                    amount=row["amount"],
                    category=row["category"],
                    date=row["date"],
                    description=row["description"],
                    liters=row["liters"] if "liters" in row.keys() else 0.0,
                )
                expense.id = row["id"]
                expenses.append(expense)
        finally:
            conn.close()
        return expenses

    def get_by_motorcycle_id(self, motorcycle_id: str) -> List[Expense]:
        """Obtiene los gastos filtrados por motocicleta."""
        conn = get_db_connection()
        expenses = []
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM expenses WHERE motorcycle_id = ?", (motorcycle_id,)
            )
            rows = cursor.fetchall()
            for row in rows:
                expense = Expense(
                    motorcycle_id=row["motorcycle_id"],
                    amount=row["amount"],
                    category=row["category"],
                    date=row["date"],
                    description=row["description"],
                    liters=row["liters"] if "liters" in row.keys() else 0.0,
                )
                expense.id = row["id"]
                expenses.append(expense)
        finally:
            conn.close()
        return expenses

    def get_by_id(self, expense_id: str):
        """Obtiene un gasto por su ID."""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,))
            row = cursor.fetchone()
            if row:
                from .models import Expense

                expense = Expense(
                    motorcycle_id=row["motorcycle_id"],
                    amount=row["amount"],
                    category=row["category"],
                    date=row["date"],
                    description=row["description"],
                    liters=row["liters"] if "liters" in row.keys() else 0.0,
                )
                expense.id = row["id"]
                return expense
        finally:
            conn.close()
        return None

    def update_by_id(self, expense_id: str, data: dict) -> bool:
        """Actualiza un gasto existente por su ID."""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE expenses
                SET amount = ?, category = ?, date = ?, description = ?, liters = ?
                WHERE id = ?
            """,
                (
                    float(data.get("amount", 0)),
                    data.get("category", ""),
                    data.get("date", ""),
                    data.get("description", ""),
                    float(data.get("liters", 0.0) if data.get("liters") else 0.0),
                    expense_id,
                ),
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def delete_by_id(self, expense_id: str) -> bool:
        """Elimina un gasto por su ID."""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()


expense_service = ExpenseService()
