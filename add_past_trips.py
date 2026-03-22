import sqlite3
import os
from datetime import datetime

DB_NAME = "klimaticket.db"

def add_historical_trip(date_str, origin, destination, price):
    """
    date_str format: 'YYYY-MM-DD HH:MM:SS'
    for example: '2025-11-15 08:30:00'
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO trips (date, origin, destination, price_saved)
        VALUES (?, ?, ?, ?)
    ''', (date_str, origin, destination, price))
    conn.commit()
    conn.close()
    print(f"✅ Mentve: {date_str} | {origin} -> {destination}")

# --- Giving the pst data ---
past_trips = [
    ("2025-10-11 09:31:00", "Wien", "Linz", 20.90),
    ("2025-10-11 20:27:00", "Linz", "Wien", 20.90),
    ("2025-10-15 09:42:00", "Wien", "Linz", 20.90),
    ("2025-10-16 10:43:00", "Linz", "Wien", 20.90),
    ("2025-10-18 07:40:00", "Wien", "Linz", 20.90),
    ("2025-10-19 11:45:00", "Linz", "Wien", 20.90),
    ("2025-10-22 18:02:00", "Wien", "Linz", 20.90),
    ("2025-10-24 16:24:00", "Linz", "Wien", 20.90),
    ("2025-10-24 20:02:00", "Wien", "Linz", 20.90),
    ("2025-10-25 05:19:00", "Linz", "Wien", 20.90),
    ("2025-10-28 17:21:00", "Wien", "Linz", 20.90),
    ("2025-10-29 08:32:00", "Linz", "Wien", 20.90),
    ("2025-11-28 17:35:00", "Wien", "Linz", 20.90),
    ("2025-11-29 09:55:00", "Linz", "Wien", 20.90),
    ("2025-12-04 13:02:00", "Wien", "Linz", 20.90),
    ("2025-12-05 19:42:00", "Linz", "Wien", 20.90),
    ("2025-12-09 15:02:00", "Wien", "Linz", 20.90),
    ("2025-12-10 18:45:00", "Linz", "Wien", 20.90),
    ("2025-12-11 08:34:00", "Wien", "Linz", 20.90),
    ("2025-12-11 18:49:00", "Linz", "Wien", 20.90),
    ("2025-12-12 07:34:00", "Wien", "Hegyeshalom", 11.70),
    ("2025-12-16 20:22:00", "Hegyeshalom", "Wien", 11.70),
    ("2025-12-17 11:22:00", "Wien", "Linz", 20.90),
    ("2025-12-18 10:32:00", "Linz", "Wien", 20.90),
    ("2026-01-09 13:02:00", "Wien", "Linz", 20.90),
    ("2026-01-10 17:45:00", "Linz", "Wien", 20.90),
    ("2026-03-10 13:04:00", "Wien", "Linz", 20.90),
    ("2026-03-11 10:02:00", "Linz", "Wien", 20.90),
    ("2026-03-12 17:35:00", "Wien", "Linz", 20.90),
    ("2026-03-13 14:06:00", "Linz", "Wien", 20.90),
    ("2026-03-17 12:55:00", "Wien", "Linz", 20.90),
    ("2026-03-18 10:29:00", "Linz", "Wien", 42.90),
]

for trip in past_trips:
    add_historical_trip(trip[0], trip[1], trip[2], trip[3])

print("\n🚀 Data's imported sucessfully!")