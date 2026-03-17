from flask import request, jsonify
from .services import trip_service


class TripController:
    """
    Presentation Layer: Manejo estricto de Peticiones y Respuestas HTTP para Viajes.
    """

    @staticmethod
    def create_trip():
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Validación de seguridad
        if not data.get("motorcycle_id"):
            return jsonify({"error": "Missing required field: motorcycle_id"}), 400

        try:
            new_trip = trip_service.create(data)
            return jsonify(new_trip.to_dict()), 201
        except Exception as e:
            return (
                jsonify({"error": "Error processing request", "details": str(e)}),
                500,
            )

    @staticmethod
    def get_trips():
        trips = trip_service.get_all()
        return jsonify([trip.to_dict() for trip in trips]), 200

    @staticmethod
    def get_trips_by_motorcycle(motorcycle_id: str):
        trips = trip_service.get_by_motorcycle_id(motorcycle_id)
        return jsonify([trip.to_dict() for trip in trips]), 200
