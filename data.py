"""
Data loader untuk AI Triase UGD.
Mendukung:
  - Load dari CSV bawaan (dataset/sample_patients.csv)
  - Load dari file CSV yang diupload user via Streamlit
  - Validasi kolom wajib dan rentang nilai vital sign
"""

import os
import pandas as pd

# ─────────────────────────────────────────────
# KOLOM & VALIDASI
# ─────────────────────────────────────────────

REQUIRED_COLUMNS = [
    "nama", "usia", "keluhan",
    "hr", "sbp", "dbp", "spo2", "rr", "suhu",
    "riwayat", "alergi",
]

VITAL_RANGES = {
    "hr":   (0, 300),
    "sbp":  (0, 300),
    "dbp":  (0, 200),
    "spo2": (0, 100),
    "rr":   (0, 80),
    "suhu": (25.0, 45.0),
}

DEFAULT_CSV_PATH = os.path.join(
    os.path.dirname(__file__), "dataset", "sample_patients.csv"
)


# ─────────────────────────────────────────────
# LOADER FUNCTIONS
# ─────────────────────────────────────────────

def load_default():
    """Load dataset bawaan dari dataset/sample_patients.csv."""
    return load_csv(DEFAULT_CSV_PATH)


def load_csv(filepath: str):
    """
    Load dataset dari path file CSV.
    Return: (cases: list[dict], errors: list[str])
    """
    df = pd.read_csv(filepath)
    return _parse_dataframe(df)


def load_uploaded(uploaded_file):
    """
    Load dataset dari Streamlit UploadedFile object.
    Return: (cases: list[dict], errors: list[str])
    """
    df = pd.read_csv(uploaded_file)
    return _parse_dataframe(df)


def _parse_dataframe(df: pd.DataFrame):
    """Parse dan validasi DataFrame menjadi list patient dicts."""
    errors = []

    # Normalisasi nama kolom
    df.columns = [c.strip().lower() for c in df.columns]

    # Cek kolom wajib
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(
            f"Kolom wajib tidak ditemukan: {', '.join(missing)}.\n"
            f"Download template_dataset.csv untuk format yang benar."
        )

    cases = []
    for idx, row in df.iterrows():
        # Vital signs
        vital = {}
        for col, (lo, hi) in VITAL_RANGES.items():
            try:
                val = float(row[col])
                if not (lo <= val <= hi):
                    errors.append(
                        f"Baris {idx+2} ({row.get('nama','')}): "
                        f"{col}={val} di luar rentang ({lo}–{hi})"
                    )
                vital[col] = val
            except (ValueError, TypeError):
                errors.append(f"Baris {idx+2}: {col} bukan angka valid ('{row[col]}')")
                vital[col] = 0

        # Usia
        try:
            usia = int(row["usia"])
        except (ValueError, TypeError):
            errors.append(f"Baris {idx+2}: usia bukan angka valid")
            usia = 0

        case = {
            "id":      str(row.get("id", f"P{idx+1:03d}")).strip(),
            "nama":    str(row["nama"]).strip(),
            "usia":    usia,
            "keluhan": str(row["keluhan"]).strip(),
            "vital": {
                "hr":   int(vital.get("hr", 0)),
                "sbp":  int(vital.get("sbp", 0)),
                "dbp":  int(vital.get("dbp", 0)),
                "spo2": int(vital.get("spo2", 0)),
                "rr":   int(vital.get("rr", 0)),
                "suhu": round(float(vital.get("suhu", 36.5)), 1),
            },
            "riwayat": str(row.get("riwayat", "Tidak ada")).strip(),
            "alergi":  str(row.get("alergi", "Tidak ada")).strip(),
        }

        # Label opsional (untuk evaluasi)
        if "label_esi" in df.columns and pd.notna(row.get("label_esi")):
            try:
                case["label_esi"] = int(row["label_esi"])
            except (ValueError, TypeError):
                pass

        if "label_ruangan" in df.columns and pd.notna(row.get("label_ruangan")):
            case["label_ruangan"] = str(row["label_ruangan"]).strip()

        cases.append(case)

    return cases, errors


def dataframe_from_cases(cases: list) -> pd.DataFrame:
    """Konversi list cases menjadi DataFrame untuk ditampilkan di UI."""
    rows = []
    for c in cases:
        v = c.get("vital", {})
        keluhan = c.get("keluhan", "-")
        rows.append({
            "ID":          c.get("id", "-"),
            "Nama":        c.get("nama", "-"),
            "Usia":        c.get("usia", "-"),
            "Keluhan":     keluhan[:60] + ("..." if len(keluhan) > 60 else ""),
            "HR":          v.get("hr", "-"),
            "SBP":         v.get("sbp", "-"),
            "SpO2":        v.get("spo2", "-"),
            "Suhu":        v.get("suhu", "-"),
            "ESI Ref":     c.get("label_esi", "-"),
            "Ruangan Ref": c.get("label_ruangan", "-"),
        })
    return pd.DataFrame(rows)


# ─────────────────────────────────────────────
# METADATA ESI & RUANGAN
# ─────────────────────────────────────────────

ESI_DESCRIPTIONS = {
    1: {
        "label": "Level 1 — Immediate",
        "color": "#E24B4A",
        "bg": "#FCEBEB",
        "desc": "Mengancam jiwa, butuh intervensi segera",
        "waktu": "Langsung ditangani",
    },
    2: {
        "label": "Level 2 — Emergent",
        "color": "#D85A30",
        "bg": "#FAECE7",
        "desc": "Kondisi serius, risiko memburuk cepat",
        "waktu": "< 15 menit",
    },
    3: {
        "label": "Level 3 — Urgent",
        "color": "#BA7517",
        "bg": "#FAEEDA",
        "desc": "Stabil tapi butuh beberapa intervensi",
        "waktu": "< 30 menit",
    },
    4: {
        "label": "Level 4 — Less Urgent",
        "color": "#3B6D11",
        "bg": "#EAF3DE",
        "desc": "Satu intervensi sederhana dibutuhkan",
        "waktu": "< 60 menit",
    },
    5: {
        "label": "Level 5 — Non-urgent",
        "color": "#185FA5",
        "bg": "#E6F1FB",
        "desc": "Tidak butuh resource atau hanya satu resource",
        "waktu": "< 120 menit",
    },
}

RUANGAN_INFO = {
    "Resusitasi":  "Peralatan life support lengkap, tim dokter + perawat standby",
    "Kritis":      "Monitor kontinu, akses IV, observasi ketat",
    "Semi-kritis": "Observasi berkala, dapat menunggu antrian singkat",
    "Observasi":   "Pantau kondisi, tindakan minimal",
    "Rawat jalan": "Penanganan ringan, dapat pulang setelah tindakan",
}
