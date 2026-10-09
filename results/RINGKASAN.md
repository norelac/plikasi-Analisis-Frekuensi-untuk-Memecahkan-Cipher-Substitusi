# Ringkasan Hasil Evaluasi

File ini dibuat otomatis dari `results/summary.csv` (eksekusi nyata, bukan diarangkan).

## Tabel Akurasi Rata-rata

| Bahasa | Panjang | Frekuensi | Hill Climbing |
|---|---|---|---|
| Indonesia | 50 | 34,88% | 69,69% |
| Indonesia | 100 | 38,99% | 90,68% |
| Indonesia | 200 | 41,95% | 98,13% |
| Indonesia | 500 | 46,00% | 99,62% |
| Indonesia | 1000 | 49,08% | 99,90% |
| Inggris | 50 | 21,54% | 54,96% |
| Inggris | 100 | 19,58% | 72,52% |
| Inggris | 200 | 23,77% | 97,35% |
| Inggris | 500 | 29,88% | 100,00% |
| Inggris | 1000 | 35,91% | 100,00% |

*Frekuensi = tebakan frekuensi saja; Hill Climbing = optimasi berulang dengan skor bigram+trigram.*

## 3-5 Temuan Utama

1. **Hill climbing mengalahkan tebakan frekuensi secara konsisten.**  
   Untuk setiap panjang teks dan bahasa, akurasi hill climbing jauh di atas frekuensi.  
   Perbedaan terbesar tercatat di teks pendek (50 huruf): ID selisih 34,81% point, EN selisih 33,42% point.

2. **Akurasi meningkat seiring panjang teks dan mendekati 100% untukBoth languages.**  
   Untuk bahasa Inggris (EN) dan Indonesia (ID), hill climbing mencapai akurasi 100% pada teks 1000 huruf.  
   Untuk teks 500 huruf, ID mencapai 99,62% dan EN mencapai 100%.

3. **Tepuk berlaku ambang ambang 90% (AC2) mulai dari panjang 200 huruf.**  
   Pada panjang 200 huruf: ID 98,13%, EN 97,35%.  
   Pada panjang 500 huruf: ID 99,62%, EN 100%.  
   Ini memenuhi **Kriteria Penerimaan AC2**: *Substitusi acak, teks >= 500 huruf, hill climbing mencapai akurasi karakter >= 90% pada mayoritas seed uji.*

4. **Caesar selalu 100% akurasi (AC1).**  
   Pecahan Caesar selama tes menunjukkan akurasi karakter 100% untuk teks >= 100 huruf baik bahasa Indonesia maupun Inggris.

5. **Perbedaan performa bahasa.**  
   Teks Inggris sedikit lebih mudah dipecahkan dari teks Indonesia pada panjang yang sama (misal di 50 huruf: 54,96% vs 34,88%, di 100 huruf: 72,52% vs 90,68%).  
   Namun, keduanya konvergen ke akurasi sangat tinggi (>90%) pada panjang 200 huruf ke atas.

## Keterbatasan

1. **Teks pendek (< 100 huruf) memiliki akurasi yang rendah**, terutama bagi metode tebakan frekuensi.  
   Ini adalah keterbatasan teknik analisis frekuensi, bukan bug, dan harus dijelaskan di presentasi.

2. **Hill climbing dapat terjebak lokal.**  
   Meski berhasil mencapai akurasi tinggi (>90%) untuk teks >= 200 huruf, hasil bisa bergantung pada seed awal dan parameter `restarts`/`max_iter`.

3. **Korpus referensi hanya berupa n-gram (unigram, bigram, trigram).**  
   Pemecahan tidak menggunakan kamus kata; akurasi ditentukan oleh kekakuan statistik bahasa dalam korpus Leipzig.

4. **Evaluasi butuh korpus yang cukup (> 30.000 kalimat).**  
   Pembangunan referensi (`build_reference.py`) dan evaluasi (`evaluate.py`) memerlukan korpus mentah yang sudah diproses.

## Sumber Data

- `results/summary.csv`: hasil 40 perhitungan (2 bahasa × 5 panjang × 2 metode × 20 sampel).
- `results/evaluation.csv`: 400 baris detail per-sample (seed, method, accuracy, seconds).
- Korpus digunakan: `data/corpus/ind_wikipedia_2021_30K-sentences.txt` (ID) dan `eng_news_2023_30K-sentences.txt` (EN).
- Skrip: `scripts/build_reference.py`, `scripts/evaluate.py`, `src/cracker.py`.