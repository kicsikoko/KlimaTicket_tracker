import sqlite3

def fix_station_names():
    conn = sqlite3.connect('klimaticket.db')
    cursor = conn.cursor()

    print("🔍 Fixing in progress...")

    # 1. Departure
    cursor.execute("""
        UPDATE trips 
        SET origin = 'Wien' 
        WHERE origin = 'Wien Meidling'
    """)
    
    # 2. Destination
    cursor.execute("""
        UPDATE trips 
        SET destination = 'Wien' 
        WHERE destination = 'Wien Meidling'
    """)

    conn.commit()
    
    #Check how many rows included
    changes = conn.total_changes
    conn.close()
    
    print(f"✅ Done! {changes} entries has changed.")

if __name__ == "__main__":
    fix_station_names()