from flask import request, jsonify
from .services import maintenance_service


class MaintenanceController:
    """
    Presentation Layer: Manejo estricto de Peticiones y Respuestas HTTP para Mantenimiento.
    """

    @staticmethod
    def create_record():
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Validación de seguridad
        if not data.get("motorcycle_id"):
            return jsonify({"error": "Missing required field: motorcycle_id"}), 400

        try:
            new_record = maintenance_service.create(data)
            return jsonify(new_record.to_dict()), 201
        except Exception as e:
            return (
                jsonify({"error": "Error processing request", "details": str(e)}),
                500,
            )

    @staticmethod
    def get_records():
        records = maintenance_service.get_all()
        return jsonify([record.to_dict() for record in records]), 200

    @staticmethod
    def get_records_by_motorcycle(motorcycle_id: str):
        records = maintenance_service.get_by_motorcycle_id(motorcycle_id)
        return jsonify([record.to_dict() for record in records]), 200
