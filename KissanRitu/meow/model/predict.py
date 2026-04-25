import pickle
import pandas as pd
from datetime import datetime

# load model
model = pickle.load(open('model/weather_model.pkl', 'rb'))
scaler = pickle.load(open('model/scaler.pkl', 'rb'))


def preprocess(sensor):
    df = pd.DataFrame([sensor])

    df['sealevelpressure'] = df['pressure']
    df['solarradiation'] = df['lux']
    df['precipprob'] = df['precipitation']

    df['dew'] = df['temp'] - ((100 - df['humidity']) / 5)

    df['winddir'] = 180
    df['windspeed'] = 5

    df['preciptype'] = df['precipitation'].apply(lambda x: 1 if x > 0 else 0)

    df['temp_change'] = 0
    df['spike'] = 0
    df['rain'] = df['precipprob'].apply(lambda x: 1 if x > 50 else 0)
    df['temp_avg_3'] = df['temp']
    df['heat_wave'] = df['temp'].apply(lambda x: 1 if x > 35 else 0)

    df['precip_change'] = 0
    df['sudden_rain'] = 0

    df['wind_change'] = 0
    df['wind_spike'] = 0

    df['hour'] = datetime.now().hour

    df['temp_norm'] = df['temp'] / 50
    df['humidity_norm'] = df['humidity'] / 100
    df['wind_norm'] = df['windspeed'] / 50

    df['stress_index'] = (
        df['temp_norm'] * 0.35 +
        df['humidity_norm'] * 0.25 +
        (df['co2'] / 1000) * 0.25 +
        (df['dust'] / 500) * 0.15
    )

    features = [
        'temp', 'dew', 'humidity', 'sealevelpressure', 'winddir',
        'solarradiation', 'windspeed', 'precipprob', 'preciptype',
        'temp_change', 'spike', 'rain', 'temp_avg_3', 'heat_wave',
        'precip_change', 'sudden_rain', 'wind_change', 'wind_spike',
        'hour', 'temp_norm', 'humidity_norm', 'wind_norm', 'stress_index'
    ]

    return df[features]


def predict_weather(sensor_data):
    df = preprocess(sensor_data)
    df_scaled = scaler.transform(df)
    prediction = model.predict(df_scaled)
    return prediction[0]