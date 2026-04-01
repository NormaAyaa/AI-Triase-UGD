"""
AI Agent Triase UGD — Google GenAI SDK (Direct)
Menggunakan ESI (Emergency Severity Index) framework 1-5.

Arsitektur:
  Input pasien → Google GenAI SDK → Tool dispatch loop →
  symptom_scorer, vital_analyzer, history_lookup, bed_allocator → Output triase
"""

import json
import os
from google import genai
from google.genai import types


# ─────────────────────────────────────────────
# TOOL IMPLEMENTATIONS
# ─────────────────────────────────────────────

def symptom_scorer(gejala: str, usia: int, riwayat: str) -> dict:
    """Menilai tingkat urgency berdasarkan gejala, usia, dan riwayat penyakit."""
    gejala_lower = gejala.lower()

    critical_keywords = [
        "tidak sadar", "penurunan kesadaran", "henti jantung", "henti napas",
        "nyeri dada hebat", "sesak berat", "kejang aktif", "perdarahan masif",
        "syok", "tidak respons"
    ]
    emergent_keywords = [
        "stroke", "kelemahan separuh", "bicara pelo", "sesak napas",
        "nyeri perut hebat", "demam tinggi kejang", "nyeri kepala hebat tiba-tiba",
        "muntah darah", "bab darah", "fraktur terbuka", "luka dalam"
    ]
    urgent_keywords = [
        "nyeri sedang", "demam", "mual muntah", "luka robek", "keseleo",
        "diare", "batuk berdarah", "nyeri punggung"
    ]

    critical_flags  = [k for k in critical_keywords  if k in gejala_lower]
    emergent_flags  = [k for k in emergent_keywords  if k in gejala_lower]
    urgent_flags    = [k for k in urgent_keywords    if k in gejala_lower]

    if critical_flags:
        base_score, level_suggestion = 5, 1
    elif emergent_flags:
        base_score, level_suggestion = 4, 2
    elif urgent_flags:
        base_score, level_suggestion = 3, 3
    else:
        base_score, level_suggestion = 2, 4

    age_modifier = 0
    if usia < 2 or usia > 75:
        age_modifier = 1
        level_suggestion = max(1, level_suggestion - 1)

    riwayat_berat = ["jantung", "gagal jantung", "dm", "diabetes", "hipertensi",
                     "asma", "copd", "kanker", "imunosupresi", "stroke"]
    riwayat_flags    = [r for r in riwayat_berat if r in riwayat.lower()]
    riwayat_modifier = min(len(riwayat_flags), 2)
    final_score      = min(5, base_score + age_modifier + riwayat_modifier)

    return {
        "urgency_score": final_score,
        "suggested_level": level_suggestion,
        "critical_flags": critical_flags,
        "emergent_flags": emergent_flags,
        "urgent_flags": urgent_flags,
        "age_modifier": age_modifier,
        "riwayat_flags": riwayat_flags,
        "summary": (f"Skor urgency {final_score}/7. Gejala kritis: {len(critical_flags)}, "
                    f"emergensi: {len(emergent_flags)}, urgen: {len(urgent_flags)}."),
    }


def vital_sign_analyzer(hr: int, sbp: int, dbp: int, spo2: int, rr: int, suhu: float) -> dict:
    """Menganalisis tanda vital dan mendeteksi nilai abnormal."""
    alerts, level_impact = [], 0

    if hr < 40 or hr > 150:
        alerts.append(f"HR KRITIS: {hr} bpm"); level_impact += 2
    elif hr < 50 or hr > 130:
        alerts.append(f"HR ABNORMAL: {hr} bpm"); level_impact += 1

    if sbp < 70:
        alerts.append(f"HIPOTENSI BERAT: SBP {sbp} mmHg — risiko syok"); level_impact += 2
    elif sbp < 90:
        alerts.append(f"HIPOTENSI: SBP {sbp} mmHg"); level_impact += 1
    elif sbp > 200:
        alerts.append(f"HIPERTENSI BERAT: SBP {sbp} mmHg"); level_impact += 1

    if spo2 < 85:
        alerts.append(f"SpO2 KRITIS: {spo2}% — hipoksia berat"); level_impact += 2
    elif spo2 < 92:
        alerts.append(f"SpO2 RENDAH: {spo2}%"); level_impact += 1

    if rr < 8 or rr > 35:
        alerts.append(f"RR KRITIS: {rr} x/menit"); level_impact += 2
    elif rr < 12 or rr > 28:
        alerts.append(f"RR ABNORMAL: {rr} x/menit"); level_impact += 1

    if suhu < 35.0:
        alerts.append(f"HIPOTERMIA: {suhu}°C"); level_impact += 1
    elif suhu > 40.0:
        alerts.append(f"HIPERTERMIA BERAT: {suhu}°C"); level_impact += 1
    elif suhu > 38.5:
        alerts.append(f"Demam tinggi: {suhu}°C")

    if level_impact >= 4:    vital_category = "KRITIS"
    elif level_impact >= 2:  vital_category = "ABNORMAL SIGNIFIKAN"
    elif level_impact >= 1:  vital_category = "ABNORMAL RINGAN"
    else:                    vital_category = "NORMAL"

    return {
        "vital_category": vital_category,
        "level_impact": level_impact,
        "alerts": alerts,
        "values": {"HR": f"{hr} bpm", "BP": f"{sbp}/{dbp} mmHg",
                   "SpO2": f"{spo2}%", "RR": f"{rr} x/menit", "Suhu": f"{suhu}°C"},
        "summary": (f"Vital sign {vital_category}. {len(alerts)} alert terdeteksi. "
                    f"Level impact: +{level_impact}."),
    }


def history_lookup(riwayat: str, alergi: str, usia: int) -> dict:
    """Menganalisis riwayat penyakit dan alergi untuk konteks klinis."""
    kontraindikasi, risk_factors = [], []
    riwayat_lower = riwayat.lower()

    if any(k in riwayat_lower for k in ["jantung", "koroner", "gagal jantung", "aritmia"]):
        risk_factors.append("Risiko kardiovaskular tinggi")
        kontraindikasi.append("Hati-hati: β-blocker, antiaritmia — cek EKG dulu")
    if "hipertensi" in riwayat_lower:
        risk_factors.append("Hipertensi — pantau BP serial")
    if any(k in riwayat_lower for k in ["dm", "diabetes"]):
        risk_factors.append("DM — cek GDS segera")
        kontraindikasi.append("Hindari glukokortikoid dosis tinggi tanpa monitor gula")
    if any(k in riwayat_lower for k in ["asma", "copd", "ppok"]):
        risk_factors.append("Gangguan respirasi kronis")
        kontraindikasi.append("Hindari β-blocker non-selektif, NSAIDs")
    if any(k in riwayat_lower for k in ["gagal ginjal", "ckd", "hemodialisis"]):
        risk_factors.append("Gangguan fungsi ginjal — sesuaikan dosis obat")
        kontraindikasi.append("Hindari NSAID, sesuaikan dosis antibiotik")

    alergi_lower = alergi.lower()
    if "penisilin" in alergi_lower or "amoksisilin" in alergi_lower:
        kontraindikasi.append("ALERGI PENISILIN: gunakan alternatif antibiotik")
    if "aspirin" in alergi_lower or "nsaid" in alergi_lower:
        kontraindikasi.append("ALERGI NSAID: hindari semua golongan NSAID")
    if "sulfa" in alergi_lower:
        kontraindikasi.append("ALERGI SULFA: hindari kotrimoksazol")

    if usia < 5:    risk_factors.append("Anak kecil — dosis dan nilai normal berbeda")
    elif usia > 70: risk_factors.append("Lansia — risiko komplikasi lebih tinggi, polifarmasi")

    high_risk = len(risk_factors) >= 2 or len(kontraindikasi) >= 2
    return {
        "high_risk": high_risk,
        "risk_factors": risk_factors,
        "kontraindikasi": kontraindikasi,
        "riwayat_relevan": riwayat if riwayat != "Tidak ada" else "Tidak ada riwayat signifikan",
        "alergi_relevan": alergi if alergi != "Tidak ada" else "Tidak ada alergi diketahui",
        "summary": (f"{'Pasien RISIKO TINGGI' if high_risk else 'Risiko standar'}. "
                    f"{len(risk_factors)} faktor risiko, {len(kontraindikasi)} kontraindikasi."),
    }


def bed_allocator(esi_level: int, vital_category: str, high_risk: bool) -> dict:
    """Merekomendasikan penempatan bed berdasarkan level ESI, kondisi vital, dan risiko."""
    allocation_map = {1: "Resusitasi", 2: "Kritis", 3: "Semi-kritis",
                      4: "Observasi", 5: "Rawat jalan"}

    adjusted_level = esi_level
    if vital_category == "KRITIS" and esi_level > 1:
        adjusted_level = max(1, esi_level - 1)
    elif vital_category == "ABNORMAL SIGNIFIKAN" and esi_level > 2:
        adjusted_level = max(2, esi_level - 1)
    if high_risk and adjusted_level > 2:
        adjusted_level = max(2, adjusted_level - 1)

    ruangan = allocation_map.get(adjusted_level, "Semi-kritis")
    ruangan_info = {
        "Resusitasi":  {"kapasitas": "2 bed",     "monitoring": "Kontinu — EKG, SpO2, BP invasif",     "rasio_staf": "1:1"},
        "Kritis":      {"kapasitas": "6 bed",     "monitoring": "Kontinu — EKG, SpO2, BP non-invasif", "rasio_staf": "1:2"},
        "Semi-kritis": {"kapasitas": "10 bed",    "monitoring": "Tiap 30 menit",                       "rasio_staf": "1:4"},
        "Observasi":   {"kapasitas": "15 bed",    "monitoring": "Tiap 1–2 jam",                        "rasio_staf": "1:6"},
        "Rawat jalan": {"kapasitas": "Unlimited", "monitoring": "Tidak diperlukan",                    "rasio_staf": "1:10"},
    }
    return {
        "ruangan": ruangan,
        "esi_adjusted": adjusted_level,
        "upgrade_dilakukan": adjusted_level < esi_level,
        "alasan_upgrade": (
            f"Upgrade dari Level {esi_level} ke {adjusted_level} karena vital {vital_category}."
            if adjusted_level < esi_level else "Tidak ada upgrade"
        ),
        "detail_ruangan": ruangan_info.get(ruangan, {}),
        "summary": f"Pasien ditempatkan di {ruangan} (ESI {adjusted_level}).",
    }


# ─────────────────────────────────────────────
# TOOL REGISTRY
# ─────────────────────────────────────────────

TOOL_FUNCTIONS = {
    "symptom_scorer":    symptom_scorer,
    "vital_sign_analyzer": vital_sign_analyzer,
    "history_lookup":    history_lookup,
    "bed_allocator":     bed_allocator,
}

TOOL_DECLARATIONS = [
    types.FunctionDeclaration(
        name="symptom_scorer",
        description="Menilai tingkat urgency berdasarkan gejala teks bebas, usia pasien, dan riwayat penyakit.",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "gejala":  types.Schema(type=types.Type.STRING, description="Keluhan/gejala pasien"),
                "usia":    types.Schema(type=types.Type.INTEGER, description="Usia pasien dalam tahun"),
                "riwayat": types.Schema(type=types.Type.STRING, description="Riwayat penyakit pasien"),
            },
            required=["gejala", "usia", "riwayat"],
        ),
    ),
    types.FunctionDeclaration(
        name="vital_sign_analyzer",
        description="Menganalisis tanda vital pasien dan mendeteksi nilai abnormal.",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "hr":   types.Schema(type=types.Type.INTEGER, description="Heart rate (bpm)"),
                "sbp":  types.Schema(type=types.Type.INTEGER, description="Tekanan darah sistolik (mmHg)"),
                "dbp":  types.Schema(type=types.Type.INTEGER, description="Tekanan darah diastolik (mmHg)"),
                "spo2": types.Schema(type=types.Type.INTEGER, description="SpO2 (%)"),
                "rr":   types.Schema(type=types.Type.INTEGER, description="Respiratory rate (x/menit)"),
                "suhu": types.Schema(type=types.Type.NUMBER,  description="Suhu tubuh (°C)"),
            },
            required=["hr", "sbp", "dbp", "spo2", "rr", "suhu"],
        ),
    ),
    types.FunctionDeclaration(
        name="history_lookup",
        description="Menganalisis riwayat penyakit dan alergi pasien untuk konteks klinis.",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "riwayat": types.Schema(type=types.Type.STRING,  description="Riwayat penyakit"),
                "alergi":  types.Schema(type=types.Type.STRING,  description="Alergi obat/makanan"),
                "usia":    types.Schema(type=types.Type.INTEGER, description="Usia pasien"),
            },
            required=["riwayat", "alergi", "usia"],
        ),
    ),
    types.FunctionDeclaration(
        name="bed_allocator",
        description="Merekomendasikan penempatan bed berdasarkan level ESI, kondisi vital, dan status risiko.",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "esi_level":      types.Schema(type=types.Type.INTEGER, description="Level ESI 1-5"),
                "vital_category": types.Schema(type=types.Type.STRING,  description="Kategori vital sign"),
                "high_risk":      types.Schema(type=types.Type.BOOLEAN, description="Apakah pasien risiko tinggi"),
            },
            required=["esi_level", "vital_category", "high_risk"],
        ),
    ),
]

SYSTEM_PROMPT = """Kamu adalah sistem AI pendukung keputusan triase UGD (Unit Gawat Darurat) rumah sakit.
Tugasmu adalah membantu tenaga medis menentukan level prioritas penanganan pasien menggunakan
framework ESI (Emergency Severity Index) 1-5.

PENTING: Kamu adalah alat bantu keputusan klinis, BUKAN pengganti dokter atau perawat terlatih.

Untuk setiap pasien, kamu HARUS memanggil keempat tools secara berurutan:
1. symptom_scorer — menilai gejala
2. vital_sign_analyzer — menganalisis tanda vital
3. history_lookup — menganalisis riwayat dan alergi
4. bed_allocator — rekomendasi penempatan (gunakan hasil tools sebelumnya)

Setelah semua tools dipanggil, berikan keputusan triase final dalam format JSON:
{
  "esi_level": <1-5>,
  "label": "<Level X — nama level>",
  "ruangan": "<nama ruangan>",
  "waktu_penanganan": "<target waktu>",
  "reasoning": "<penjelasan klinis 2-3 kalimat>",
  "tindakan_prioritas": ["<tindakan 1>", "<tindakan 2>"],
  "peringatan": ["<peringatan jika ada>"],
  "disclaimer": "Rekomendasi ini adalah alat bantu. Keputusan final ada pada tenaga medis."
}"""


# ─────────────────────────────────────────────
# MAIN TRIAGE FUNCTION
# ─────────────────────────────────────────────

def run_triage(patient_data: dict, api_key: str) -> dict:
    """
    Menjalankan triase untuk satu pasien menggunakan Google GenAI SDK langsung.
    Returns dict dengan result dan tool_calls trace.
    """
    client = genai.Client(api_key=api_key)
    tools  = [types.Tool(function_declarations=TOOL_DECLARATIONS)]
    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        tools=tools,
        temperature=0.1,
    )

    patient_json = json.dumps(patient_data, ensure_ascii=False, indent=2)
    prompt = f"Data pasien berikut perlu ditriase:\n{patient_json}\n\nLakukan triase lengkap dengan memanggil semua tools, kemudian berikan keputusan final dalam format JSON."

    # Build conversation history
    contents = [types.Content(role="user", parts=[types.Part(text=prompt)])]
    tool_calls_trace = []

    # Agentic loop — max 10 turns untuk safety
    for _ in range(10):
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=contents,
            config=config,
        )

        candidate = response.candidates[0]
        parts      = candidate.content.parts

        # Append model response to history
        contents.append(types.Content(role="model", parts=parts))

        # Check if there are function calls
        fn_calls = [p for p in parts if p.function_call is not None]

        if not fn_calls:
            # No more function calls — extract final text response
            break

        # Execute all function calls
        fn_responses = []
        for part in fn_calls:
            fc   = part.function_call
            name = fc.name
            args = dict(fc.args)

            # Execute the tool
            try:
                tool_fn = TOOL_FUNCTIONS.get(name)
                if tool_fn:
                    result = tool_fn(**args)
                else:
                    result = {"error": f"Tool '{name}' tidak ditemukan"}
            except Exception as e:
                result = {"error": str(e)}

            tool_calls_trace.append({"tool": name, "input": args, "output": result})

            fn_responses.append(types.Part(
                function_response=types.FunctionResponse(
                    name=name,
                    response=result,
                )
            ))

        # Append tool results to history
        contents.append(types.Content(role="user", parts=fn_responses))

    # Extract final text
    final_text = ""
    for part in parts:
        if hasattr(part, "text") and part.text:
            final_text += part.text

    # Parse JSON result
    triage_result = {}
    try:
        start = final_text.find("{")
        end   = final_text.rfind("}") + 1
        if start >= 0 and end > start:
            triage_result = json.loads(final_text[start:end])
    except json.JSONDecodeError:
        triage_result = {
            "esi_level": 3,
            "label": "Level 3 — Urgent",
            "ruangan": "Semi-kritis",
            "waktu_penanganan": "< 30 menit",
            "reasoning": final_text[:300] if final_text else "Gagal parse hasil",
            "tindakan_prioritas": ["Evaluasi dokter segera"],
            "peringatan": [],
            "disclaimer": "Rekomendasi ini adalah alat bantu. Keputusan final ada pada tenaga medis.",
        }

    return {
        "patient":      patient_data,
        "result":       triage_result,
        "tool_calls":   tool_calls_trace,
        "raw_response": final_text,
    }
