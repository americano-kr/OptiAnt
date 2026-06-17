# ==========================================
# PERSIAPAN ENVIRONMENT & LIBRARY
# ==========================================
# !pip install folium geopy requests

import numpy as np
import folium
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from geopy.distance import geodesic
import requests

# ==========================================
# BAGIAN 1: PERSIAPAN DATA LOKASI
# ==========================================
lokasi = {
    "Depot (PENS/ITS)": (-7.2756, 112.7939),
    "A (Galaxy Mall)":  (-7.2756, 112.7820),
    "B (Klampis)":      (-7.2872, 112.7803),
    "C (Semolowaru)":   (-7.3021, 112.7801),
    "D (Bratang)":      (-7.2965, 112.7602),
    "E (Kertajaya)":    (-7.2831, 112.7634),
    "F (Dharmawangsa)": (-7.2705, 112.7565),
    "G (Mulyosari)":    (-7.2562, 112.7983),
    "H (Kenjeran)":     (-7.2471, 112.7805),
    "I (Pacarkeling)":  (-7.2589, 112.7551),
    "J (Ngagel)":       (-7.2901, 112.7431)
}

nama_lokasi = list(lokasi.keys())
koordinat   = list(lokasi.values())
jml_titik   = len(lokasi)

# Kalkulasi Matriks Jarak Geodesic
matriks_jarak = np.zeros((jml_titik, jml_titik))
for i in range(jml_titik):
    for j in range(jml_titik):
        if i != j:
            matriks_jarak[i][j] = geodesic(koordinat[i], koordinat[j]).kilometers

print(f"✅ Menggunakan {jml_titik} lokasi dengan matriks jarak geodesic.\n")

# ==========================================
# BAGIAN 1B: KONFIGURASI JALUR MACET
# ==========================================
# Tandai pasangan (i, j) yang macet — indeks sesuai urutan nama_lokasi di atas:
#   0=Depot, 1=A, 2=B, 3=C, 4=D, 5=E, 6=F, 7=G, 8=H, 9=I, 10=J
#
# Contoh: jalur dari A(1) ke B(2) dan dari Depot(0) ke G(7) dianggap macet.
# Ubah daftar di bawah sesuai kondisi lapangan.

JALUR_MACET = [
    (1, 2),   # A (Galaxy Mall) → B (Klampis)
    (0, 7),   # Depot           → G (Mulyosari)
]

PENALTI_MACET = 4.0   # visibilitas jalur macet dibagi nilai ini

def is_macet(i, j):
    """Cek apakah jalur i→j (atau j→i) termasuk macet."""
    return (i, j) in JALUR_MACET or (j, i) in JALUR_MACET

print("🚦 Jalur yang ditandai MACET:")
for (a, b) in JALUR_MACET:
    print(f"   {nama_lokasi[a]}  ↔  {nama_lokasi[b]}")
print(f"   Penalti visibilitas: ÷{PENALTI_MACET}\n")

# ==========================================
# BAGIAN 2: ALGORITMA ANT COLONY OPTIMIZATION
# ==========================================
jml_semut  = 20
iterasi    = 50
alpha      = 1.0   # bobot feromon
beta       = 2.0   # bobot visibilitas
penguapan  = 0.5

def hitung_visibilitas(i, j, dengan_penalti=True):
    """
    η(i,j) = 1 / jarak(i,j)
    Jika jalur macet dan dengan_penalti=True → η dibagi PENALTI_MACET
    """
    if matriks_jarak[i][j] == 0:
        return 0.0
    eta = 1.0 / matriks_jarak[i][j]
    if dengan_penalti and is_macet(i, j):
        eta /= PENALTI_MACET
    return eta

def hitung_probabilitas(posisi, dikunjungi, feromon, dengan_penalti=True):
    """
    Rumus probabilitas ACO:
        P(i→j) = [τ(i,j)^α × η(i,j)^β] / Σ [τ(i,s)^α × η(i,s)^β]
    Kembalikan array probabilitas untuk semua j.
    """
    p = np.zeros(jml_titik)
    for j in range(jml_titik):
        if j not in dikunjungi:
            eta = hitung_visibilitas(posisi, j, dengan_penalti)
            p[j] = (feromon[posisi][j] ** alpha) * (eta ** beta)
    total = p.sum()
    if total > 0:
        p /= total
    return p

def jalankan_aco(dengan_penalti=True, label=""):
    """
    Jalankan satu sesi ACO.
    dengan_penalti=True  → jalur macet dihukum (pakai penalti visibilitas)
    dengan_penalti=False → abaikan macet (skenario normal/pembanding)
    """
    feromon = np.ones((jml_titik, jml_titik))
    rute_terbaik  = None
    jarak_terpendek = float('inf')
    riwayat = []

    # Simpan contoh tabel probabilitas dari depot pada iterasi pertama
    contoh_prob_iterasi1 = None

    for it in range(iterasi):
        semua_rute, semua_jarak = [], []

        for _ in range(jml_semut):
            rute = [0]
            dikunjungi = {0}

            while len(rute) < jml_titik:
                pos = rute[-1]
                p   = hitung_probabilitas(pos, dikunjungi, feromon, dengan_penalti)
                total = p.sum()

                if total == 0:
                    sisa = list(set(range(jml_titik)) - dikunjungi)
                    pilihan = np.random.choice(sisa)
                else:
                    pilihan = np.random.choice(range(jml_titik), p=p)

                rute.append(pilihan)
                dikunjungi.add(pilihan)

            rute.append(0)
            total_j = sum(matriks_jarak[rute[k]][rute[k+1]] for k in range(jml_titik))
            semua_rute.append(rute)
            semua_jarak.append(total_j)

            if total_j < jarak_terpendek:
                jarak_terpendek = total_j
                rute_terbaik = rute.copy()

        # Simpan tabel probabilitas dari Depot (iterasi pertama)
        if it == 0 and contoh_prob_iterasi1 is None:
            contoh_prob_iterasi1 = []
            for j in range(1, jml_titik):
                eta  = hitung_visibilitas(0, j, dengan_penalti)
                tau  = feromon[0][j]
                skor = (tau ** alpha) * (eta ** beta)
                contoh_prob_iterasi1.append({
                    "j":    j,
                    "nama": nama_lokasi[j],
                    "dist": matriks_jarak[0][j],
                    "tau":  tau,
                    "eta":  eta,
                    "skor": skor,
                    "macet": dengan_penalti and is_macet(0, j)
                })
            total_skor = sum(d["skor"] for d in contoh_prob_iterasi1)
            for d in contoh_prob_iterasi1:
                d["prob"] = d["skor"] / total_skor if total_skor > 0 else 0

        riwayat.append(jarak_terpendek)

        # Update feromon
        feromon *= (1 - penguapan)
        for idx_s, rute in enumerate(semua_rute):
            delta = 1.0 / semua_jarak[idx_s]
            for k in range(jml_titik):
                feromon[rute[k]][rute[k+1]] += delta

    return rute_terbaik, jarak_terpendek, riwayat, feromon, contoh_prob_iterasi1

# ==========================================
# JALANKAN DUA SKENARIO
# ==========================================
print("=" * 55)
print("  SKENARIO 1: Tanpa memperhitungkan macet (Normal)")
print("=" * 55)
rute_normal, jarak_normal, riwayat_normal, _, _ = jalankan_aco(False, "Normal")
print(f"  Jarak terpendek : {jarak_normal:.4f} km")
print(f"  Rute            : {' → '.join(nama_lokasi[i] for i in rute_normal)}\n")

print("=" * 55)
print("  SKENARIO 2: Dengan penalti jalur macet")
print("=" * 55)
rute_macet, jarak_macet, riwayat_macet, feromon_akhir, tabel_prob = jalankan_aco(True, "Macet")
print(f"  Jarak terpendek : {jarak_macet:.4f} km")
print(f"  Rute            : {' → '.join(nama_lokasi[i] for i in rute_macet)}\n")

# ==========================================
# BAGIAN 3: TAMPILKAN RUMUS & TABEL PROBABILITAS
# ==========================================
print("=" * 55)
print("  RUMUS PROBABILITAS PEMILIHAN JALUR (ACO)")
print("=" * 55)
print("""
  P(i→j) = [ τ(i,j)^α  ×  η(i,j)^β ]
            ─────────────────────────────────────
            Σₛ [ τ(i,s)^α  ×  η(i,s)^β ]

  Keterangan:
    τ(i,j)  = intensitas feromon pada jalur i→j
    η(i,j)  = visibilitas = 1/jarak(i,j)
               (jika macet: η dibagi PENALTI_MACET)
    α = {alpha}   → bobot kepentingan feromon
    β = {beta}   → bobot kepentingan visibilitas
    Σ       = penjumlahan atas semua kota belum dikunjungi
""".format(alpha=alpha, beta=beta))

print("-" * 95)
print(f"  Contoh perhitungan: dari DEPOT → semua titik (Skenario Macet, iterasi-1, α={alpha}, β={beta})")
print("-" * 95)
print(f"  {'Tujuan':<20} {'Jarak(km)':>9} {'τ(0,j)':>8} {'η(0,j)':>10} {'τ^α×η^β':>10} {'P(0→j)':>8}  Status")
print("-" * 95)

for d in sorted(tabel_prob, key=lambda x: -x["prob"]):
    status = "🔴 MACET (η÷{:.0f})".format(PENALTI_MACET) if d["macet"] else "✅ Lancar"
    print(f"  {d['nama']:<20} {d['dist']:>9.4f} {d['tau']:>8.4f} {d['eta']:>10.6f} {d['skor']:>10.6f} {d['prob']*100:>7.2f}%  {status}")

print("-" * 95)
print()

# ==========================================
# BAGIAN 4: VISUALISASI GRAFIK & PETA
# ==========================================

# 4A. Grafik Konvergensi (kedua skenario dalam satu gambar)
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

for ax, riwayat, warna, judul in [
    (axes[0], riwayat_normal, '#2980b9', 'Normal (tanpa penalti macet)'),
    (axes[1], riwayat_macet,  '#e74c3c', 'Dengan Penalti Macet'),
]:
    ax.plot(range(1, iterasi + 1), riwayat, marker='o', linestyle='-',
            color=warna, markersize=3, linewidth=1.5)
    ax.set_title(f'Konvergensi ACO — {judul}', fontsize=12)
    ax.set_xlabel('Iterasi', fontsize=10)
    ax.set_ylabel('Total Jarak Terpendek (km)', fontsize=10)
    ax.grid(True, linestyle='--', alpha=0.6)

plt.suptitle('Perbandingan Konvergensi Dua Skenario', fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.show()

# 4B. Bar Chart Probabilitas dari Depot (skenario macet)
tabel_sorted = sorted(tabel_prob, key=lambda x: -x["prob"])
labels  = [d["nama"].split("(")[0].strip() for d in tabel_sorted]
probs   = [d["prob"] * 100 for d in tabel_sorted]
warna_b = ['#e74c3c' if d["macet"] else '#2ecc71' for d in tabel_sorted]

plt.figure(figsize=(10, 4))
bars = plt.bar(labels, probs, color=warna_b, edgecolor='white', linewidth=0.8)
for bar, prob in zip(bars, probs):
    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
             f'{prob:.1f}%', ha='center', va='bottom', fontsize=9)
plt.title('Probabilitas Pemilihan Jalur dari Depot (Iterasi-1, Skenario Macet)\n'
          '🔴 Merah = jalur macet (probabilitas ditekan)  |  🟢 Hijau = lancar', fontsize=12)
plt.ylabel('Probabilitas (%)', fontsize=10)
plt.xlabel('Tujuan', fontsize=10)
plt.ylim(0, max(probs) * 1.2)
plt.grid(axis='y', linestyle='--', alpha=0.5)
plt.tight_layout()
plt.show()

# 4C. Peta Folium — Rute Normal vs Macet
print("\nMeminta data jalan raya dari server OSRM...")

def ambil_rute_osrm(rute_indeks):
    koordinat_string = ";".join(
        [f"{koordinat[idx][1]},{koordinat[idx][0]}" for idx in rute_indeks]
    )
    url = (f"http://router.project-osrm.org/route/v1/driving/{koordinat_string}"
           f"?geometries=geojson&overview=full")
    try:
        response = requests.get(url, timeout=10).json()
        if response.get("code") == "Ok":
            return [[c[1], c[0]] for c in response["routes"][0]["geometry"]["coordinates"]]
    except Exception:
        pass
    return [koordinat[idx] for idx in rute_indeks]

jalur_normal_raya = ambil_rute_osrm(rute_normal)
jalur_macet_raya  = ambil_rute_osrm(rute_macet)

peta = folium.Map(location=koordinat[0], zoom_start=13, tiles='CartoDB positron')

# Marker semua titik
for i, coord in enumerate(koordinat):
    warna = 'red' if i == 0 else ('orange' if any(is_macet(i, j) for j in range(jml_titik)) else 'blue')
    ikon  = 'home' if i == 0 else 'shopping-cart'
    folium.Marker(
        location=coord,
        popup=f"<b>{nama_lokasi[i]}</b>",
        tooltip=nama_lokasi[i],
        icon=folium.Icon(color=warna, icon=ikon)
    ).add_to(peta)

# Tandai jalur macet dengan garis tebal merah transparan
fg_macet_highlight = folium.FeatureGroup(name='⚠️ Jalur Macet')
for (a, b) in JALUR_MACET:
    folium.PolyLine(
        [koordinat[a], koordinat[b]],
        color='#e74c3c',
        weight=10,
        opacity=0.35,
        tooltip=f"⚠️ MACET: {nama_lokasi[a]} ↔ {nama_lokasi[b]}"
    ).add_to(fg_macet_highlight)
peta.add_child(fg_macet_highlight)

# LAYER 1: Rute Normal (Biru, putus-putus)
fg_normal = folium.FeatureGroup(name='🔵 Rute Normal (tanpa macet)')
folium.PolyLine(
    jalur_normal_raya,
    color='#2980b9',
    weight=4,
    opacity=0.7,
    dash_array='10, 8',
    tooltip=f"Rute Normal — {jarak_normal:.2f} km"
).add_to(fg_normal)
peta.add_child(fg_normal)

# LAYER 2: Rute Hindari Macet (Hijau, tebal)
fg_hindari = folium.FeatureGroup(name='🟢 Rute Hindari Macet (Optimal)')
folium.PolyLine(
    jalur_macet_raya,
    color='#27ae60',
    weight=5,
    opacity=0.9,
    tooltip=f"Rute Hindari Macet — {jarak_macet:.2f} km"
).add_to(fg_hindari)
peta.add_child(fg_hindari)

folium.LayerControl().add_to(peta)

# ==========================================
# BAGIAN 5: RINGKASAN AKHIR
# ==========================================
print("\n" + "=" * 55)
print("  RINGKASAN HASIL")
print("=" * 55)
print(f"  Jarak skenario normal  : {jarak_normal:.4f} km")
print(f"  Jarak hindari macet    : {jarak_macet:.4f} km")
print(f"  Selisih                : {jarak_macet - jarak_normal:+.4f} km")
print()
print("  Rute Normal :")
print("  ", " → ".join(nama_lokasi[i] for i in rute_normal))
print()
print("  Rute Hindari Macet :")
print("  ", " → ".join(nama_lokasi[i] for i in rute_macet))
print()
print("  Jalur berbeda antara dua skenario :")
set_normal = set(zip(rute_normal, rute_normal[1:]))
set_macet  = set(zip(rute_macet,  rute_macet[1:]))
hanya_normal = set_normal - set_macet
hanya_macet  = set_macet  - set_normal
for (a, b) in hanya_normal:
    print(f"    ❌ Ditinggalkan : {nama_lokasi[a]} → {nama_lokasi[b]}")
for (a, b) in hanya_macet:
    print(f"    ✅ Pengganti    : {nama_lokasi[a]} → {nama_lokasi[b]}")

print("\n✅ Selesai! Menampilkan Peta:\n")
display(peta)
