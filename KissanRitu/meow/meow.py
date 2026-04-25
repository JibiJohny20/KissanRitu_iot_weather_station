import sqlite3
import csv

conn = sqlite3.connect("sensor_data.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM sensors")
rows = cursor.fetchall()

with open("sensor_data.csv", "w", newline="") as f:
    writer = csv.writer(f)

    # write column names
    writer.writerow([i[0] for i in cursor.description])

    # write data
    writer.writerows(rows)

conn.close()

print("CSV file created: sensor_data.csv")