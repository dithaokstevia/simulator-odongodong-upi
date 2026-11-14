import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import datetime
import streamlit.components.v1 as components

# ---------------------------------------------------------
# 1. KONFIGURASI DASHBOARD
# ---------------------------------------------------------
st.set_page_config(
    page_title="Simulator Parametrik Odong-Odong UPI",
    page_icon="🚌",
    layout="wide"
)

st.title("🚌 Simulator Parametrik Rute & Penjadwalan Odong-Odong UPI")
st.caption("Kelompok 6 - Ditha Okstevia, Eisha Karima Fidareini, Nailah Amani Nuryaman, Nesa Dwi Rizqi Marsha Reneta, Wafa Nidaul Hasanah - Proyek MSTR Kampus UPI Silihwangi 2026 (Presisi 9 Halte & Sesi Operasional Dinamis)")
st.markdown("---")

# Data Nama 9 Halte Singkat Presisi
list_halte = ["FPTI", "FIP", "FPMIPA", "FPOK", "FK", "FPEB", "FPSD", "FPBS", "FPIPS"]

# ---------------------------------------------------------
# 2. SIDEBAR: PANEL KONTROL PARAMETER OPERASIONAL & SESI
# ---------------------------------------------------------
st.sidebar.header("⚙️ Panel Parameter Simulator")

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

# ---------------------------------------------------------
# 3. PANEL SUPIR: INPUT POSISI LEG, KURSI TERISI & HALTE TURUN WITH VALIDATION
# ---------------------------------------------------------
st.sidebar.markdown("---")
st.sidebar.header("👨‍✈️ Panel Supir: Input Real-Time")

# Input Supir Odong 1
st.sidebar.subheader("🚌 Odong 1 (Start: FPTI)")
pilihan_leg_o1 = st.sidebar.selectbox(
    "Posisi Leg Jalan Odong 1 Saat Ini:", 
    options=list(range(9)), 
    index=0,
    format_func=lambda x: f"Leg {x+1}: {list_halte[x]} -> {list_halte[(x+1)%9]}",
    key="sb_leg_o1"
)
terisi_o1 = st.sidebar.number_input("Kursi Terisi Saat Ini (Odong 1):", 0, kapasitas_maks, 10, key="t_o1")
turun_o1 = {}
with st.sidebar.expander("📍 Rincian Halte Turun Penumpang (Odong 1)"):
    for idx, h_short in enumerate(list_halte):
        def_val = 5 if h_short == "FPMIPA" else (5 if h_short == "FPEB" else 0)
        turun_o1[h_short] = st.number_input(f"Turun di {h_short}:", 0, terisi_o1, def_val, key=f"turun_o1_{idx}")

total_turun_o1 = sum(turun_o1.values())
if total_turun_o1 != terisi_o1:
    st.sidebar.warning(f"⚠️ Total turun Odong 1 ({total_turun_o1} org) != Kursi terisi ({terisi_o1} org)")

# Input Supir Odong 2
st.sidebar.subheader("🚌 Odong 2 (Start: FPMIPA)")
pilihan_leg_o2 = st.sidebar.selectbox(
    "Posisi Leg Jalan Odong 2 Saat Ini:", 
    options=list(range(9)), 
    index=2,
    format_func=lambda x: f"Leg {x+1}: {list_halte[x]} -> {list_halte[(x+1)%9]}",
    key="sb_leg_o2"
)
terisi_o2 = st.sidebar.number_input("Kursi Terisi Saat Ini (Odong 2):", 0, kapasitas_maks, 8, key="t_o2")
turun_o2 = {}
with st.sidebar.expander("📍 Rincian Halte Turun Penumpang (Odong 2)"):
    for idx, h_short in enumerate(list_halte):
        def_val = 8 if h_short == "FK" else 0
        turun_o2[h_short] = st.number_input(f"Turun di {h_short}:", 0, terisi_o2, def_val, key=f"turun_o2_{idx}")

total_turun_o2 = sum(turun_o2.values())
if total_turun_o2 != terisi_o2:
    st.sidebar.warning(f"⚠️ Total turun Odong 2 ({total_turun_o2} org) != Kursi terisi ({terisi_o2} org)")

# Input Supir Odong 3
st.sidebar.subheader("🚌 Odong 3 (Start: FPEB)")
pilihan_leg_o3 = st.sidebar.selectbox(
    "Posisi Leg Jalan Odong 3 Saat Ini:", 
    options=list(range(9)), 
    index=5,
    format_func=lambda x: f"Leg {x+1}: {list_halte[x]} -> {list_halte[(x+1)%9]}",
    key="sb_leg_o3"
)
terisi_o3 = st.sidebar.number_input("Kursi Terisi Saat Ini (Odong 3):", 0, kapasitas_maks, 4, key="t_o3")
turun_o3 = {}
with st.sidebar.expander("📍 Rincian Halte Turun Penumpang (Odong 3)"):
    for idx, h_short in enumerate(list_halte):
        def_val = 4 if h_short == "FPTI" else 0
        turun_o3[h_short] = st.number_input(f"Turun di {h_short}:", 0, terisi_o3, def_val, key=f"turun_o3_{idx}")

total_turun_o3 = sum(turun_o3.values())
if total_turun_o3 != terisi_o3:
    st.sidebar.warning(f"⚠️ Total turun Odong 3 ({total_turun_o3} org) != Kursi terisi ({terisi_o3} org)")

sisa_o1 = kapasitas_maks - terisi_o1
sisa_o2 = kapasitas_maks - terisi_o2
sisa_o3 = kapasitas_maks - terisi_o3

# ---------------------------------------------------------
# 4. TABEL MATRIKS JARAK DINAMIS (9 LEG)
# ---------------------------------------------------------
st.subheader("1️⃣ Matriks Jarak Antar-Halte Tetap 9 Fakultas Utama (Dapat Diedit)")

leg_list = [f"Leg {i+1}: {list_halte[i]} -> {list_halte[(i+1)%9]}" for i in range(9)]
jarak_list_baru = [320, 120, 327, 120, 150, 130, 160, 230, 180]

data_jarak = {
    "Leg Rute Lingkar Kampus": leg_list,
    "Estimasi Jarak (Meter)": jarak_list_baru
}

df_jarak = pd.DataFrame(data_jarak)
df_edited = st.data_editor(df_jarak, num_rows="fixed", use_container_width=True, key="editor_jarak_clean")

# ---------------------------------------------------------
# 5. ENGINE KALKULASI MATEMATIKA PVRTP
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

# ---------------------------------------------------------
# 6. STATUS KETERISIAN KURSI & RINCIAN TURUN PER HALTE (DENGAN VALIDASI)
# ---------------------------------------------------------
st.markdown("### 💺 Status Keterisian Kursi & Rincian Penumpang Turun per Halte")
m_col1, m_col2, m_col3 = st.columns(3)

with m_col1:
    st.subheader("🚌 Odong 1 (Start: FPTI)")
    st.metric("Kursi Terisi", f"{terisi_o1} / {kapasitas_maks} Orang", delta=f"Sisa {sisa_o1} Kursi Langsung Kosong")
    st.progress(terisi_o1 / kapasitas_maks)
    if terisi_o1 >= kapasitas_maks:
        st.error("⚠️ STATUS: KABIN PENUH SAAT INI")
    else:
        st.success(f"✅ STATUS: TERSEDIA {sisa_o1} KURSI LANGSUNG")
    
    st.markdown("**📍 Rincian Penumpang Akan Turun di Halte:**")
    if total_turun_o1 != terisi_o1:
        st.warning(f"⚠️ Total input turun ({total_turun_o1} org) BELUM SAMA dengan Kursi Terisi ({terisi_o1} org)! Silakan supir sesuaikan rincian.")
    else:
        df_t1 = pd.DataFrame([{"Halte Tujuan": k, "Jumlah Turun (Orang)": v} for k, v in turun_o1.items() if v > 0])
        if not df_t1.empty:
            st.dataframe(df_t1, use_container_width=True, hide_index=True)
        else:
            st.caption("Belum ada rincian halte turun diinput supir.")

with m_col2:
    st.subheader("🚌 Odong 2 (Start: FPMIPA)")
    st.metric("Kursi Terisi", f"{terisi_o2} / {kapasitas_maks} Orang", delta=f"Sisa {sisa_o2} Kursi Langsung Kosong")
    st.progress(terisi_o2 / kapasitas_maks)
    if terisi_o2 >= kapasitas_maks:
        st.error("⚠️ STATUS: KABIN PENUH SAAT INI")
    else:
        st.success(f"✅ STATUS: TERSEDIA {sisa_o2} KURSI LANGSUNG")
    
    st.markdown("**📍 Rincian Penumpang Akan Turun di Halte:**")
    if total_turun_o2 != terisi_o2:
        st.warning(f"⚠️ Total input turun ({total_turun_o2} org) BELUM SAMA dengan Kursi Terisi ({terisi_o2} org)! Silakan supir sesuaikan rincian.")
    else:
        df_t2 = pd.DataFrame([{"Halte Tujuan": k, "Jumlah Turun (Orang)": v} for k, v in turun_o2.items() if v > 0])
        if not df_t2.empty:
            st.dataframe(df_t2, use_container_width=True, hide_index=True)
        else:
            st.caption("Belum ada rincian halte turun diinput supir.")

with m_col3:
    st.subheader("🚌 Odong 3 (Start: FPEB)")
    st.metric("Kursi Terisi", f"{terisi_o3} / {kapasitas_maks} Orang", delta=f"Sisa {sisa_o3} Kursi Langsung Kosong")
    st.progress(terisi_o3 / kapasitas_maks)
    if terisi_o3 >= kapasitas_maks:
        st.error("⚠️ STATUS: KABIN PENUH SAAT INI")
    else:
        st.success(f"✅ STATUS: TERSEDIA {sisa_o3} KURSI LANGSUNG")
    
    st.markdown("**📍 Rincian Penumpang Akan Turun di Halte:**")
    if total_turun_o3 != terisi_o3:
        st.warning(f"⚠️ Total input turun ({total_turun_o3} org) BELUM SAMA dengan Kursi Terisi ({terisi_o3} org)! Silakan supir sesuaikan rincian.")
    else:
        df_t3 = pd.DataFrame([{"Halte Tujuan": k, "Jumlah Turun (Orang)": v} for k, v in turun_o3.items() if v > 0])
        if not df_t3.empty:
            st.dataframe(df_t3, use_container_width=True, hide_index=True)
        else:
            st.caption("Belum ada rincian halte turun diinput supir.")

st.markdown("---")

# ---------------------------------------------------------
# 7. ANIMASI PERGERAKAN 3 TITIK (MENGIKUTI INPUT SUPIR IN SIDEBAR)
# ---------------------------------------------------------
st.subheader("Status Pergerakan 3 Armada Odong-Odong")
st.write("Tampilan animasi di bawah **secara otomatis bergerak sesuai posisi Leg Perjalanan yang diinput supir di Panel Sidebar**:")

def render_anim_odong_direct(pilihan_leg_anim, border_color):
    nama_asal = list_halte[pilihan_leg_anim]
    nama_tujuan = list_halte[(pilihan_leg_anim + 1) % 9]
    jarak_leg = df_edited.iloc[pilihan_leg_anim]["Estimasi Jarak (Meter)"]
    waktu_jalan_leg = df_edited.iloc[pilihan_leg_anim]["Waktu Jalan (Menit)"]

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
    @keyframes moveAndShake {{
        0% {{ left: 2%; transform: translateY(0px) rotate(0deg); }}
        25% {{ transform: translateY(-4px) rotate(-3deg); }}
        50% {{ transform: translateY(3px) rotate(3deg); }}
        75% {{ transform: translateY(-3px) rotate(-2deg); }}
        100% {{ left: 88%; transform: translateY(0px) rotate(0deg); }}
    }}
    body {{ margin: 0; padding: 0; background: transparent; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }}
    .anim-container {{ background: linear-gradient(135deg, #1e293b, #0f172a); border-radius: 16px; padding: 20px; color: white; border: 2px solid {border_color}; }}
    .nodes-wrapper {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }}
    .node-box {{ background: #334155; padding: 10px 16px; border-radius: 12px; border: 2px solid {border_color}; font-weight: bold; font-size: 14px; width: 38%; text-align: center; }}
    .track-line {{ position: relative; height: 12px; background: #475569; border-radius: 6px; margin: 35px 10px 15px 10px; border: 1px dashed #94a3b8; }}
    .car-icon {{ position: absolute; top: -26px; font-size: 34px; animation: moveAndShake 3.5s infinite linear; filter: drop-shadow(0px 4px 6px rgba(0,0,0,0.4)); }}
    .info-badge {{ text-align: center; background: #0284c7; padding: 6px 14px; border-radius: 20px; font-size: 13px; font-weight: 600; display: inline-block; }}
    </style>
    </head>
    <body>
    <div class="anim-container">
        <div class="nodes-wrapper">
            <div class="node-box">📍 TITIK ASAL<br><span style="color: #38bdf8; font-size: 15px;">Halte {nama_asal}</span></div>
            <div style="text-align: center;"><span class="info-badge">📏 {jarak_leg} Meter | ⏱️ {waktu_jalan_leg} Menit</span></div>
            <div class="node-box">🏁 TITIK TUJUAN<br><span style="color: #4ade80; font-size: 15px;">Halte {nama_tujuan}</span></div>
        </div>
        <div class="track-line"><div class="car-icon">🚌</div></div>
    </div>
    </body>
    </html>
    """
    components.html(html_code, height=210)

anim_tab1, anim_tab2, anim_tab3 = st.tabs([
    "🚌 Animasi Odong 1 (Start: FPTI)",
    "🚌 Animasi Odong 2 (Start: FPMIPA)",
    "🚌 Animasi Odong 3 (Start: FPEB)"
])

with anim_tab1:
    st.info(f"📍 Leg Perjalanan Odong 1 Saat Ini (Input Supir): **Leg {pilihan_leg_o1+1}: {list_halte[pilihan_leg_o1]} ➔ {list_halte[(pilihan_leg_o1+1)%9]}**")
    render_anim_odong_direct(pilihan_leg_o1, "#38bdf8")

with anim_tab2:
    st.info(f"📍 Leg Perjalanan Odong 2 Saat Ini (Input Supir): **Leg {pilihan_leg_o2+1}: {list_halte[pilihan_leg_o2]} ➔ {list_halte[(pilihan_leg_o2+1)%9]}**")
    render_anim_odong_direct(pilihan_leg_o2, "#f59e0b")

with anim_tab3:
    st.info(f"📍 Leg Perjalanan Odong 3 Saat Ini (Input Supir): **Leg {pilihan_leg_o3+1}: {list_halte[pilihan_leg_o3]} ➔ {list_halte[(pilihan_leg_o3+1)%9]}**")
    render_anim_odong_direct(pilihan_leg_o3, "#10b981")

st.markdown("---")

# ---------------------------------------------------------
# 8. TABEL JADWAL PRESISI WAKTU KEDATANGAN
# ---------------------------------------------------------
st.subheader("3️⃣ Tabel Jadwal Presisi Kedatangan di Setiap Halte (Timetable Dinamis Sesi)")

leg_durations = df_edited["Total Waktu Leg (Menit)"].tolist()

def build_timetable_sesi(start_halte_idx, start_dt, end_dt):
    rows = []
    num_haltes = len(list_halte)
    curr_dt = start_dt
    trip_count = 1
    
    while curr_dt <= end_dt:
        for step in range(num_haltes):
            h_idx = (start_halte_idx + step) % num_haltes
            h_name = f"Halte {list_halte[h_idx]}"
            
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
            origin_name = f"Halte {list_halte[start_halte_idx]}"
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
    "🚌 Odong 1 (Start: Halte FPTI)",
    "🚌 Odong 2 (Start: Halte FPMIPA)",
    "🚌 Odong 3 (Start: Halte FPEB)"
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
# 9. PETA INTERAKTIF 9 HALTE (TANPA GARIS RUTE)
# ---------------------------------------------------------
st.markdown("---")
st.subheader("4️⃣ Visualisasi Peta Titik Penanda 9 Halte Tetap Kampus UPI")
st.write("Peta di bawah **hanya menampilkan titik penanda 9 halte (tanpa garis)**:")

data_koordinat_awal = {
    "Nama Halte": [f"Halte {h}" for h in list_halte],
    "Latitude": [-6.8637, -6.8617, -6.8620, -6.8610, -6.8608, -6.8603, -6.8602, -6.8606, -6.8613],
    "Longitude": [107.5925, 107.5911, 107.5904, 107.5900, 107.5912, 107.5925, 107.5933, 107.5940, 107.5927],
    "Warna Icon": ["blue", "green", "red", "darkred", "cadetblue", "orange", "darkgreen", "darkblue", "purple"]
}

df_coords = pd.DataFrame(data_koordinat_awal)
df_coords_edited = st.data_editor(df_coords, num_rows="fixed", use_container_width=True, key="editor_coords_clean")

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

st_folium(m, width=1100, height=550)
