# Aplikasi Analisis Frekuensi untuk Memecahkan Cipher Substitusi

Demo serangan analisis frekuensi terhadap cipher substitusi (Caesar dan
monoalfabetik) untuk teks Bahasa Indonesia dan Inggris. Tugas UTS Kriptografi.

## Instalasi

```bash
pip install -r requirements.txt
```

## Menjalankan

```bash
streamlit run src/app.py
```

## Perintah lain

```bash
pytest -q
python scripts/build_reference.py --corpus data/corpus/<file> --lang id --out data/ref_id.json
python scripts/evaluate.py
```

Lihat `PRD.md`, `TASKS.md`, dan `AGENTS.md` untuk detail.
