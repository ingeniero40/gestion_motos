from flask import Blueprint
from .controllers import TripController

# Definición del Blueprint para el bounded context "trips"
trips_bp = Blueprint("trips", __name__)

# Mapeo de rutas a Controladores
trips_bp.route("/", methods=["POST"])(TripController.create_trip)
trips_bp.route("/", methods=["GET"])(TripController.get_trips)
# Filtrar por motocicleta específica
trips_bp.route("/motorcycle/<string:motorcycle_id>", methods=["GET"])(
    TripController.get_trips_by_motorcycle
)
