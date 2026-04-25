import sqlite3

DB_FILE = "sensor_data.db"

conn = sqlite3.connect(DB_FILE)
c = conn.cursor()

# Check rows first (optional)
c.execute("SELECT * FROM sensors WHERE timestamp='26/03/14,23:15:01+22'")
rows = c.fetchall()
print("Rows to delete:", len(rows))

# Delete them
c.execute("DELETE FROM sensors WHERE timestamp='time-not-synced'")
conn.commit()

print("Deleted rows:", conn.total_changes)

conn.close()