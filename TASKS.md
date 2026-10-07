# TASKS.md

Centang `[x]` setelah selesai. Kerjakan berurutan.

## M0 Setup
- [x] Buat struktur folder sesuai PRD bagian 7, `requirements.txt`, `.gitignore`
      (abaikan `data/corpus/`, `__pycache__/`, `.venv/`).
- [x] README.md singkat berisi cara install dan menjalankan.
**Selesai jika:** `pip install -r requirements.txt` dan `pytest -q` (kosong) berjalan.

## M1 Referensi frekuensi
- [x] `scripts/build_reference.py`: baca korpus (opsi `--format leipzig|plain`), buang
      selain A-Z, hitung unigram (%), bigram dan trigram (log-prob dengan add-one smoothing),
      simpan JSON.
- [x] `src/reference.py`: fungsi `load_reference(lang)` yang membaca JSON.
- [x] **BERHENTI dan minta pengguna menaruh korpus di `data/corpus/`** bila belum ada.
      Jangan membuat angka sendiri. (Korpus sudah tersedia, tidak perlu berhenti.)
**Selesai jika:** `ref_en.json` dan `ref_id.json` ada, dan unigram-nya masuk akal
(Inggris: E tertinggi; Indonesia: A tertinggi).

## M2 Cipher
- [x] `src/cipher.py`: `caesar_encrypt/decrypt`, `generate_key(seed)`,
      `substitution_encrypt/decrypt`.
- [x] Tes: round-trip encrypt lalu decrypt sama dengan teks asli, huruf besar/kecil dan
      tanda baca terjaga, kunci valid (permutasi 26 huruf unik).
**Selesai jika:** semua tes cipher lulus.

## M3 Analisis
- [x] `src/analysis.py`: `letter_frequencies`, `ngram_counts`, `chi_square`,
      `index_of_coincidence`.
- [x] Tes dengan teks kecil yang hasilnya bisa dihitung manual.
**Selesai jika:** tes lulus.

## M4 Cracker
- [x] `crack_caesar(ciphertext, lang)` memakai chi-square.
- [x] `frequency_guess(ciphertext, lang)` memetakan peringkat frekuensi ke peringkat referensi.
- [x] `hill_climb(ciphertext, lang, restarts, iterations, seed)` memakai skor bigram+trigram.
- [x] `detect_language(ciphertext)` opsional (FR3).
- [x] Tes: Caesar 100% pada teks uji; hill climbing lebih baik dari `frequency_guess` saja.
**Selesai jika:** AC1 terpenuhi, AC2 diukur dan dilaporkan.

## M5 Evaluasi
- [x] `scripts/evaluate.py` sesuai FR5. Simpan `results/evaluation.csv` dan
      `results/accuracy_vs_length.png`.
- [x] Siapkan teks uji dari korpus (potong dari bagian yang tidak dipakai sebagai referensi
      bila memungkinkan, supaya evaluasi tidak bias).
**Selesai jika:** CSV dan grafik terbentuk dari eksekusi nyata.

## M6 Aplikasi Streamlit
- [ ] Tab Enkripsi, Analisis, Pecahkan (dengan editor pemetaan manual), Evaluasi.
- [ ] Bar chart perbandingan ciphertext vs referensi.
**Selesai jika:** AC4 terpenuhi, dicoba manual dengan satu contoh Inggris dan satu Indonesia.

## M7 Finalisasi
- [ ] `pytest -q` lulus semua, `ruff check` bersih.
- [ ] README dilengkapi: cara pakai, ringkasan hasil evaluasi, keterbatasan.
- [ ] Buat `results/RINGKASAN.md`: angka evaluasi utama dan temuan, sebagai bahan slide.

## Usulan (jangan dikerjakan tanpa persetujuan)
-