import requests
import json
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()
URL_BASE = os.getenv("URL_BASE")
ACCELERATOR_URL = f"{URL_BASE}/data"
ALARM_URL = f"{URL_BASE}/alarm"
SENSOR_IDS = ["mpu6050_sensor", "alarme_system"]

def get_accelerator_data():
    try:
        response = requests.post(
            ACCELERATOR_URL,
            headers={"x-api-key": os.getenv("API_KEY")},
            data=json.dumps({"sensor_ids": SENSOR_IDS})
        )
        response.raise_for_status()
        data = response.json()
        print("[DEBUG] Contenu brut reçu:", data)

        if isinstance(data, dict) and "body" in data:
            data = json.loads(data["body"])

        parsed = []
        for item in data:
            payload = item.get("payload", {})
            timestamp = item.get("timestamp")

            parsed.append({
                "timestamp": pd.to_datetime(timestamp, unit="s"),
                "x": float(payload.get("accel_x", 0)),
                "y": float(payload.get("accel_y", 0)),
                "z": float(payload.get("accel_z", 0)),
                "door_state": payload.get("door_state", "unknown"),
                "people_count": int(payload.get("people_count", 0))
            })

        df = pd.DataFrame(parsed)
        df = df.set_index("timestamp").sort_index()
        return df

    except Exception as e:
        print(f"[ERREUR] get_accelerator_data: {e}")
        return None

def get_alarm_data():
    try:
        response = requests.post(
            ALARM_URL,
            headers={"x-api-key": os.getenv("API_KEY")},
            data=json.dumps({})
        )
        response.raise_for_status()
        data = response.json()

        if isinstance(data, dict) and "body" in data:
            data = json.loads(data["body"])

        parsed = []
        for item in data:
            payload = item.get("payload", {})
            timestamp = item.get("timestamp")

            parsed.append({
                "timestamp": pd.to_datetime(timestamp, unit="s"),
                "alarm_state": payload.get("alarm_state", "unknown"),
                "user": payload.get("user", "unknown"),
            })

        df = pd.DataFrame(parsed)
        df = df.set_index("timestamp").sort_index()
        return df

    except Exception as e:
        print(f"[ERREUR] get_alarm_data: {e}")
        return None