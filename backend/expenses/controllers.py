from flask import request, jsonify
from .services import expense_service


class ExpenseController:
    """
    Presentation Layer: Manejo de Peticiones y Respuestas HTTP para Gastos (Expenses).
    """

    @staticmethod
    def create_expense():
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Validación de seguridad
        required_fields = ["motorcycle_id", "amount", "category"]
        if not all(field in data for field in required_fields):
            return (
                jsonify(
                    {"error": f"Missing required fields: {', '.join(required_fields)}"}
                ),
                400,
            )

        try:
            new_expense = expense_service.create(data)
            return jsonify(new_expense.to_dict()), 201
        except Exception as e:
            return (
                jsonify({"error": "Error processing request", "details": str(e)}),
                500,
            )

    @staticmethod
    def get_expenses():
        expenses = expense_service.get_all()
        return jsonify([expense.to_dict() for expense in expenses]), 200

    @staticmethod
    def get_expenses_by_motorcycle(motorcycle_id: str):
        expenses = expense_service.get_by_motorcycle_id(motorcycle_id)
        return jsonify([expense.to_dict() for expense in expenses]), 200
