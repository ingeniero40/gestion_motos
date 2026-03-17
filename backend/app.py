import os
from flask import Flask, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Cargar variables de entorno
load_dotenv()


def create_app():
    """
    Application factory for the Flask backend.
    """
    # Establecer la carpeta base correcta para templates y static
    base_dir = os.path.abspath(os.path.dirname(__file__))
    app = Flask(
        __name__,
        template_folder=os.path.join(base_dir, "templates"),
        static_folder=os.path.join(base_dir, "static"),
    )

    # Permitir peticiones desde el frontend (CORS)
    CORS(app)

    # Configuraciones básicas
    app.config["JSON_AS_ASCII"] = False

    # Inicializar Base de Datos SQLite
    from infrastructure.db import init_db
    from motorcycles.services import motorcycle_service

    init_db()

    # Seed data: Asegurar que exista al menos una moto para propósitos de UI
    motos = motorcycle_service.get_all()
    if not motos:
        motorcycle_service.create(
            {
                "make": "Yamaha",
                "model": "MT-07",
                "year": 2023,
                "vin": "JYAR04150000XXXX",
                "current_mileage": 12450,
            }
        )

    def get_validated_mileage_since_last_oil(moto, services, trips):
        # Mantenemos esta función por compatibilidad con código antiguo temporalmente
        return int(moto.current_mileage), 0

    @app.route("/", methods=["GET"])
    def index():
        """
        Ruta principal: Dashboard dinámico con estadísticas por mes y año.
        """
        from motorcycles.services import motorcycle_service
        from expenses.services import expense_service
        from maintenance.services import maintenance_service
        from trips.services import trip_service
        from collections import defaultdict
        from flask import request
        import json

        moto = motorcycle_service.get_all()[0] if motorcycle_service.get_all() else None

        selected_year = request.args.get("year", str(datetime.now().year))

        # --- Agregaciones de Gastos ---
        all_expenses = expense_service.get_by_motorcycle_id(moto.id) if moto else []

        # Años disponibles para el filtro
        years_available = sorted(
            set(e.date[:4] for e in all_expenses if e.date), reverse=True
        )
        if str(datetime.now().year) not in years_available:
            years_available.insert(0, str(datetime.now().year))

        # Gastos del año seleccionado agrupados por mes
        MONTHS_ES = [
            "Ene",
            "Feb",
            "Mar",
            "Abr",
            "May",
            "Jun",
            "Jul",
            "Ago",
            "Sep",
            "Oct",
            "Nov",
            "Dic",
        ]
        monthly_totals = defaultdict(float)
        for e in all_expenses:
            if e.date and e.date[:4] == selected_year:
                month_idx = int(e.date[5:7]) - 1
                monthly_totals[month_idx] += e.amount

        chart_labels = json.dumps(MONTHS_ES)
        chart_data = json.dumps([round(monthly_totals.get(i, 0), 2) for i in range(12)])

        # Total del año seleccionado
        total_year = sum(monthly_totals.values())

        # Mes con mayor gasto
        peak_month = (
            max(monthly_totals, key=monthly_totals.get) if monthly_totals else None
        )
        peak_month_name = MONTHS_ES[peak_month] if peak_month is not None else "—"
        peak_month_value = (
            monthly_totals.get(peak_month, 0) if peak_month is not None else 0
        )

        # --- Servicios ---
        all_services = maintenance_service.get_by_motorcycle_id(moto.id) if moto else []
        total_services = len(all_services)

        # --- Actividad reciente (últimos 5 items combinados) ---
        recent_activity = []
        for e in sorted(all_expenses, key=lambda x: x.date, reverse=True)[:3]:
            recent_activity.append(
                {
                    "type": "expense",
                    "icon": (
                        "ph-gas-pump"
                        if e.category == "Combustible"
                        else "ph-shopping-bag"
                    ),
                    "color": (
                        "var(--accent-orange)"
                        if e.category == "Combustible"
                        else "var(--accent-blue)"
                    ),
                    "title": e.description,
                    "subtitle": f"{e.date} • ${e.amount:,.2f}",
                }
            )
        for s in sorted(all_services, key=lambda x: x.date, reverse=True)[:2]:
            recent_activity.append(
                {
                    "type": "service",
                    "icon": "ph-wrench",
                    "color": "var(--accent-blue)",
                    "title": s.service_type,
                    "subtitle": f"{s.date} • {s.mileage_at_service:,} km",
                }
            )
        # Reordenar por fecha
        recent_activity.sort(key=lambda x: str(x["subtitle"])[:10], reverse=True)
        recent_activity = recent_activity[:5]

        # --- Viajes y Velocidad ---
        all_trips = trip_service.get_by_motorcycle_id(moto.id) if moto else []
        max_speed_record = max([t.max_speed_kmh for t in all_trips] + [0])
        total_distance_trips = sum(t.distance_km for t in all_trips)

        # --- Rendimiento de Gasolina (Último Tanque) ---
        fuel_expenses = [e for e in all_expenses if e.category == "Combustible"]
        fuel_expenses.sort(key=lambda x: x.date, reverse=True)
        
        fuel_efficiency = 0
        total_fuel_gallons = 0
        
        if fuel_expenses:
            last_fuel = fuel_expenses[0]
            total_fuel_gallons = last_fuel.liters
            # Distancia de viajes registrados en o después de la última recarga
            dist_since_last_fuel = sum(t.distance_km for t in all_trips if t.date and t.date >= last_fuel.date)
            
            if total_fuel_gallons > 0:
                fuel_efficiency = dist_since_last_fuel / total_fuel_gallons
        total_km_validated = moto.current_mileage if moto else 0
        oil_life = 0

        if moto:
            # Cálculo de Vida de Aceite: El odómetro actual es directamente la distancia desde el último cambio!
            interval = (
                moto.oil_change_interval if moto.oil_change_interval > 0 else 1500
            )
            oil_life = max(0, 100 - (total_km_validated / interval) * 100)

        return render_template(
            "index.html",
            moto=moto,
            total_km_validated=total_km_validated,
            oil_life=int(oil_life),
            chart_labels=chart_labels,
            chart_data=chart_data,
            selected_year=selected_year,
            years_available=years_available,
            total_year=total_year,
            peak_month_name=peak_month_name,
            peak_month_value=peak_month_value,
            total_services=total_services,
            recent_activity=recent_activity,
            max_speed_record=max_speed_record,
            total_distance_trips=total_distance_trips,
            fuel_efficiency=round(fuel_efficiency, 2),
            total_fuel_liters=round(total_fuel_gallons, 2), # Pasando galones al template
        )

    @app.route("/trips", methods=["GET", "POST"])
    def trips_view():
        from motorcycles.services import motorcycle_service
        from trips.services import trip_service
        from flask import request, redirect, url_for

        moto = motorcycle_service.get_all()[0] if motorcycle_service.get_all() else None

        if request.method == "POST" and moto:
            distance_km = float(request.form.get("distance_km", 0.0))
            max_speed = float(request.form.get("max_speed_kmh", 0.0))

            trip_service.create(
                {
                    "motorcycle_id": moto.id,
                    "title": request.form.get("title"),
                    "date": request.form.get("date"),
                    "distance_km": distance_km,
                    "max_speed_kmh": max_speed,
                    "description": request.form.get("description", ""),
                }
            )
            # Sincronizar Odómetro
            moto.current_mileage += int(round(distance_km))
            motorcycle_service.update_by_id(moto.id, moto.to_dict())

            # Detección de exceso de velocidad para la alerta visual inmediata
            speed_alert = max_speed > 60

            # Recargar datos para renderizar con la alerta
            all_trips = trip_service.get_by_motorcycle_id(moto.id)
            all_trips.sort(key=lambda x: x.date if x.date else "", reverse=True)
            trips_years = sorted(
                set(t.date[:4] for t in all_trips if t.date), reverse=True
            )

            return render_template(
                "trips.html",
                trips=all_trips[
                    :5
                ],  # Mostrar primeros 5 (paginación simple para el refresh)
                moto=moto,
                page=1,
                total_pages=(len(all_trips) + 4) // 5,
                has_next=len(all_trips) > 5,
                has_prev=False,
                search_query="",
                selected_year="",
                trips_years=trips_years,
                sort_order="desc",
                speed_alert=speed_alert,
                speed_value=max_speed,
            )

        all_trips = trip_service.get_by_motorcycle_id(moto.id) if moto else []

        # Filtros
        search_query = request.args.get("search", "").lower()
        selected_year = request.args.get("year", "")
        sort_order = request.args.get("sort", "desc")

        if search_query:
            all_trips = [
                t
                for t in all_trips
                if search_query in t.title.lower()
                or search_query in t.description.lower()
            ]

        if selected_year:
            all_trips = [
                t for t in all_trips if t.date and t.date.startswith(selected_year)
            ]

        # Ordenación
        reverse_sort = True if sort_order == "desc" else False
        all_trips.sort(key=lambda x: x.date if x.date else "", reverse=reverse_sort)

        # Años disponibles para filtro (de los viajes registrados)
        trips_years = sorted(set(t.date[:4] for t in all_trips if t.date), reverse=True)

        # Paginación
        page = int(request.args.get("page", 1))
        per_page = 5
        total_trips = len(all_trips)
        total_pages = (total_trips + per_page - 1) // per_page

        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        trips_page = all_trips[start_idx:end_idx]

        # Último viaje para persistencia en formulario
        last_trip = trip_service.get_last_by_motorcycle_id(moto.id) if moto else None

        return render_template(
            "trips.html",
            trips=trips_page,
            moto=moto,
            page=page,
            total_pages=total_pages,
            has_next=(page < total_pages),
            has_prev=(page > 1),
            search_query=search_query,
            selected_year=selected_year,
            trips_years=trips_years,
            sort_order=sort_order,
            last_trip=last_trip,
        )

    @app.route("/trips/update/<trip_id>", methods=["POST"])
    def update_trip(trip_id):
        from trips.services import trip_service
        from motorcycles.services import motorcycle_service
        from flask import request, redirect, url_for

        # Obtener el viaje antiguo para calcular la diferencia de KM
        old_trip = trip_service.get_by_id(trip_id)
        if not old_trip:
            return redirect(url_for("trips_view"))

        try:
            new_distance = float(request.form.get("distance_km", 0.0))
            new_max_speed = float(request.form.get("max_speed_kmh", 0.0))

            # Validación básica
            if new_distance < 0:
                new_distance = 0
            if new_max_speed < 0:
                new_max_speed = 0

            trip_data = {
                "title": request.form.get("title", "Viaje sin título"),
                "date": request.form.get("date"),
                "distance_km": new_distance,
                "max_speed_kmh": new_max_speed,
                "description": request.form.get("description", ""),
            }

            if trip_service.update(trip_id, trip_data):
                # Sincronizar Odómetro: sumar diferencia
                diff = new_distance - old_trip.distance_km
                moto = motorcycle_service.get_by_id(old_trip.motorcycle_id)
                if moto:
                    # Usar la diferencia acumulada para no perder decimales en el total si es posible,
                    # pero como current_mileage es int, redondeamos la diferencia.
                    moto.current_mileage += int(round(diff))
                    # Asegurar que no sea negativo
                    if moto.current_mileage < 0:
                        moto.current_mileage = 0
                    motorcycle_service.update_by_id(moto.id, moto.to_dict())

        except (ValueError, TypeError):
            # En caso de error de conversión, simplemente ignoramos la actualización del odómetro
            pass

        return redirect(url_for("trips_view"))

    @app.route("/trips/delete/<trip_id>", methods=["POST"])
    def delete_trip(trip_id):
        from trips.services import trip_service
        from motorcycles.services import motorcycle_service
        from flask import redirect, url_for

        trip = trip_service.get_by_id(trip_id)
        if trip:
            # Sincronizar Odómetro: restar distancia del viaje eliminado
            moto = motorcycle_service.get_by_id(trip.motorcycle_id)
            if moto:
                moto.current_mileage -= int(round(trip.distance_km))
                # Asegurar que no sea negativo
                if moto.current_mileage < 0:
                    moto.current_mileage = 0
                motorcycle_service.update_by_id(moto.id, moto.to_dict())

            trip_service.delete(trip_id)

        return redirect(url_for("trips_view"))

    @app.route("/services", methods=["GET", "POST"])
    def services_view():
        from motorcycles.services import motorcycle_service
        from maintenance.services import maintenance_service
        from flask import request, redirect, url_for

        moto = motorcycle_service.get_all()[0] if motorcycle_service.get_all() else None

        if request.method == "POST" and moto:
            # Crear nuevo servicio
            service_mileage = int(request.form.get("mileage", 0))
            maintenance_service.create(
                {
                    "motorcycle_id": moto.id,
                    "service_type": request.form.get("service_type"),
                    "date": request.form.get("date"),
                    "mileage_at_service": service_mileage,
                    "cost": float(request.form.get("cost", 0.0)),
                    "notes": request.form.get("notes", ""),
                }
            )

            # Sincronizar Oodómetro si el servicio fue cambio de aceite
            service_type_lower = request.form.get("service_type", "").lower()
            if "aceite" in service_type_lower:
                from motorcycles.services import motorcycle_service
                moto.current_mileage = 0
                motorcycle_service.update_by_id(moto.id, moto.to_dict())

            return redirect(url_for("services_view"))

        services = maintenance_service.get_by_motorcycle_id(moto.id) if moto else []
        # Ordenar por fecha descendente
        services.sort(key=lambda x: x.date, reverse=True)

        # Calcular próximo mantenimiento basado en el intervalo configurado
        next_service_mileage = 0
        km_remaining_to_next = 0
        if moto:
            interval = (
                moto.oil_change_interval if moto.oil_change_interval > 0 else 1500
            )
            total_km_validated = moto.current_mileage
            next_service_mileage = interval
            km_remaining_to_next = max(0, next_service_mileage - total_km_validated)

        return render_template(
            "services.html",
            services=services,
            moto=moto,
            next_service_mileage=next_service_mileage,
            km_remaining_to_next=km_remaining_to_next,
        )

    @app.route("/expenses", methods=["GET", "POST"])
    def expenses_view():
        from motorcycles.services import motorcycle_service
        from expenses.services import expense_service
        from flask import request, redirect, url_for

        moto = motorcycle_service.get_all()[0] if motorcycle_service.get_all() else None

        if request.method == "POST" and moto:
            # Crear nuevo gasto
            expense_service.create(
                {
                    "motorcycle_id": moto.id,
                    "amount": float(request.form.get("amount", 0.0)),
                    "category": request.form.get("category"),
                    "date": request.form.get("date"),
                    "description": request.form.get("description", ""),
                }
            )
            return redirect(url_for("expenses_view"))

        expenses = expense_service.get_by_motorcycle_id(moto.id) if moto else []
        # Ordenar por fecha descendente
        expenses.sort(key=lambda x: x.date, reverse=True)
        total_month = sum(e.amount for e in expenses)  # Simplificación para demo
        return render_template(
            "expenses.html", expenses=expenses, total_month=total_month
        )

    @app.route("/expenses/delete/<expense_id>", methods=["POST"])
    def delete_expense(expense_id):
        from expenses.services import expense_service
        from flask import redirect, url_for

        expense_service.delete_by_id(expense_id)
        return redirect(url_for("expenses_view"))

    @app.route("/incomes", methods=["GET", "POST"])
    def incomes_view():
        from motorcycles.services import motorcycle_service
        from incomes.services import income_service
        from flask import request, redirect, url_for

        moto = motorcycle_service.get_all()[0] if motorcycle_service.get_all() else None
        if request.method == "POST" and moto:
            income_service.create(
                {
                    "motorcycle_id": moto.id,
                    "amount": float(request.form.get("amount", 0.0)),
                    "date": request.form.get("date"),
                    "description": request.form.get("description", ""),
                    "platform": request.form.get("platform", ""),
                    "hours_worked": float(request.form.get("hours", 0.0)),
                }
            )
            return redirect(url_for("incomes_view"))

        incomes = income_service.get_by_motorcycle_id(moto.id) if moto else []
        incomes.sort(key=lambda x: x["date"], reverse=True)
        return render_template("incomes.html", incomes=incomes)

    @app.route("/incomes/delete/<income_id>", methods=["POST"])
    def delete_income(income_id):
        from infrastructure.db import get_db_connection
        from flask import redirect, url_for

        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM incomes WHERE id = ?", (income_id,))
            conn.commit()
        finally:
            conn.close()
        return redirect(url_for("incomes_view"))

    @app.route("/services/delete/<service_id>", methods=["POST"])
    def delete_service(service_id):
        from maintenance.services import maintenance_service
        from flask import redirect, url_for

        maintenance_service.delete_by_id(service_id)
        return redirect(url_for("services_view"))

    @app.route("/expenses/edit/<expense_id>", methods=["GET", "POST"])
    def edit_expense(expense_id):
        from expenses.services import expense_service
        from flask import request, redirect, url_for

        expense = expense_service.get_by_id(expense_id)
        if not expense:
            return redirect(url_for("expenses_view"))

        if request.method == "POST":
            expense_service.update_by_id(expense_id, request.form)
            return redirect(url_for("expenses_view"))

        return render_template("edit_expense.html", expense=expense)

    @app.route("/services/edit/<service_id>", methods=["GET", "POST"])
    def edit_service(service_id):
        from maintenance.services import maintenance_service
        from flask import request, redirect, url_for

        service = maintenance_service.get_by_id(service_id)
        if not service:
            return redirect(url_for("services_view"))

        if request.method == "POST":
            maintenance_service.update_by_id(service_id, request.form)
            return redirect(url_for("services_view"))

        return render_template("edit_service.html", service=service)

    @app.route("/profile", methods=["GET"])
    def profile_view():
        from motorcycles.services import motorcycle_service
        from expenses.services import expense_service
        from maintenance.services import maintenance_service

        moto = motorcycle_service.get_all()[0] if motorcycle_service.get_all() else None

        # Calcular estadísticas del perfil
        if moto:
            expenses = expense_service.get_by_motorcycle_id(moto.id)
            services = maintenance_service.get_by_motorcycle_id(moto.id)
            total_spent = sum(e.amount for e in expenses)
            total_services = len(services)
            last_service = (
                max(services, key=lambda s: s.date).date
                if services
                else "Sin registros"
            )
        else:
            total_spent, total_services, last_service = 0, 0, "—"

        return render_template(
            "profile.html",
            moto=moto,
            total_spent=total_spent,
            total_services=total_services,
            last_service=last_service,
        )

    @app.route("/profile/edit", methods=["GET", "POST"])
    def edit_motorcycle():
        from motorcycles.services import motorcycle_service
        from flask import request, redirect, url_for

        moto = motorcycle_service.get_all()[0] if motorcycle_service.get_all() else None
        if not moto:
            return redirect(url_for("profile_view"))

        if request.method == "POST":
            motorcycle_service.update_by_id(moto.id, request.form)
            return redirect(url_for("profile_view"))

        return render_template("edit_motorcycle.html", moto=moto)

    @app.route("/api/health", methods=["GET"])
    def health_check():
        """
        Endpoint básico para comprobar que el backend está funcionando.
        """
        return (
            jsonify({"status": "healthy", "message": "MotoLog Backend API is running"}),
            200,
        )

    @app.route("/analytics", methods=["GET"])
    def analytics_view():
        """
        Dashboard de Análisis Inteligente con KPIs avanzados y Predicciones.
        """
        from motorcycles.services import motorcycle_service
        from expenses.services import expense_service
        from maintenance.services import maintenance_service
        from trips.services import trip_service
        from incomes.services import income_service
        import calendar

        moto = motorcycle_service.get_all()[0] if motorcycle_service.get_all() else None
        if not moto:
            return redirect(url_for("index"))

        # Datos base
        all_expenses = expense_service.get_by_motorcycle_id(moto.id)
        all_services = maintenance_service.get_by_motorcycle_id(moto.id)
        all_trips = trip_service.get_by_motorcycle_id(moto.id)
        all_incomes = income_service.get_by_motorcycle_id(moto.id)

        now = datetime.now()
        today_str = now.strftime("%Y-%m-%d")
        month_str = now.strftime("%Y-%m")

        # --- 1. Análisis de Uso ---
        trips_today = [t for t in all_trips if t.date == today_str]
        trips_month = [t for t in all_trips if t.date and t.date.startswith(month_str)]

        km_today = sum(t.distance_km for t in trips_today)
        km_month = sum(t.distance_km for t in trips_month)

        days_in_month = (now - now.replace(day=1)).days + 1
        avg_km_day = km_month / days_in_month if days_in_month > 0 else 0

        # --- 2. Análisis de Combustible (A partir del último gasto registrado) ---
        fuel_expenses = [e for e in all_expenses if e.category == "Combustible"]
        fuel_expenses.sort(key=lambda x: x.date, reverse=True)
        fuel_month = [e for e in fuel_expenses if e.date.startswith(month_str)]

        total_fuel_gallons = sum(e.liters for e in fuel_expenses)
        total_fuel_cost = sum(e.amount for e in fuel_expenses)
        
        yield_kml = 0
        cost_per_km_fuel = 0
        
        if fuel_expenses:
            last_fuel = fuel_expenses[0]
            dist_since_last_fuel = sum(t.distance_km for t in all_trips if t.date and t.date >= last_fuel.date)
            if last_fuel.liters > 0:
                yield_kml = dist_since_last_fuel / last_fuel.liters
            if dist_since_last_fuel > 0:
                cost_per_km_fuel = last_fuel.amount / dist_since_last_fuel

        total_dist = sum(t.distance_km for t in all_trips)

        # --- 3. Análisis de Mantenimiento ---
        total_maint_cost = sum(s.cost for s in all_services)
        maint_month = sum(s.cost for s in all_services if s.date.startswith(month_str))

        # Predicción Aceite
        total_km_validated = moto.current_mileage if moto else 0
        interval = moto.oil_change_interval or 1500
        km_to_next_oil = max(0, interval - total_km_validated)
        status_pct = max(0, 100 - (total_km_validated / interval) * 100)

        # --- 4. Análisis Financiero (Costos Operativos e Ingresos) ---
        income_month = sum(
            i["amount"] for i in all_incomes if i["date"].startswith(month_str)
        )
        expenses_month = sum(
            e.amount for e in all_expenses if e.date.startswith(month_str)
        )
        net_gain_month = income_month - expenses_month

        total_op_cost = sum(e.amount for e in all_expenses) + total_maint_cost
        total_cost_per_km = total_op_cost / total_dist if total_dist > 0 else 0

        # --- 5. Alertas ---
        alerts = []
        if km_to_next_oil < 500:
            alerts.append(
                {
                    "type": "warning",
                    "msg": f"Cambio de aceite próximo ({int(km_to_next_oil)} km)",
                }
            )

        if yield_kml and yield_kml > 130:
            alerts.append(
                {
                    "type": "warning",
                    "msg": "Rendimiento inusualmente alto o tanque vacío. Registre gasto de gasolina pronto.",
                }
            )
        elif yield_kml and yield_kml < 30:
            alerts.append(
                {
                    "type": "warning",
                    "msg": f"Bajo rendimiento de combutible detectado ({int(yield_kml)} km/Gal)",
                }
            )

        # --- Gráficas ---
        # Km por mes (últimos 6 meses)
        chart_km_labels = []
        chart_km_data = []
        for i in range(5, -1, -1):
            m_date = now - timedelta(days=i * 30)
            m_key = m_date.strftime("%Y-%m")
            m_name = calendar.month_name[m_date.month][:3]
            chart_km_labels.append(m_name)
            chart_km_data.append(
                sum(
                    t.distance_km
                    for t in all_trips
                    if t.date and t.date.startswith(m_key)
                )
            )

        # --- 6. Análisis de Seguridad (Alertas de Velocidad) ---
        speed_alerts_history = [t for t in all_trips if t.max_speed_kmh > 50]
        total_speed_alerts = len(speed_alerts_history)
        max_speed_record = max([t.max_speed_kmh for t in all_trips] + [0])
        recent_speed_alerts = sorted(
            speed_alerts_history, key=lambda x: x.date if x.date else "", reverse=True
        )[:3]

        return render_template(
            "analytics.html",
            moto=moto,
            km_today=round(km_today, 1),
            km_month=round(km_month, 1),
            avg_km_day=round(avg_km_day, 1),
            yield_kml=round(yield_kml, 1),
            cost_per_km=round(total_cost_per_km, 2),
            fuel_spend_month=round(sum(e.amount for e in fuel_month), 2),
            maint_spend_month=round(maint_month, 2),
            km_to_next_oil=int(km_to_next_oil),
            status_pct=int(status_pct),
            income_month=income_month,
            expenses_month=expenses_month,
            net_gain_month=net_gain_month,
            alerts=alerts,
            chart_km_labels=chart_km_labels,
            chart_km_data=chart_km_data,
            total_speed_alerts=total_speed_alerts,
            max_speed_record=max_speed_record,
            recent_speed_alerts=recent_speed_alerts,
        )

    # Importación de Blueprints
    from motorcycles.routes import motorcycles_bp
    from trips.routes import trips_bp
    from maintenance.routes import maintenance_bp
    from expenses.routes import expenses_bp

    # Registro de Blueprints
    app.register_blueprint(motorcycles_bp, url_prefix="/api/motorcycles")
    app.register_blueprint(trips_bp, url_prefix="/api/trips")
    app.register_blueprint(maintenance_bp, url_prefix="/api/maintenance")
    app.register_blueprint(expenses_bp, url_prefix="/api/expenses")

    return app


if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", 5000))
    # En desarrollo, debug=True permite recarga automática
    app.run(host="0.0.0.0", port=port, debug=True)



