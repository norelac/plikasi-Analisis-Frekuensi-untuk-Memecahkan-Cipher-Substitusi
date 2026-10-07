"""Muat dan validasi file referensi frekuensi (data/ref_<lang>.json)."""

import json
import string
from pathlib import Path

ALPHABET = string.ascii_uppercase
SUPPORTED_LANGS = ("en", "id")


def reference_path(lang: str) -> Path:
    """Kembalikan path file referensi untuk bahasa tertentu."""
    if lang not in SUPPORTED_LANGS:
        raise ValueError(
            f"Bahasa tidak didukung: {lang!r}. Pilih salah satu: {SUPPORTED_LANGS}."
        )
    return Path(__file__).resolve().parent.parent / "data" / f"ref_{lang}.json"


def validate_reference(data: dict) -> None:
    """Validasi isi struktur referensi, raise ValueError bila tidak valid."""
    for key in ("lang", "unigram", "bigram", "trigram"):
        if key not in data:
            raise ValueError(f"Referensi tidak valid: kunci {key!r} hilang.")

    unigram = data["unigram"]
    if set(unigram) != set(ALPHABET):
        raise ValueError("Referensi tidak valid: unigram harus memuat 26 huruf A-Z.")
    total = sum(unigram.values())
    if not 99.0 <= total <= 101.0:
        raise ValueError(
            f"Referensi tidak valid: total unigram {total} bukan persen (%)."
        )

    if len(data["bigram"]) != 26**2:
        raise ValueError("Referensi tidak valid: bigram harus memuat 26^2 entri.")
    if len(data["trigram"]) != 26**3:
        raise ValueError("Referensi tidak valid: trigram harus memuat 26^3 entri.")


def load_reference(lang: str) -> dict:
    """Muat referensi frekuensi untuk `lang` ('en' atau 'id').

    Mengembalikan dict dengan kunci `lang`, `unigram` (persen),
    `bigram` dan `trigram` (log-probabilitas).
    """
    path = reference_path(lang)
    if not path.is_file():
        raise FileNotFoundError(
            f"File referensi tidak ditemukan: {path}. "
            "Jalankan scripts/build_reference.py terlebih dahulu."
        )
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    validate_reference(data)
    return data
