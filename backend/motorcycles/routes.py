from flask import Blueprint
from .controllers import MotorcycleController

# Definición del Blueprint para el bounded context "motorcycles"
motorcycles_bp = Blueprint("motorcycles", __name__)

# Mapeo de rutas a Controladores
motorcycles_bp.route("/", methods=["POST"])(MotorcycleController.create_motorcycle)
motorcycles_bp.route("/", methods=["GET"])(MotorcycleController.get_motorcycles)
motorcycles_bp.route("/<string:moto_id>", methods=["GET"])(
    MotorcycleController.get_motorcycle_by_id
)
