import os
import json
import time
import random
import paho.mqtt.client as mqtt
import sqlite3
from datetime import datetime
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

# Buat tabel transaksi kalau belum ada
cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        transaction_id TEXT,
        amount INTEGER,
        source TEXT,
        destination TEXT,
        status TEXT,
        created_at TEXT,
        completed_at TEXT
    )
""")
conn.commit()

# MQTT Client setup
client = mqtt.Client()
client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

def generate_transaction_id():
    """Bikin ID transaksi random."""
    return "TX" + str(random.randint(10000, 99999))

def send_transaction():
    """Kirim transaksi random tiap beberapa detik."""
    while True:
        transaction_id = generate_transaction_id()
        amount = random.randint(10000, 1000000)
        source = random.choice(["BNI", "Mandiri", "BCA", "BRI", "CIMB", "HiBank"])
        destination = random.choice(["BNI", "Mandiri", "BCA", "BRI", "CIMB", "HiBank"])
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Simpan transaksi dengan status PENDING
        cursor.execute("""
            INSERT INTO transactions (transaction_id, amount, source, destination, status, created_at, completed_at)
            VALUES (?, ?, ?, ?, ?, ?, NULL)
        """, (transaction_id, amount, source, destination, "PENDING", created_at))
        conn.commit()
        
        print(f"[LOG] Transaction {transaction_id} created with status PENDING")

        # Publish ke Bifast dengan topic routing yang lebih terstruktur
        topic = f"banking/{source}/{destination}/created/{transaction_id}"
        payload = {
            "transaction_id": transaction_id,
            "amount": amount,
            "source": source,
            "destination": destination,
            "created_at": created_at
        }
        client.publish(topic, json.dumps(payload))
        print(f"[PUBLISHED] {transaction_id} sent to {topic}")

        time.sleep(random.randint(2, 5) / 25)  # Random delay biar kayak transaksi real

# Koneksi ke broker
try:
    print(f"[INFO] Connecting to MQTT broker at {MQTT_HOST}:{MQTT_PORT}...")
    client.connect(MQTT_HOST, MQTT_PORT, 60)
    client.loop_start()  # Biar ga blocking
    send_transaction()
except Exception as e:
    print(f"[ERROR] Connection failed: {e}")
    exit(1)
