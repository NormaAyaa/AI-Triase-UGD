# 🏥 AI Triase UGD — LangGraph + Streamlit

Sistem AI pendukung keputusan triase UGD berbasis **LangGraph agent** dengan framework **ESI (Emergency Severity Index) 1–5**. Dibangun sebagai proyek portofolio AI Engineer dengan fokus domain kesehatan Indonesia.

> ⚕️ **Disclaimer:** Sistem ini adalah alat bantu keputusan klinis, **bukan** pengganti tenaga medis terlatih. Seluruh keputusan medis tetap menjadi tanggung jawab dokter dan perawat yang berwenang.

---

## Demo

> Setelah deploy ke Streamlit Cloud, ganti baris ini dengan URL live demo kamu.
> Contoh: https://ai-triage-ugd.streamlit.app

---

## Arsitektur

```
Input pasien (gejala, vital sign, riwayat)
    │
    ▼
LangGraph Agent ─── Gemini 2.0 Flash (Google)
    │
    ├── tool: symptom_scorer       → skor urgency dari gejala teks bebas
    ├── tool: vital_sign_analyzer  → deteksi nilai HR/BP/SpO2/RR/suhu abnormal
    ├── tool: history_lookup       → analisis riwayat penyakit & kontraindikasi
    └── tool: bed_allocator        → rekomendasi ruangan + upgrade otomatis
    │
    ▼
Output: ESI level 1–5 + ruangan + reasoning chain + tindakan prioritas
```

---

## Tech Stack

| Komponen     | Library / Tool              |
|--------------|-----------------------------|
| AI Agent     | LangGraph + LangChain       |
| LLM          | Gemini 2.0 Flash (Google)   |
| UI           | Streamlit                   |
| Data         | Pandas                      |
| Deploy       | Streamlit Cloud (gratis)    |

---

## Fitur

- **Triase real-time** — input manual atau pilih dari 12 kasus demo klinis
- **Reasoning chain** — tampilkan setiap tool call dan outputnya secara transparan
- **Vital sign preview** — indikator warna otomatis (normal / warning / kritis)
- **Bed allocator cerdas** — upgrade ruangan otomatis jika vital sign kritis
- **Batch evaluasi** — jalankan 12 kasus sekaligus, bandingkan hasil AI vs label referensi

---

## ESI Framework

| Level | Nama        | Target waktu  | Kondisi                                  |
|-------|-------------|---------------|------------------------------------------|
| 1     | Immediate   | Langsung      | Mengancam jiwa, butuh intervensi segera  |
| 2     | Emergent    | < 15 menit    | Kondisi serius, risiko memburuk cepat    |
| 3     | Urgent      | < 30 menit    | Stabil, butuh beberapa intervensi        |
| 4     | Less Urgent | < 60 menit    | Satu intervensi sederhana                |
| 5     | Non-urgent  | < 120 menit   | Tidak butuh resource signifikan          |

---

## Struktur Project

```
ai-triage-ugd/
├── app.py              # Streamlit UI (3 tab: triase, demo kasus, evaluasi)
├── agent.py            # LangGraph agent + 4 tools triase
├── data.py             # 12 synthetic patient cases + ESI metadata
├── requirements.txt    # Python dependencies
├── .env.example        # Template environment variables
├── .gitignore
└── README.md
```

---

## Setup Lokal

### 1. Clone repository

```bash
git clone https://github.com/<username>/ai-triage-ugd.git
cd ai-triage-ugd
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Konfigurasi API key

```bash
cp .env.example .env
# Edit .env, isi GOOGLE_API_KEY dengan key kamu
```

Dapatkan API key di [aistudio.google.com](https://aistudio.google.com/app/apikey).

### 4. Jalankan aplikasi

```bash
streamlit run app.py
```

Buka [http://localhost:8501](http://localhost:8501) di browser, masukkan API key di sidebar.

---

## Upload ke GitHub

```bash
git init
git add .
git commit -m "feat: AI triage UGD agent with LangGraph + Streamlit"
git branch -M main
git remote add origin https://github.com/<username>/ai-triage-ugd.git
git push -u origin main
```

---

## Deploy ke Streamlit Cloud (Gratis)

1. Push repo ke GitHub (langkah di atas)
2. Buka [share.streamlit.io](https://share.streamlit.io) → **New app**
3. Pilih repo `ai-triage-ugd`, branch `main`, main file `app.py`
4. Klik **Advanced settings → Secrets**, tambahkan:

```toml
GOOGLE_API_KEY = "AIza..."
```

5. Klik **Deploy** — URL live siap dalam ~2 menit

> Setelah deploy, ganti bagian input API key di `app.py` dengan:
> ```python
> api_key = st.secrets.get("GOOGLE_API_KEY", "")
> ```

---

## Keputusan Teknis

**Kenapa LangGraph?**
LangGraph memungkinkan agent memanggil tools secara dinamis dengan state management yang eksplisit. Dibandingkan LangChain AgentExecutor biasa, LangGraph lebih mudah di-debug karena setiap node dalam graph bisa diinspeksi secara terpisah.

**Kenapa tools terpisah alih-alih satu prompt besar?**
Modularitas. Setiap tool bisa diuji secara independen, diganti dengan versi yang lebih canggih (misal: ML model untuk `symptom_scorer`), dan reasoning chain lebih transparan untuk audit klinis.

**Kenapa ESI dan bukan sistem triase lain?**
ESI adalah standar yang paling banyak digunakan secara internasional, terdokumentasi dengan baik, dan memiliki 5 level yang cukup granular untuk demo portofolio tanpa terlalu kompleks.

**Keterbatasan sistem ini:**
- Tools `symptom_scorer` dan `vital_sign_analyzer` masih berbasis rule-based sederhana — pada sistem produksi sebaiknya diganti model ML yang dilatih dengan data klinis nyata
- Dataset 12 kasus adalah data sintetis; akurasi pada data nyata belum dievaluasi
- Tidak menangani kasus dengan informasi tidak lengkap secara robust

---

## Pengembangan Lanjutan

- [ ] Ganti `symptom_scorer` dengan model IndoBERT fine-tuned pada data klinis
- [ ] Tambahkan autentikasi pengguna (login perawat/dokter)
- [ ] Simpan riwayat triase ke PostgreSQL untuk audit trail
- [ ] Integrasi dengan sistem informasi rumah sakit (SIMRS)
- [ ] Tambahkan monitoring model dengan Evidently/LangSmith
- [ ] Support input suara (Whisper) untuk situasi darurat

---

## Lisensi

MIT License — bebas digunakan untuk keperluan edukasi dan portofolio.

---

*Dibangun sebagai proyek portofolio AI Engineer — domain kesehatan Indonesia.*
