import sqlite3

DB_FILE = "sensor_data.db"

conn = sqlite3.connect(DB_FILE)
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS sensors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    co2 INTEGER,
    pm1 INTEGER,
    pm25 INTEGER,
    pm10 INTEGER,
    temp TEXT,
    humidity TEXT,
    lux TEXT,
    pressure TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
''')

conn.commit()
conn.close()
print("Database created with correct schema!")