from flask import Blueprint
from .controllers import MaintenanceController

# Definición del Blueprint para el bounded context "maintenance"
maintenance_bp = Blueprint("maintenance", __name__)

# Mapeo de rutas a Controladores
maintenance_bp.route("/", methods=["POST"])(MaintenanceController.create_record)
maintenance_bp.route("/", methods=["GET"])(MaintenanceController.get_records)
maintenance_bp.route("/motorcycle/<string:motorcycle_id>", methods=["GET"])(
    MaintenanceController.get_records_by_motorcycle
)
