import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "motolog.db")


def get_db_connection():
    """Establece una conexión con la base de datos SQLite y retorna el objeto de conexión."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Permite acceder a las columnas por nombre
    return conn


def init_db():
    """Inicializa la estructura de la base de datos (DDL)."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        # Tabla Motorcycles
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS motorcycles (
                id TEXT PRIMARY KEY,
                make TEXT NOT NULL,
                model TEXT NOT NULL,
                year INTEGER NOT NULL,
                vin TEXT,
                current_mileage INTEGER DEFAULT 0,
                oil_change_interval INTEGER DEFAULT 5000
            )
        """
        )

        # Migración: Añadir columna si no existe (SQLite no soporta ADD COLUMN IF NOT EXISTS)
        try:
            cursor.execute(
                "ALTER TABLE motorcycles ADD COLUMN oil_change_interval INTEGER DEFAULT 5000"
            )
        except sqlite3.OperationalError:
            pass  # La columna ya existe

        # Tabla Trips
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS trips (
                id TEXT PRIMARY KEY,
                motorcycle_id TEXT NOT NULL,
                distance_km REAL NOT NULL,
                max_speed_kmh REAL DEFAULT 0.0,
                date TEXT NOT NULL,
                title TEXT,
                description TEXT,
                FOREIGN KEY (motorcycle_id) REFERENCES motorcycles (id)
            )
        """
        )

        # Tabla Maintenance
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS maintenance (
                id TEXT PRIMARY KEY,
                motorcycle_id TEXT NOT NULL,
                service_type TEXT NOT NULL,
                date TEXT NOT NULL,
                mileage_at_service INTEGER DEFAULT 0,
                cost REAL DEFAULT 0.0,
                notes TEXT,
                FOREIGN KEY (motorcycle_id) REFERENCES motorcycles (id)
            )
        """
        )

        # Tabla Expenses
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS expenses (
                id TEXT PRIMARY KEY,
                motorcycle_id TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                date TEXT NOT NULL,
                description TEXT,
                liters REAL DEFAULT 0.0,
                FOREIGN KEY (motorcycle_id) REFERENCES motorcycles (id)
            )
        """
        )

        # Migración: Añadir columna liters si no existe
        try:
            cursor.execute("ALTER TABLE expenses ADD COLUMN liters REAL DEFAULT 0.0")
        except sqlite3.OperationalError:
            pass

        # Tabla Incomes (Ingresos)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS incomes (
                id TEXT PRIMARY KEY,
                motorcycle_id TEXT NOT NULL,
                amount REAL NOT NULL,
                date TEXT NOT NULL,
                description TEXT,
                platform TEXT,
                hours_worked REAL DEFAULT 0.0,
                FOREIGN KEY (motorcycle_id) REFERENCES motorcycles (id)
            )
        """
        )

        # Tabla Settings (Configuración de la App)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS settings (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                dark_mode INTEGER DEFAULT 1,
                currency TEXT DEFAULT 'USD',
                measure_unit TEXT DEFAULT 'km',
                speed_threshold REAL DEFAULT 50.0
            )
        """
        )

        # Insertar configuración por defecto si no existe
        cursor.execute("SELECT COUNT(*) FROM settings")
        if cursor.fetchone()[0] == 0:
            cursor.execute(
                "INSERT INTO settings (id, dark_mode, currency, measure_unit, speed_threshold) VALUES (?, ?, ?, ?, ?)",
                ("default", 1, "USD", "km", 50.0),
            )

        conn.commit()
    finally:
        conn.close()
