# PRD: Aplikasi Analisis Frekuensi untuk Memecahkan Cipher Substitusi

## 1. Ringkasan
Aplikasi untuk mendemonstrasikan serangan **analisis frekuensi** terhadap cipher
substitusi (Caesar dan monoalphabetic), mendukung teks **Bahasa Indonesia** dan
**Bahasa Inggris**. Dibuat untuk tugas UTS mata kuliah Kriptografi (Challenge 1:
presentasi teknik analisis frekuensi + program aplikasinya, khusus algoritma substitusi).

## 2. Tujuan
- G1: Mendemonstrasikan bahwa cipher substitusi bocor lewat pola statistik bahasa.
- G2: Menyediakan alat interaktif: enkripsi, analisis frekuensi, dan pemecahan cipher.
- G3: Menghasilkan data evaluasi (akurasi vs panjang teks) untuk bahan presentasi.

## 3. Di Luar Lingkup (Non-Goals)
- Cipher polialfabetik (Vigenere, dll.) dan cipher modern (AES, RSA).
- Akun pengguna, database, deployment produksi.
- Bahasa selain Indonesia dan Inggris.

## 4. Pengguna
Dosen penguji dan mahasiswa lain saat demo; pembuat project saat belajar.

## 5. Kebutuhan Fungsional

### FR1 Cipher
- Caesar: enkripsi/dekripsi dengan shift 0-25.
- Substitusi acak: generate kunci permutasi A-Z (dengan seed opsional), enkripsi/dekripsi.
- Pertahankan huruf besar/kecil, spasi, angka, dan tanda baca. Hanya huruf A-Z yang diubah.

### FR2 Analisis Frekuensi
- Hitung frekuensi huruf (unigram), bigram, dan trigram dari sebuah teks.
- Tampilkan perbandingan frekuensi ciphertext vs frekuensi referensi bahasa terpilih.
- Hitung statistik pendukung: chi-square terhadap referensi, Index of Coincidence.

### FR3 Pemecahan Otomatis
- Caesar: coba 26 shift, pilih yang chi-square-nya terkecil.
- Substitusi: (a) tebakan awal berdasarkan peringkat frekuensi; (b) perbaikan dengan
  **hill climbing**: tukar dua huruf pada kunci, terima jika skor n-gram membaik,
  dengan beberapa kali restart acak. Skor = log-probabilitas bigram + trigram dari referensi.
- Mode pilih bahasa manual, plus opsi "deteksi otomatis" (coba kedua bahasa, ambil skor terbaik).

### FR4 Editor Pemetaan Manual
- Tabel pemetaan huruf cipher -> huruf plain yang bisa diubah pengguna.
- Plaintext hasil dekripsi langsung diperbarui saat pemetaan berubah.
- Tombol: "Terapkan tebakan otomatis", "Reset", "Tukar dua huruf".
- Tandai huruf yang sudah dipetakan dan huruf plaintext yang bentrok (dipakai dua kali).

### FR5 Evaluasi
- Script yang membuat teks uji dengan panjang 50, 100, 200, 500, 1000 huruf per bahasa,
  mengenkripsi dengan kunci acak (seed tetap), memecahkan dengan kedua metode
  (tebakan frekuensi saja vs hill climbing), lalu menyimpan hasil ke CSV.
- Metrik: **akurasi karakter** = persentase huruf plaintext yang benar setelah dekripsi.
- Hasilkan grafik akurasi vs panjang teks (PNG) untuk slide.

### FR6 Referensi Frekuensi
- Script `build_reference.py` membangun `ref_en.json` dan `ref_id.json` dari korpus
  (format Leipzig: `nomor<TAB>kalimat`, atau teks biasa).
- JSON berisi: frekuensi unigram (%), serta bigram dan trigram (log-probabilitas).
- **Angka frekuensi tidak boleh dikarang oleh agent.** Harus dihitung dari korpus.

## 6. Kebutuhan Non-Fungsional
- Python 3.11+, dependensi minimal (lihat requirements.txt).
- Logika inti (cipher, analisis, cracking) bebas dari UI agar bisa diuji.
- Hasil evaluasi reproducible (seed tetap).
- Antarmuka berbahasa Indonesia. Nama fungsi/variabel dalam bahasa Inggris.
- Pemecahan teks 1000 huruf selesai < 10 detik di laptop biasa.

## 7. Arsitektur

```
project-analisis-frekuensi/
├── data/
│   ├── corpus/            # korpus mentah (tidak di-commit)
│   ├── ref_en.json
│   ├── ref_id.json
│   └── samples/           # contoh teks uji
├── src/
│   ├── cipher.py          # FR1
│   ├── analysis.py        # FR2
│   ├── cracker.py         # FR3
│   ├── reference.py       # muat/bangun referensi (FR6)
│   └── app.py             # UI Streamlit (FR4)
├── scripts/
│   ├── build_reference.py
│   └── evaluate.py        # FR5
├── tests/
├── results/               # CSV dan grafik evaluasi
├── notebooks/             # opsional, hanya untuk eksperimen
├── PRD.md, AGENTS.md, TASKS.md, requirements.txt, README.md
```

## 8. Antarmuka (Streamlit, 4 tab)
1. **Enkripsi**: input teks, pilih Caesar/Substitusi, atur kunci, tampilkan ciphertext.
2. **Analisis**: input ciphertext, pilih bahasa, tampilkan bar chart ciphertext vs referensi,
   tabel bigram/trigram teratas, nilai chi-square dan IC.
3. **Pecahkan**: tombol auto-crack, editor pemetaan manual, hasil plaintext berdampingan
   dengan ciphertext.
4. **Evaluasi**: tampilkan tabel dan grafik dari `results/`.

## 9. Kriteria Penerimaan
- AC1: Caesar dengan teks Inggris dan Indonesia >= 100 huruf dipecahkan dengan akurasi 100%.
- AC2: Substitusi acak, teks >= 500 huruf, hill climbing mencapai akurasi karakter >= 90%
  pada mayoritas seed uji. Jika tidak tercapai, laporkan angka sebenarnya di hasil evaluasi.
- AC3: Semua tes pytest lulus.
- AC4: `streamlit run src/app.py` berjalan tanpa error dan semua tab berfungsi.
- AC5: `evaluate.py` menghasilkan CSV dan grafik yang bisa langsung dipakai di slide.

## 10. Risiko
- Teks pendek (< 100 huruf) akurasinya rendah. Ini keterbatasan teknik, bukan bug,
  dan harus dijelaskan di presentasi.
- Korpus belum tersedia. Agent harus berhenti dan meminta pengguna mengunduhnya.
- Bahasa Indonesia dan Inggris dibedakan lewat referensi n-gram, bukan kamus kata.