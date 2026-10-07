# AGENTS.md: Panduan untuk Agent

Baca `PRD.md` dan `TASKS.md` sebelum mengerjakan apa pun.

## Aturan kerja
1. Kerjakan task di `TASKS.md` **berurutan**. Selesaikan dan uji satu milestone sebelum lanjut.
2. Setelah selesai satu task, centang di `TASKS.md` dan ringkas apa yang diubah.
3. Jangan menambah fitur di luar `PRD.md`. Kalau ada ide tambahan, tuliskan di bagian
   "Usulan" di akhir `TASKS.md`, jangan langsung dikerjakan.
4. Kalau ada yang ambigu atau korpus belum ada, **berhenti dan tanya pengguna**.
5. **Jangan mengarang data.** Frekuensi referensi harus dihitung dari korpus lewat
   `scripts/build_reference.py`. Hasil evaluasi harus dari eksekusi nyata, jangan ditulis manual.
6. Laporkan hasil apa adanya, termasuk jika target akurasi tidak tercapai.
7. **Setiap prompt selesai, jalankan `pytest -q` dan periksa hasil sebelum melanjutkan.**

## Konvensi kode
- Python 3.11+, type hints pada fungsi publik, docstring singkat.
- Nama fungsi/variabel/file dalam bahasa Inggris. Teks UI dan pesan ke pengguna dalam
  bahasa Indonesia.
- Logika inti di `src/` tidak boleh meng-import Streamlit.
- Fungsi murni (tanpa efek samping) sebisa mungkin. Randomness harus menerima parameter `seed`.
- Format dengan `ruff format` dan cek dengan `ruff check`.

## Perintah
- Install: `pip install -r requirements.txt`
- Tes: `pytest -q`
- Bangun referensi: `python scripts/build_reference.py --corpus <path> --lang id --out data/ref_id.json`
- Evaluasi: `python scripts/evaluate.py`
- Jalankan aplikasi: `streamlit run src/app.py`

## Definisi selesai
Sebuah task dianggap selesai jika kodenya berjalan, tes terkait lulus, dan
kriteria penerimaannya di `TASKS.md` terpenuhi.