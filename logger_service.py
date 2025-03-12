import os
import json
import paho.mqtt.client as mqtt
import sqlite3
from dotenv import load_dotenv

# Load env
load_dotenv()

# Konfigurasi Solace
MQTT_HOST = os.getenv("SOLACE_HOST")
MQTT_PORT = int(os.getenv("SOLACE_PORT"))
MQTT_USERNAME = os.getenv("SOLACE_USERNAME")
MQTT_PASSWORD = os.getenv("SOLACE_PASSWORD")

# Koneksi ke SQLite
DB_PATH = os.getenv("SQLITE_DB_PATH")
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = conn.cursor()

def on_message(client, userdata, message):
    """Terima response dari BI Fast dan log ke database."""
    payload = json.loads(message.payload.decode())
    transaction_id = payload["transaction_id"]
    status = payload["status"]
    completed_at = payload["completed_at"]

    cursor.execute("UPDATE transactions SET status=?, completed_at=? WHERE transaction_id=?",
                   (status, completed_at, transaction_id))
    conn.commit()
    print(f"[LOG] Transaction {transaction_id} -> {status} at {completed_at}")

def on_connect(client, userdata, flags, rc):
    """Subscribe ke transaksi yang telah selesai."""
    print("[INFO] Connected to Solace MQTT broker")
    client.subscribe("banking/+/+/completed/+")
    print("[INFO] Subscribed to banking/+/+/completed/+")

client = mqtt.Client()
client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
client.on_connect = on_connect
client.on_message = on_message

print(f"[INFO] Connecting to MQTT broker at {MQTT_HOST}:{MQTT_PORT}...")
client.connect(MQTT_HOST, MQTT_PORT, 60)
client.loop_forever()
