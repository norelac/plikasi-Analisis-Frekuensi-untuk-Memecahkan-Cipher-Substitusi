# Aplikasi Analisis Frekuensi untuk Memecahkan Cipher Substitusi

Aplikasi Python dan Streamlit untuk mendemonstrasikan serangan **analisis frekuensi** terhadap cipher substitusi (Caesar dan monoalfabetik), mendukung teks **Bahasa Indonesia** dan **Bahasa Inggris**. Dibuat untuk tugas UTS mata kuliah Kriptografi (Challenge 1).

## 🚀 Fitur Utama

- **Enkripsi**: Caesar Cipher (shift 0-25) dan Substitusi Acak (permutasi A-Z dengan seed opsional).
- **Analisis Frekuensi**: Perbandingan frekuensi unigram (huruf) vs referensi, top bigram/trigram, Chi-square, dan Index of Coincidence (IC).
- **Pemecahan Cipher**:
  - Caesar: Chi-square scanning 26 shift.
  - Substitusi: Tebakan awal berbasis peringkat frekuensi, dioptimasi dengan **Hill Climbing** (log-probabilitas bigram + trigram).
  - Editor pemetaan manual dengan deteksi bentrok (duplikasi) huruf plaintext.
  - Deteksi bahasa otomatis (ID / EN).
- **Evaluasi**: Pengujian akurasi vs panjang teks (50, 100, 200, 500, 1000 huruf) dengan grafik otomatis.

## 📦 Instalasi

Pastikan menggunakan Python 3.11+.

```bash
# 1. Clone repository
git clone https://github.com/norelac/plikasi-Analisis-Frekuensi-untuk-Memecahkan-Cipher-Substitusi.git
cd plikasi-Analisis-Frekuensi-untuk-Memecahkan-Cipher-Substitusi

# 2. Buat virtual environment
python -m venv .venv

# 3. Aktivasi virtual environment
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Windows CMD:
.venv\Scripts\activate.bat
# Linux / macOS:
source .venv/bin/activate

# 4. Install dependensi
pip install -r requirements.txt
```

## 🛠️ Penggunaan

### 1. Menjalankan Aplikasi Web (Streamlit)

```bash
streamlit run src/app.py
```

Aplikasi akan terbuka otomatis di browser pada `http://localhost:8501`.

### 2. Membangun Referensi Frekuensi (Opsional)

Jika ingin memperbarui frekuensi dari korpus:

```bash
# Bahasa Indonesia
python scripts/build_reference.py --corpus data/corpus/ind_wikipedia_2021_30K-sentences.txt --lang id --out data/ref_id.json

# Bahasa Inggris
python scripts/build_reference.py --corpus data/corpus/eng_news_2023_30K-sentences.txt --lang en --out data/ref_en.json
```

*Catatan: 10% kalimat terakhir otomatis disisihkan sebagai holdout (`data/samples/holdout_<lang>.txt`) untuk data uji.*

### 3. Menjalankan Evaluasi Akurasi

```bash
# Evaluasi cepat (N=3 sampel)
python scripts/evaluate.py --quick

# Evaluasi penuh (N=20 sampel, butuh beberapa menit)
python scripts/evaluate.py
```

Hasil akan disimpan di:
- `results/evaluation.csv` (data mentah per pengujian)
- `results/summary.csv` (rata-rata per panjang teks dan metode)
- `results/accuracy_vs_length.png` (grafik akurasi)

### 4. Menjalankan Pengujian (Testing)

```bash
pytest -q
ruff check .
```

## 📂 Struktur Proyek

```
.
├── data/
│   ├── corpus/                # Korpus mentah (tidak di-commit, .gitignore)
│   ├── ref_en.json            # Referensi frekuensi n-gram Bahasa Inggris
│   ├── ref_id.json            # Referensi frekuensi n-gram Bahasa Indonesia
│   ├── samples/               # Data holdout untuk pengujian
│   └── SUMBER_KORPUS.md       # Catatan metadata sumber korpus
├── results/
│   ├── evaluation.csv         # Data hasil evaluasi per sampel
│   ├── summary.csv            # Rata-rata akurasi & waktu evaluasi
│   ├── accuracy_vs_length.png # Grafik akurasi vs panjang teks
│   └── RINGKASAN.md           # Temuan utama & analisis hasil evaluasi
├── scripts/
│   ├── build_reference.py     # Script pembuatan data referensi dari korpus
│   └── evaluate.py            # Script benchmarking & pengujian performa
├── src/
│   ├── __init__.py
│   ├── analysis.py            # Analisis frekuensi, n-gram, Chi-square, IC
│   ├── app.py                 # Antarmuka web Streamlit (4 Tab)
│   ├── cipher.py              # Enkripsi & dekripsi Caesar & substitusi
│   ├── cracker.py             # Algoritma pemecah (Caesar, frekuensi, Hill Climbing)
│   └── reference.py           # Validasi & loader data referensi
├── tests/
│   ├── test_analysis.py
│   ├── test_app.py
│   ├── test_cipher.py
│   ├── test_cracker.py
│   ├── test_evaluate.py
│   └── test_reference.py
├── AGENTS.md                  # Panduan agen AI
├── PRD.md                     # Product Requirements Document
├── TASKS.md                   # Task tracking milestone
├── requirements.txt           # Dependensi Python
└── README.md
```

## 📊 Ringkasan Hasil Evaluasi

Berdasarkan benchmark 20 sampel per konfigurasi (`results/summary.csv`):

| Panjang Teks | ID (Frekuensi) | ID (Hill Climbing) | EN (Frekuensi) | EN (Hill Climbing) |
|---|---|---|---|---|
| **50 huruf** | 34,88% | 69,69% | 21,54% | 54,96% |
| **100 huruf** | 38,99% | 90,68% | 19,58% | 72,52% |
| **200 huruf** | 41,95% | 98,13% | 23,77% | 97,35% |
| **500 huruf** | 46,00% | **99,62%** | 29,88% | **100,00%** |
| **1000 huruf**| 49,08% | **99,90%** | 35,91% | **100,00%** |

*Catatan: Caesar mencapai akurasi **100%** untuk semua teks uji >= 100 huruf.*

## ⚠️ Keterbatasan

1. **Teks Sangat Pendek (< 100 huruf)**: Analisis frekuensi rentan karena statistik kemunculan huruf belum konvergen ke distribusi bahasa asli. Ini keterbatasan teknik, bukan bug.
2. **Local Optimum pada Hill Climbing**: Hill climbing murni dapat terjebak pada optimum lokal jika restart tidak cukup banyak (diatasi dengan multi-restart dan tebakan awal berbasis frekuensi).
3. **Bergantung pada Model N-gram**: Pemecahan hanya menggunakan model unigram/bigram/trigram, bukan pemindaian kamus kosakata (*dictionary search*).

## 📚 Sumber Korpus & Sitasi

Data referensi dibangun dari **Leipzig Corpora Collection**:
- **Bahasa Indonesia**: `ind_wikipedia_2021_30K` (Wikipedia, materi 2021, 30.000 kalimat).
- **Bahasa Inggris**: `eng_news_2023_30K` (Berita web, materi 2023, 30.000 kalimat).

Sitasi resmi:
> D. Goldhahn, T. Eckart & U. Quasthoff: *Building Large Monolingual Dictionaries at the Leipzig Corpora Collection: From 100 to 200 Languages*. In: Proceedings of the 8th International Language Resources and Evaluation (LREC 2012), 2012.  
> Informasi lisensi & unduhan: https://wortschatz.uni-leipzig.de/en/download/
