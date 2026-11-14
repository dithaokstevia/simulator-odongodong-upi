import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import datetime

# ---------------------------------------------------------
# 1. KONFIGURASI DASHBOARD
# ---------------------------------------------------------
st.set_page_config(
    page_title="Simulator Parametrik Odong-Odong UPI",
    page_icon="🚌",
    layout="wide"
)

st.title("🚌 Simulator Parametrik Rute & Penjadwalan Odong-Odong UPI")
st.caption("Kelompok 6 - Proyek MSTR Kampus UPI Silihwangi 2026 (Presisi 9 Halte & Sesi Operasional Dinamis)")
st.markdown("---")

# ---------------------------------------------------------
# 2. SIDEBAR: PANEL KONTROL PARAMETER OPERASIONAL & SESI
# ---------------------------------------------------------
st.sidebar.header("⚙️ Panel Parameter Simulator")

# Parameter Kecepatan & Dwell Time
kecepatan_kmjam = st.sidebar.slider(
    "Kecepatan Rata-Rata Odong-Odong (km/jam):", 
    min_value=10, 
    max_value=25, 
    value=15, 
    step=1
)

dwell_time = st.sidebar.number_input(
    "Waktu Henti di Halte / Dwell Time (Menit):", 
    min_value=1, 
    max_value=10, 
    value=3, 
    step=1
)

jumlah_armada = 3
kapasitas_maks = 10

st.sidebar.markdown("---")
st.sidebar.header("🕒 Pengaturan Jam Operasional Sesi")

pilihan_sesi = st.sidebar.selectbox(
    "Pilih Sesi yang Dikelola:", 
    ["Sesi Pagi (Utama)", "Sesi Sore (Kepulangan)", "Sesi Kustom (Bebas)"]
)

if "Pagi" in pilihan_sesi:
    default_start = datetime.time(6, 30)
    default_end = datetime.time(8, 0)
elif "Sore" in pilihan_sesi:
    default_start = datetime.time(16, 0)
    default_end = datetime.time(16, 30)
else:
    default_start = datetime.time(10, 0)
    default_end = datetime.time(12, 0)

jam_mulai_sesi = st.sidebar.time_input("Jam Mulai Operasional Sesi:", default_start)
jam_selesai_sesi = st.sidebar.time_input("Jam Selesai Operasional Sesi:", default_end)

t_mulai_dt = datetime.datetime.combine(datetime.date.today(), jam_mulai_sesi)
t_selesai_dt = datetime.datetime.combine(datetime.date.today(), jam_selesai_sesi)

if t_selesai_dt < t_mulai_dt:
    durasi_sesi_menit = 0.0
else:
    durasi_sesi_menit = (t_selesai_dt - t_mulai_dt).total_seconds() / 60.0

st.sidebar.info("💡 **Petunjuk**: Ubah jam operasional atau jarak leg di bawah untuk memperbarui jadwal secara otomatis.")

# ---------------------------------------------------------
# 3. TABEL MATRIKS JARAK DINAMIS (9 LEG)
# ---------------------------------------------------------
st.subheader("1️⃣ Matriks Jarak Antar-Halte Tetap 9 Fakultas Utama (Dapat Diedit)")

leg_list = [
    "Leg 1: Halte 1 (FPTI Gerbang Bawah) -> Halte 2 (FIP Baru)",
    "Leg 2: Halte 2 (FIP Baru) -> Halte 3 (FPMIPA JICA)",
    "Leg 3: Halte 3 (FPMIPA JICA) -> Halte 4 (FPOK Utama)",
    "Leg 4: Halte 4 (FPOK Utama) -> Halte 5 (FK Kedokteran)",
    "Leg 5: Halte 5 (FK Kedokteran) -> Halte 6 (FPEB Utama)",
    "Leg 6: Halte 6 (FPEB Utama) -> Halte 7 (FPSD Utama)",
    "Leg 7: Halte 7 (FPSD Utama) -> Halte 8 (FPBS / ATM Center)",
    "Leg 8: Halte 8 (FPBS / ATM Center) -> Halte 9 (FPIPS Utama)",
    "Leg 9: Halte 9 (FPIPS Utama) -> Halte 1 (FPTI Gerbang Bawah)"
]

jarak_list_baru = [
    320,  # FPTI - FIP
    120,  # FIP - FPMIPA
    327,  # FPMIPA - FPOK
    120,  # FPOK - FK
    150,  # FK - FPEB
    130,  # FPEB - FPSD
    160,  # FPSD - FPBS
    230,  # FPBS - FPIPS
    180   # FPIPS - FPTI
]

data_jarak = {
    "Leg Rute Lingkar Kampus": leg_list,
    "Estimasi Jarak (Meter)": jarak_list_baru
}

df_jarak = pd.DataFrame(data_jarak)
df_edited = st.data_editor(df_jarak, num_rows="fixed", use_container_width=True, key="editor_jarak_clean")

# ---------------------------------------------------------
# 4. ENGINE KALKULASI MATEMATIKA PVRTP
# ---------------------------------------------------------
kecepatan_m_min = (kecepatan_kmjam * 1000) / 60.0
df_edited["Waktu Jalan (Menit)"] = (df_edited["Estimasi Jarak (Meter)"] / kecepatan_m_min).round(2)
df_edited["Total Waktu Leg (Menit)"] = (df_edited["Waktu Jalan (Menit)"] + dwell_time).round(2)

total_siklus_menit = df_edited["Total Waktu Leg (Menit)"].sum()
headway_menit = total_siklus_menit / jumlah_armada
waktu_tunggu_rata = headway_menit / 2.0
waktu_tunggu_maks = headway_menit

if total_siklus_menit > 0 and durasi_sesi_menit > 0:
    total_putaran_sesi = durasi_sesi_menit / total_siklus_menit
else:
    total_putaran_sesi = 0.0

st.markdown("### 📊 Hasil Perhitungan Parameter & Indikator Operasional Sesi")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Total 1 Siklus Putar", f"{total_siklus_menit:.1f} Menit")
with col2:
    st.metric("Interval Kedatangan (Headway)", f"{headway_menit:.1f} Menit")
with col3:
    st.metric("Rata-Rata Waktu Tunggu", f"{waktu_tunggu_rata:.1f} Menit")
with col4:
    st.metric("Total Durasi Sesi", f"{durasi_sesi_menit:.0f} Menit")
with col5:
    st.metric("Total Putaran Sesi", f"{total_putaran_sesi:.2f} Putaran")

st.markdown(f"ℹ️ **Kapasitas Armada**: Ditetapkan maksimal **{kapasitas_maks} Orang Penumpang** per odong-odong.")
st.markdown("---")

# ---------------------------------------------------------
# 5. TABEL JADWAL PRESISI WAKTU KEDATANGAN
# ---------------------------------------------------------
st.subheader("2️⃣ Tabel Jadwal Presisi Kedatangan di Setiap Halte (Timetable Dinamis Sesi)")

halte_names = [
    "Halte 1 (FPTI - Gerbang Bawah)",
    "Halte 2 (FIP Baru)",
    "Halte 3 (FPMIPA - JICA)",
    "Halte 4 (FPOK Utama)",
    "Halte 5 (FK Kedokteran)",
    "Halte 6 (FPEB Utama)",
    "Halte 7 (FPSD Utama)",
    "Halte 8 (FPBS / ATM Center)",
    "Halte 9 (FPIPS Utama)"
]

leg_durations = df_edited["Total Waktu Leg (Menit)"].tolist()

def build_timetable_sesi(start_halte_idx, start_dt, end_dt):
    rows = []
    num_haltes = len(halte_names)
    curr_dt = start_dt
    trip_count = 1
    
    while curr_dt <= end_dt:
        for step in range(num_haltes):
            h_idx = (start_halte_idx + step) % num_haltes
            h_name = halte_names[h_idx]
            
            if curr_dt <= end_dt:
                rows.append({
                    "Putaran / Trip": f"Trip {trip_count}",
                    "Nama Halte Singgah": h_name,
                    "Jam Kedatangan Presisi": curr_dt.strftime("%H.%M WIB")
                })
            else:
                break
            
            dur = leg_durations[h_idx]
            curr_dt += datetime.timedelta(minutes=dur)
            
        if curr_dt <= end_dt:
            origin_name = halte_names[start_halte_idx]
            rows.append({
                "Putaran / Trip": f"Trip {trip_count} (Selesai)",
                "Nama Halte Singgah": f"Kembali ke {origin_name}",
                "Jam Kedatangan Presisi": curr_dt.strftime("%H.%M WIB")
            })
        
        trip_count += 1
        if trip_count > 10:
            break
            
    return pd.DataFrame(rows)

tab1, tab2, tab3 = st.tabs([
    "🚌 Odong 1 (Start: Halte 1 FPTI)",
    "🚌 Odong 2 (Start: Halte 3 FPMIPA)",
    "🚌 Odong 3 (Start: Halte 6 FPEB)"
])

with tab1:
    st.markdown(f"**Jadwal Operasional Odong 1 ({jam_mulai_sesi.strftime('%H.%M')} - {jam_selesai_sesi.strftime('%H.%M')} WIB)**")
    df_o1 = build_timetable_sesi(0, t_mulai_dt, t_selesai_dt)
    st.dataframe(df_o1, use_container_width=True, hide_index=True)

with tab2:
    st.markdown(f"**Jadwal Operasional Odong 2 ({jam_mulai_sesi.strftime('%H.%M')} - {jam_selesai_sesi.strftime('%H.%M')} WIB)**")
    df_o2 = build_timetable_sesi(2, t_mulai_dt, t_selesai_dt)
    st.dataframe(df_o2, use_container_width=True, hide_index=True)

with tab3:
    st.markdown(f"**Jadwal Operasional Odong 3 ({jam_mulai_sesi.strftime('%H.%M')} - {jam_selesai_sesi.strftime('%H.%M')} WIB)**")
    df_o3 = build_timetable_sesi(5, t_mulai_dt, t_selesai_dt)
    st.dataframe(df_o3, use_container_width=True, hide_index=True)

# ---------------------------------------------------------
# 6. PETA INTERAKTIF (TANPA GARIS) & SIMULASI LIVE
# ---------------------------------------------------------
st.markdown("---")
st.subheader("3️⃣ Visualisasi Peta Titik 9 Halte & Simulasi Pergerakan Odong-Odong")
st.write("Peta di bawah **hanya menampilkan titik penanda halte (tanpa garis)**. Gunakan slider simulasi di bawah untuk melihat posisi armada berjalan secara live:")

data_koordinat_awal = {
    "Nama Halte": [
        "Halte 1: FPTI (Gedung A-D Gerbang Bawah)",
        "Halte 2: FIP Baru (Gedung FIP Baru)",
        "Halte 3: FPMIPA (Gedung JICA FPMIPA)",
        "Halte 4: FPOK (Gedung FPOK Utama)",
        "Halte 5: FK (Gedung Fakultas Kedokteran)",
        "Halte 6: FPEB (Gedung FPEB Utama)",
        "Halte 7: FPSD (Gedung FPSD Utama)",
        "Halte 8: FPBS (Gedung FPBS / ATM Center)",
        "Halte 9: FPIPS (Gedung FPIPS Utama)"
    ],
    "Latitude": [-6.8637, -6.8617, -6.8620, -6.8610, -6.8608, -6.8603, -6.8602, -6.8606, -6.8613],
    "Longitude": [107.5925, 107.5911, 107.5904, 107.5900, 107.5912, 107.5925, 107.5933, 107.5940, 107.5927],
    "Warna Icon": ["blue", "green", "red", "darkred", "cadetblue", "orange", "darkgreen", "darkblue", "purple"]
}

df_coords = pd.DataFrame(data_koordinat_awal)
df_coords_edited = st.data_editor(df_coords, num_rows="fixed", use_container_width=True, key="editor_coords_clean")

menit_simulasi = st.slider(
    "🎬 **Slider Simulasi Waktu Pergerakan (Menit Sejak Jam Mulai Sesi)**:", 
    min_value=0, 
    max_value=max(int(durasi_sesi_menit), 30), 
    value=0, 
    step=1
)

tile_url = "https://tile.openstreetmap.org/{z}/{x}/{y}.png"

m = folium.Map(
    location=[-6.8610, 107.5925], 
    zoom_start=17, 
    tiles=tile_url,
    attr="&copy; OpenStreetMap contributors"
)

folium.LatLngPopup().add_to(m)

for index, row in df_coords_edited.iterrows():
    pos = [float(row["Latitude"]), float(row["Longitude"])]
    folium.Marker(
        location=pos,
        popup=row["Nama Halte"],
        tooltip=row["Nama Halte"],
        icon=folium.Icon(color=row["Warna Icon"], icon="bus", prefix="fa")
    ).add_to(m)

if total_siklus_menit > 0:
    h_idx1 = int((menit_simulasi / total_siklus_menit * 9)) % 9
    pos1 = [df_coords_edited.iloc[h_idx1]["Latitude"], df_coords_edited.iloc[h_idx1]["Longitude"]]
    folium.Marker(
        location=pos1,
        popup=f"🚌 Odong 1 (Posisi Menit Ke-{menit_simulasi})",
        tooltip=f"Odong 1 di {df_coords_edited.iloc[h_idx1]['Nama Halte']}",
        icon=folium.Icon(color="red", icon="play", prefix="fa")
    ).add_to(m)

st_folium(m, width=1100, height=550)
