import psycopg2
from psycopg2.extras import RealDictCursor
import os

# Configuración de PostgreSQL
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "motolog")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD") or input("Ingresa la contraseña de PostgreSQL: ")
DB_PORT = int(os.getenv("DB_PORT", 5432))


def get_db_connection():
    """Establece una conexión con la base de datos PostgreSQL y retorna el objeto de conexión."""
    conn = psycopg2.connect(
        host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD, port=DB_PORT
    )
    return conn


def init_db():
    """Inicializa la estructura de la base de datos (DDL)."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)

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

        # Migración: Añadir columna si no existe
        cursor.execute(
            "ALTER TABLE motorcycles ADD COLUMN IF NOT EXISTS oil_change_interval INTEGER DEFAULT 5000"
        )

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
        cursor.execute(
            "ALTER TABLE expenses ADD COLUMN IF NOT EXISTS liters REAL DEFAULT 0.0"
        )

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
        if cursor.fetchone()['count'] == 0:
            cursor.execute(
                "INSERT INTO settings (id, dark_mode, currency, measure_unit, speed_threshold) VALUES (%s, %s, %s, %s, %s)",
                ("default", 1, "USD", "km", 50.0),
            )

        conn.commit()
    finally:
        conn.close()
