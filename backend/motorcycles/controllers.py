from flask import request, jsonify
from .services import motorcycle_service


class MotorcycleController:
    """
    Presentation Layer: Manejo estricto de Peticiones y Respuestas HTTP
    """

    @staticmethod
    def create_motorcycle():
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Validación básica exigida por diseño seguro (Security by Design)
        required_fields = ["make", "model", "year"]
        if not all(field in data for field in required_fields):
            return (
                jsonify(
                    {"error": f"Missing required fields: {', '.join(required_fields)}"}
                ),
                400,
            )

        try:
            new_moto = motorcycle_service.create(data)
            return jsonify(new_moto.to_dict()), 201
        except Exception as e:
            return (
                jsonify({"error": "Error processing request", "details": str(e)}),
                500,
            )

    @staticmethod
    def get_motorcycles():
        motos = motorcycle_service.get_all()
        return jsonify([moto.to_dict() for moto in motos]), 200

    @staticmethod
    def get_motorcycle_by_id(moto_id: str):
        moto = motorcycle_service.get_by_id(moto_id)
        if not moto:
            return jsonify({"error": "Motorcycle not found"}), 404
        return jsonify(moto.to_dict()), 200
