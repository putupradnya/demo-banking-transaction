import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
import altair as alt

# Koneksi ke database SQLite
DB_FILE = "transactions-db2-log.db"

def load_data():
    """Load transaksi dari database."""
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM transactions", conn)
    conn.close()
    return df

# Konfigurasi layout
st.set_page_config(page_title="Real-Time Transaction Dashboard", layout="wide")

# Auto Refresh Tiap 1 Detik
st_autorefresh(interval=2000, key="data_refresh")  # Refresh tiap 1 detik

st.title("Transaction Dashboard Monitoring")

# Load data terbaru
df = load_data()

# **1️⃣ Total Transaksi**
total_transaksi = len(df)
completed_transaksi = df[df["status"] == "COMPLETED"].shape[0]
pending_transaksi = df[df["status"] == "PENDING"].shape[0]

st.subheader("Summary")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Transaksi", total_transaksi)
col2.metric("Completed", completed_transaksi)
col3.metric("Pending", pending_transaksi)

# **2️⃣ Rata-rata Waktu Penyelesaian**
if completed_transaksi > 0:
    df_completed = df[df["status"] == "COMPLETED"].copy()
    df_completed["created_at"] = pd.to_datetime(df_completed["created_at"])
    df_completed["completed_at"] = pd.to_datetime(df_completed["completed_at"])
    df_completed["processing_time"] = (df_completed["completed_at"] - df_completed["created_at"]).dt.total_seconds()

    avg_processing_time = df_completed["processing_time"].mean()
    # st.metric("⏳ Rata-rata Waktu Penyelesaian", f"{avg_processing_time:.2f} detik")
    col4.metric("Avg Transaction Time (Sec)", f"{avg_processing_time:.2f}")

else:
    # st.metric("⏳ Rata-rata Waktu Penyelesaian", "N/A")
    col4.metric("Avg Transaction Time (Sec)", f"N/A")


st.subheader("Transaksi per Merchant & Receiver")

# Ubah data jadi long format biar bisa di-stack
# Hitung jumlah transaksi per merchant (source) dan receiver (destination)
merchant_counts = df.groupby("source").size().reset_index(name="count")
merchant_counts["type"] = "Merchant (Sender)"

receiver_counts = df.groupby("destination").size().reset_index(name="count")
receiver_counts["type"] = "Receiver"

# Gabungkan data merchant dan receiver
combined_counts = pd.concat([
    merchant_counts.rename(columns={"source": "name"}),
    receiver_counts.rename(columns={"destination": "name"})
])

# Buat stacked bar chart pakai Altair
chart = alt.Chart(combined_counts).mark_bar().encode(
    x=alt.X("name:N", title="Merchant / Receiver"),
    y=alt.Y("count:Q", title="Jumlah Transaksi"),
    color=alt.Color("type:N", title="Kategori", scale=alt.Scale(domain=["Merchant (Sender)", "Receiver"], range=["blue", "orange"]))
).properties(
    width=600,
    height=400
)

st.altair_chart(chart, use_container_width=True)


# **5️⃣ Transaksi Per Menit (Real-Time)**
st.subheader("Transaksi per Menit")
df["created_at"] = pd.to_datetime(df["created_at"])
df["minute"] = df["created_at"].dt.strftime("%H:%M")
transactions_per_minute = df.groupby("minute").size()
st.line_chart(transactions_per_minute)
