from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import sqlite3
import os

# ✅ ML IMPORT
from model.predict import predict_weather

app = Flask(__name__)
CORS(app)

# ✅ DB PATH
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "sensor_data.db")


# ------------------ DB FUNCTIONS ------------------
def insert_data(co2, pm1, pm25, pm10, temp, humidity, lux, pressure, timestamp=None):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    if timestamp:
        c.execute('''
            INSERT INTO sensors (co2, pm1, pm25, pm10, temp, humidity, lux, pressure, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (co2, pm1, pm25, pm10, temp, humidity, lux, pressure, timestamp))
    else:
        c.execute('''
            INSERT INTO sensors (co2, pm1, pm25, pm10, temp, humidity, lux, pressure)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (co2, pm1, pm25, pm10, temp, humidity, lux, pressure))

    conn.commit()
    conn.close()


def fetch_all():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        SELECT id, co2, pm1, pm25, pm10, temp, humidity, lux, pressure, timestamp
        FROM sensors
        ORDER BY timestamp DESC
        LIMIT 100
    ''')
    rows = c.fetchall()
    conn.close()
    return rows


def row_to_dict(r):
    return {
        "id":        r[0],
        "co2":       r[1],
        "pm1":       r[2],
        "pm25":      r[3],
        "aqi":       r[3],
        "pm10":      r[4],
        "temp":      r[5],
        "humidity":  r[6],
        "lux":       r[7],
        "pressure":  r[8],
        "timestamp": r[9]
    }


# ------------------ PREPARE DATA FOR MODEL ------------------
def prepare_sensor_for_model(data):
    return {
        "temp": float(data["temp"]),
        "humidity": float(data["humidity"]),
        "pressure": float(data["pressure"]),
        "lux": float(data["lux"]),
        "precipitation": 0,  # no sensor → default
        "co2": float(data["co2"]),
        "dust": float(data["pm25"])  # using PM2.5
    }


# ------------------ API: RECEIVE DATA ------------------
@app.route("/data", methods=["POST"])
def receive_data():
    data = request.get_json()

    if not data:
        return jsonify({"status": "fail", "reason": "No JSON received"}), 400

    try:
        insert_data(
            int(data.get("co2", 0)),
            int(data.get("pm1", 0)),
            int(data.get("pm25", 0)),
            int(data.get("pm10", 0)),
            data.get("temp", ""),
            data.get("humidity", ""),
            data.get("lux", ""),
            data.get("pressure", ""),
            data.get("timestamp", None)
        )
        return jsonify({"status": "success"}), 200

    except Exception as e:
        return jsonify({"status": "fail", "reason": str(e)}), 500


# ------------------ API: GET LATEST DATA + ML ------------------
@app.route("/latest")
def latest_data():
    rows = fetch_all()

    if not rows:
        return jsonify({})

    data = row_to_dict(rows[0])

    try:
        sensor_input = prepare_sensor_for_model(data)
        prediction = predict_weather(sensor_input)
        data["prediction"] = int(prediction)
    except Exception as e:
        data["prediction_error"] = str(e)

    return jsonify(data)


# ------------------ API: GET HISTORY ------------------
@app.route("/history")
def history_data():
    rows = fetch_all()
    return jsonify([row_to_dict(r) for r in rows])


# ------------------ DASHBOARD (WITH ML) ------------------
@app.route("/")
def dashboard():
    rows = fetch_all()

    processed_rows = []

    for r in rows:
        data = row_to_dict(r)

        try:
            sensor_input = prepare_sensor_for_model(data)
            prediction = predict_weather(sensor_input)
            data["prediction"] = int(prediction)

            # 🔥 SMART ALERTS
            if data["co2"] > 800:
                data["alert"] = "⚠️ Poor Air Quality"
            elif float(data["temp"]) > 35:
                data["alert"] = "🔥 Heatwave"
            else:
                data["alert"] = "✅ Normal"

        except Exception as e:
            data["prediction"] = "Error"
            data["alert"] = "Error"

        processed_rows.append(data)

    return render_template("dashboard.html", rows=processed_rows)


# ------------------ RUN APP ------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True, threaded=True)

