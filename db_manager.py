import sqlite3

DB_NAME = "klimaticket.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    #Created the table for the trips
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS trips (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                   origin TEXT,
                   destination TEXT,
                   price_saved REAL)''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS prices (
                   route TEXT PRIMARY KEY,
                   price REAL)

    ''')
    #Upload default prices
    cursor.execute("INSERT OR IGNORE INTO prices VALUES ('Wien->Linz', 20.90)")
    cursor.execute("INSERT OR IGNORE INTO prices VALUES ('Linz->Wien', 20.90)")

    conn.commit()
    conn.close()

def get_price(route):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT price FROM prices WHERE route = ?", (route,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0

def log_trip(origin, destination, price):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO trips (origin, destination, price_saved) VALUES (?,?,?)",
        (origin, destination, price)
    )
    conn.commit()
    conn.close()

def get_stats():
    conn = sqlite3.connect(DB_NAME)
    cursor =    conn.cursor()
    cursor.execute("SELECT SUM(price_saved), COUNT(id) FROM trips")
    result = cursor.fetchone() #retrieve the result
    conn.close()
    return result