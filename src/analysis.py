"""Analisis frekuensi teks: unigram, n-gram, chi-square, IC.

Semua fungsi murni dan case-insensitive (teks dibersihkan ke A-Z dulu).
"""

import string
from collections import Counter

ALPHABET = string.ascii_uppercase


def _clean(text: str) -> str:
    """Ambil hanya huruf A-Z dari teks (ubah ke huruf besar)."""
    return "".join(ch for ch in text.upper() if ch in ALPHABET)


def letter_frequencies(text: str) -> dict[str, float]:
    """Frekuensi tiap huruf A-Z dalam persen (0.0 bila tak muncul)."""
    cleaned = _clean(text)
    total = len(cleaned)
    counts = Counter(cleaned)
    return {
        ch: (counts.get(ch, 0) / total * 100.0 if total else 0.0) for ch in ALPHABET
    }


def ngram_counts(text: str, n: int) -> Counter:
    """Hitung kemunculan tiap n-gram (n=2 bigram, n=3 trigram)."""
    if n not in (2, 3):
        raise ValueError(f"n harus 2 atau 3, diterima: {n!r}.")
    cleaned = _clean(text)
    return Counter(cleaned[i : i + n] for i in range(len(cleaned) - n + 1))


def chi_square(text: str, ref_unigram: dict[str, float]) -> float:
    """Chi-square jumlah huruf teks terhadap unigram referensi (persen).

    Mengembalikan tak-hingga bila teks tak memuat huruf.
    """
    cleaned = _clean(text)
    total = len(cleaned)
    if not total:
        return float("inf")
    counts = Counter(cleaned)
    score = 0.0
    for ch in ALPHABET:
        expected = total * ref_unigram.get(ch, 0.0) / 100.0
        if expected <= 0:
            continue
        score += (counts.get(ch, 0) - expected) ** 2 / expected
    return score


def index_of_coincidence(text: str) -> float:
    """Index of Coincidence: peluang dua huruf acak sama."""
    cleaned = _clean(text)
    total = len(cleaned)
    if total < 2:
        return 0.0
    counts = Counter(cleaned)
    return sum(c * (c - 1) for c in counts.values()) / (total * (total - 1))


def top_ngrams(text: str, n: int, k: int) -> list[tuple[str, int]]:
    """K `k` n-gram terbanyak beserta jumlahnya."""
    return ngram_counts(text, n).most_common(k)
