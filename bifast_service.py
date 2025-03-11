import os
import json
import time
import random
import sqlite3
import paho.mqtt.client as mqtt
from dotenv import load_dotenv

# load env
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
        client.subscribe("transaction/request")
        print("[INFO] Subscribed to transaction/request")
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

        # Simulasi pemrosesan transaksi (delay 3-5 detik)
        process_time = random.randint(3, 5)
        print(f"[PROCESSING] {transaction_id} - Processing for {process_time} seconds...")
        time.sleep(process_time/500)

        completed_at = time.strftime("%Y-%m-%d %H:%M:%S")

        # Insert langsung sebagai "COMPLETED"
        cursor.execute("""
            INSERT INTO transactions (transaction_id, source, destination, amount, status, created_at, completed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (transaction_id, source, destination, amount, "COMPLETED", created_at, completed_at))
        conn.commit()
        print(f"[INSERTED] {transaction_id} -> COMPLETED at {completed_at}")

        # Kirim response ke MQTT
        response_payload = {
            "transaction_id": transaction_id,
            "source": source,
            "destination": destination,
            "amount": amount,
            "status": "COMPLETED",
            "created_at": created_at,
            "completed_at": completed_at
        }
        client.publish(f"transaction/response/{transaction_id}", json.dumps(response_payload))
        print(f"[PUBLISHED] Transaction {transaction_id} completed -> transaction/response/{transaction_id}")

    except Exception as e:
        print(f"[ERROR] Failed to process transaction: {e}")

def on_disconnect(client, userdata, rc):
    """Callback saat koneksi terputus."""
    print("[WARNING] Disconnected from broker. Reconnecting in 5 seconds...")
    time.sleep(5)
    try:
        client.reconnect()
    except Exception as e:
        print(f"[ERROR] Reconnect failed: {e}")

# Set event handler
client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect

# Koneksi ke broker
print(f"[INFO] Connecting to MQTT broker at {MQTT_HOST}:{MQTT_PORT}...")
client.connect(MQTT_HOST, MQTT_PORT, 60)
client.loop_forever()
