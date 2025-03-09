import os
import json
import paho.mqtt.client as mqtt
import sqlite3

# Konfigurasi Solace
MQTT_HOST = os.getenv("SOLACE_HOST", "localhost")
MQTT_PORT = int(os.getenv("SOLACE_PORT", 1883))
MQTT_USERNAME = os.getenv("SOLACE_USERNAME", "default")
MQTT_PASSWORD = os.getenv("SOLACE_PASSWORD", "default")

# Koneksi ke SQLite
conn = sqlite3.connect("transactions.db", check_same_thread=False)
cursor = conn.cursor()

def on_message(client, userdata, message):
    """Terima response dari BI Fast dan log ke database."""
    payload = json.loads(message.payload.decode())
    transaction_id = payload["transaction_id"]
    status = payload["status"]
    completed_at = payload["completed_at"]

    # Update transaksi ke COMPLETED di DB
    cursor.execute("UPDATE transactions SET status=?, completed_at=? WHERE transaction_id=?",
                   (status, completed_at, transaction_id))
    conn.commit()
    print(f"[LOG] Transaction {transaction_id} -> {status} at {completed_at}")

def on_connect(client, userdata, flags, rc):
    """Subscribe ke transaksi response dari BI Fast."""
    print("[INFO] Connected to Solace MQTT broker")
    client.subscribe("transaction/response/#")

# Setup MQTT Client
client = mqtt.Client()
client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
client.on_connect = on_connect
client.on_message = on_message

# Koneksi ke broker dan mulai loop
print(f"[INFO] Connecting to MQTT broker at {MQTT_HOST}:{MQTT_PORT}...")
client.connect(MQTT_HOST, MQTT_PORT, 60)
client.loop_forever()
