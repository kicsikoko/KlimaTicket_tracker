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

def get_stats(start_date):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    query = ("SELECT SUM(price_saved), COUNT(id) FROM trips WHERE date >= ?")
    cursor.execute(query, (start_date,))
    result = cursor.fetchone()
    conn.close()
    return result

def delete_last_trip():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    #Search the highest number (ID) and delete
    cursor.execute("DELETE FROM trips WHERE id = (SELECT MAX(id) FROM trips)")
    conn.commit()
    conn.close()

def get_monthly_stats():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    #Search only those rows which year-month aligns with today's
    query = """
        SELECT SUM(price_saved), COUNT(id) 
        FROM trips 
        WHERE strftime('%Y-%m', date) = strftime('%Y-%m', 'now')
    """
    cursor.execute(query)
    result = cursor.fetchone()
    conn.close()
    return result #(monthly_sum, monthly_count)

def get_recent_trips(limit=5):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    #Request the most recent X trips in chronological order (newest at the top)
    query = "SELECT date, origin, destination, price_saved FROM trips ORDER BY id DESC LIMIT ?"
    cursor.execute(query, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_all_trips():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT date, origin, destination, price_saved FROM trips ORDER BY date ASC")
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_data_for_chart():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Csoportosítunk év és hónap szerint, hogy ne keveredjenek az évek
    query = """
        SELECT strftime('%Y-%m', date) as month, SUM(price_saved)
        FROM trips
        GROUP BY month
        ORDER BY month ASC
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    return rows # Format: [('2025-11', 140.5), ('2025-12', 90.2)...]

def get_cumulative_data():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # This is the magic of the "Window Function": it adds all previous months to each month
    query = """
        SELECT month, SUM(monthly_sum) OVER (ORDER BY month)
        FROM (
            SELECT strftime('%Y-%m', date) as month, SUM(price_saved) as monthly_sum
            FROM trips
            WHERE date >= '2025-10-06'
            GROUP BY month
        )
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    return rows # [('2025-10', 80), ('2025-11', 220), ...]

def get_savings_by_route_category(start_date):
    """
    Categorize the trips and calculate the total savings by category.
    Categories: Vienna-Linz, Hegyeshalom, Other
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # This is a "CASE" SQL query that labels the data on the fly
    query = """
        SELECT 
            CASE 
                -- If both cities are Vienna or Linz, then commuting
                WHEN (origin IN ('Wien', 'Linz') AND destination IN ('Wien', 'Linz')) THEN 'Wien-Linz'
                -- if anything Hegyeshalom
                WHEN (origin LIKE '%Hegyes%' OR destination LIKE '%Hegyes%') THEN 'Hegyeshalom'
                -- everything else
                ELSE 'Other (Custom)'
            END as route_category,
            SUM(price_saved) as total_saved
        FROM trips
        WHERE date >= ?
        GROUP BY route_category
    """
    cursor.execute(query, (start_date,))
    rows = cursor.fetchall()
    conn.close()
    
    # We'll convert this into a dictionary (dict) for easier processing: {'Wien-Linz': 500, 'Other': 100}
    return {row[0]: row[1] for row in rows}