# Realtime Transaction Processing & Dashboard with Streamlit

## 📝 Deskripsi

Project ini adalah sistem **event-driven transaction processing** dengan Solace Pubsub+ yang terdiri dari beberapa service untuk menangani transaksi merchant dan sistem pembayaran seperti Bifast(Simplifikasi). Data transaksi disimpan dalam SQLite dan divisualisasikan dalam dashboard real-time berbasis **Streamlit**.

---

## 📌 Fitur Utama

✅ **Merchant Service** → Generate transaksi baru dari merchant.
✅ **Bifast Service** → Memproses transaksi merchant ke status **COMPLETED**.
✅ **Logging Service** → Mencatat semua transaksi dalam database SQLite.
✅ **Dashboard Real-time** → Menampilkan metrik transaksi dengan **auto-refresh setiap 1 detik**.
✅ **Stacked bar chart** untuk perbandingan transaksi **merchant & receiver**.
✅ **Time-series chart** untuk melihat tren transaksi dari waktu ke waktu.

---
## ⚙️ Setup Solace Pubsub+
Setup atau jalankan Solace via docker melalui step berikut [ini](https://solace.com/products/event-broker/software/getting-started/)

## ⚙️ Instalasi & Menjalankan Project

### 1️⃣ Clone repository

```bash
git clone https://github.com/your-repo/realtime-transaction-dashboard.git
cd realtime-transaction-dashboard
```

### 2️⃣ Buat virtual environment (Python 3.11)

```bash
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate  # Windows
```

### 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Jalankan setiap service di terminal yang berbeda

- **Merchant Service:**
  ```bash
  python merchant_service.py
  ```
- **Bifast Service:**
  ```bash
  python bifast_service.py
  ```
- **Logging Service:**
  ```bash
  python logging_service.py
  ```
- **Dashboard:**
  ```bash
  streamlit run dashboard.py
  ```

---

## 📂 Struktur Project

```
📁 realtime-transaction-dashboard
│── 📄 merchant_service.py   # Generate transaksi baru
│── 📄 bifast_service.py     # Memproses transaksi ke COMPLETED
│── 📄 logging_service.py    # Mencatat transaksi ke SQLite
│── 📄 dashboard.py          # Streamlit dashboard real-time
│── 📄 database.db           # SQLite database file
│── 📄 requirements.txt      # List of dependencies
│── 📄 README.md             # Dokumentasi proyek
```

---

## 📊 Penjelasan Setiap Service

### 1️⃣ Merchant Service (`merchant_service.py`)

- Generate transaksi baru dengan status **PENDING**.
- Setiap transaksi memiliki **transaction_id, sender, receiver, timestamp**.
- Data ditulis ke SQLite melalui Logging Service.

### 2️⃣ Bifast Service (`bifast_service.py`)

- Mengecek transaksi **PENDING** dan mengubahnya ke **COMPLETED** setelah 3-5 detik.
- Menambahkan timestamp **completed_at** ke transaksi yang selesai.
- Data ditulis ulang ke SQLite melalui Logging Service.

### 3️⃣ Logging Service (`logging_service.py`)

- Bertanggung jawab untuk mencatat semua transaksi ke SQLite.
- Tidak melakukan **update**, tetapi menulis **record baru** untuk setiap perubahan status transaksi.

### 4️⃣ Dashboard Real-time (`dashboard.py`)

- **Auto-refresh setiap 1 detik** untuk update data real-time.
- **Jumlah total transaksi & status transaksi (PENDING, COMPLETED).**
- **Stacked bar chart** untuk perbandingan transaksi **Merchant & Receiver**.
- **Time-series chart** untuk melihat tren transaksi.

---

## 📦 Dependencies

- `streamlit`
- `pandas`
- `sqlite3`
- `altair`
- `time`
- `random`
<<<<<<< HEAD
- `paho-mqtt`
=======
- paho-mqtt
>>>>>>> be98b05 (add .env for local development for flexibility setting credential)

Pastikan semua dependencies sudah terinstall sebelum menjalankan project.

---

## 📢 Kontribusi

Jika ingin berkontribusi, silakan fork repo ini dan buat pull request! 🚀
