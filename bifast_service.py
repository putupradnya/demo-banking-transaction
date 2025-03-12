import os
import json
import time
import random
import sqlite3
import paho.mqtt.client as mqtt
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

# Setup MQTT
client = mqtt.Client()
client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

def on_connect(client, userdata, flags, rc):
    """Callback saat MQTT terhubung."""
    if rc == 0:
        print("[INFO] Connected to Solace MQTT broker")
        client.subscribe("banking/+/+/created/+")
        print("[INFO] Subscribed to banking/+/+/created/+")
    else:
        print(f"[ERROR] Connection failed with code {rc}")

def on_message(client, userdata, message):
    """Callback saat menerima transaksi dari MQTT."""
    try:
        payload = json.loads(message.payload.decode())
        transaction_id = payload["transaction_id"]
        amount = payload["amount"]
        source = payload["source"]
        destination = payload["destination"]
        created_at = payload["created_at"]

        # Simulasi pemrosesan transaksi
        process_time = random.randint(3, 5)
        print(f"[PROCESSING] {transaction_id} - Processing for {process_time} seconds...")
        time.sleep(process_time / 10)

        completed_at = time.strftime("%Y-%m-%d %H:%M:%S")

        # Insert langsung sebagai "COMPLETED"
        cursor.execute("""
            UPDATE transactions SET status=?, completed_at=? WHERE transaction_id=?
        """, ("COMPLETED", completed_at, transaction_id))
        conn.commit()
        print(f"[UPDATED] {transaction_id} -> COMPLETED at {completed_at}")

        # Publish hasil ke topic dengan format baru
        topic = f"banking/{source}/{destination}/completed/{transaction_id}"
        response_payload = {
            "transaction_id": transaction_id,
            "source": source,
            "destination": destination,
            "amount": amount,
            "status": "COMPLETED",
            "created_at": created_at,
            "completed_at": completed_at
        }
        client.publish(topic, json.dumps(response_payload))
        print(f"[PUBLISHED] {transaction_id} completed -> {topic}")

    except Exception as e:
        print(f"[ERROR] Failed to process transaction: {e}")

client.on_connect = on_connect
client.on_message = on_message

print(f"[INFO] Connecting to MQTT broker at {MQTT_HOST}:{MQTT_PORT}...")
client.connect(MQTT_HOST, MQTT_PORT, 60)
client.loop_forever()
