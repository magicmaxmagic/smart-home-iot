import requests
import json
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()
URL_BASE = os.getenv("URL_BASE")
ACCELERATOR_URL = f"{URL_BASE}/data" 
TEMPERATURE_URL = f"{URL_BASE}/temp" 

def get_accelerator_data():
    """
    Récupère les données depuis l'API Gateway et les transforme en JSON utilisable.
    """
    response = requests.get(ACCELERATOR_URL, headers={"x-api-key": os.getenv("API_KEY")})
    response.raise_for_status()  # Vérifie si l'API renvoie une erreur
    data = response.json()
    # data = {'statusCode': 200, 'body': '[{"payload": {"acceleration": {"x": -0.24, "y": 0.0, "z": 0.9}, "timestamp": 1742096823.0}, "sensor_id": "MPU6050_1", "timestamp": 1742096823.0}, {"payload": {"acceleration": {"x": -0.25, "y": -0.01, "z": 0.91}, "timestamp": 1742097401.0}, "sensor_id": "MPU6050_1", "timestamp": 1742097401.0}, {"payload": {"acceleration": {"x": -0.25, "y": -0.02, "z": 0.9}, "timestamp": 1742099259.0}, "sensor_id": "MPU6050_1", "timestamp": 1742099259.0}, {"payload": {"acceleration": {"x": -0.24, "y": 0.0, "z": 0.9}, "timestamp": 1742098168.0}, "sensor_id": "MPU6050_1", "timestamp": 1742098168.0}]'}

    # Vérifier si `body` est une string encodée et la convertir en JSON
    if isinstance(data, dict) and "body" in data:
        data = json.loads(data["body"])

    if data:
        if isinstance(data, str):
            data = json.loads(data)  # Conversion si encore sous forme de string

        if not isinstance(data, list):
            return
        # Préparation des données pour affichage
        flattened_data = []
        for item in data:
            payload = item.get("payload", {})
            acceleration = payload.get("acceleration", {})
            timestamp = item.get("timestamp")
            sensor_id = item.get("sensor_id", "Unknown")

            if timestamp is not None:
                flattened_data.append({
                    "timestamp": timestamp,
                    "sensor_id": sensor_id,
                    "x": acceleration.get("x"),
                    "y": acceleration.get("y"),
                    "z": acceleration.get("z"),
                })
                
        df = pd.DataFrame(flattened_data)
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
        df = df.set_index("timestamp")

        # Convertir toutes les colonnes numériques en `float`
        for col in ["x", "y", "z"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        # Melt les colonnes pour affichage
        # df_melted = df.reset_index().melt("timestamp", var_name="variable", value_name="value")

    return df

def get_temp_data():
    ...

if __name__ == "__main__":
    print(get_accelerator_data())