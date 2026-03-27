#!/usr/bin/env python
"""Verify that seed data was correctly populated in the database."""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "backend", "motolog.db")

def verify_database():
    """Check database contents."""
    if not os.path.exists(DB_PATH):
        print("❌ Database file not found")
        return False
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check motorcycles
        cursor.execute("SELECT COUNT(*) FROM motorcycles")
        moto_count = cursor.fetchone()[0]
        
        # Check trips
        cursor.execute("SELECT COUNT(*) FROM trips")
        trips_count = cursor.fetchone()[0]
        
        # Check expenses
        cursor.execute("SELECT COUNT(*) FROM expenses")
        expenses_count = cursor.fetchone()[0]
        
        # Check maintenance
        cursor.execute("SELECT COUNT(*) FROM maintenance")
        services_count = cursor.fetchone()[0]
        
        # Check incomes
        cursor.execute("SELECT COUNT(*) FROM incomes")
        incomes_count = cursor.fetchone()[0]
        
        print(f"✓ Database file: {DB_PATH}")
        print(f"✓ Motorcycles: {moto_count}")
        print(f"✓ Trips: {trips_count}")
        print(f"✓ Expenses: {expenses_count}")
        print(f"✓ Maintenance Services: {services_count}")
        print(f"✓ Incomes: {incomes_count}")
        print()
        
        # Get motorcycle details
        cursor.execute("SELECT make, model, year, current_mileage FROM motorcycles LIMIT 1")
        moto = cursor.fetchone()
        if moto:
            print(f"Motorcycle: {moto[0]} {moto[1]} ({moto[2]}) - Mileage: {moto[3]} km")
        
        # Get fuel expenses
        cursor.execute("SELECT description, amount, liters FROM expenses WHERE category='Combustible' ORDER BY date DESC LIMIT 1")
        fuel = cursor.fetchone()
        if fuel:
            print(f"Latest fuel purchase: {fuel[0]} - ${fuel[1]:,.0f} ({fuel[2]:.1f} liters)")
        
        # Calculate efficiency
        cursor.execute("""
            SELECT SUM(distance_km), 
                   (SELECT SUM(liters) FROM expenses WHERE category='Combustible') as total_liters
            FROM trips
        """)
        result = cursor.fetchone()
        if result[0] and result[1] and result[1] > 0:
            efficiency = result[0] / result[1]
            print(f"Current fuel efficiency: {efficiency:.1f} km/L")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error checking database: {e}")
        conn.close()
        return False

if __name__ == "__main__":
    print("📊 Verifying MotoLog Database Seed Data\n")
    verify_database()
