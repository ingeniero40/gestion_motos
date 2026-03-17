from flask import Blueprint
from .controllers import ExpenseController

# Definición del Blueprint para el bounded context "expenses"
expenses_bp = Blueprint("expenses", __name__)

# Mapeo de rutas a Controladores
expenses_bp.route("/", methods=["POST"])(ExpenseController.create_expense)
expenses_bp.route("/", methods=["GET"])(ExpenseController.get_expenses)
expenses_bp.route("/motorcycle/<string:motorcycle_id>", methods=["GET"])(
    ExpenseController.get_expenses_by_motorcycle
)
