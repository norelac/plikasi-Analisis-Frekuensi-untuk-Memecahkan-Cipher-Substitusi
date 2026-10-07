"""Pemecah cipher substitusi: Caesar, tebakan frekuensi, hill climbing.

Semua fungsi murni. Randomness memakai parameter `seed` agar reproducible.
"""

import random
from collections import Counter

from src import cipher
from src.analysis import chi_square, clean_text
from src.cipher import ALPHABET
from src.reference import load_reference

_ref_cache: dict[str, dict] = {}
_trigram_cache: dict[str, list[float]] = {}


def clear_cache() -> None:
    """Bersihkan cache referensi dan tabel trigram."""
    _ref_cache.clear()
    _trigram_cache.clear()


def _get_reference(lang: str) -> dict:
    """Ambil referensi bahasa dari cache (muat sekali saja)."""
    if lang not in _ref_cache:
        _ref_cache[lang] = load_reference(lang)
    return _ref_cache[lang]


def _trigram_table(lang: str) -> list[float]:
    """Tabel log-probabilitas trigram sebagai list 26^3 (urutan AAA..ZZZ)."""
    if lang not in _trigram_cache:
        ref = _get_reference(lang)
        table = [0.0] * 26**3
        for trigram, logprob in ref["trigram"].items():
            table[
                (ord(trigram[0]) - 65) * 676
                + (ord(trigram[1]) - 65) * 26
                + (ord(trigram[2]) - 65)
            ] = logprob
        _trigram_cache[lang] = table
    return _trigram_cache[lang]


def score_text(text: str, lang: str, bigram_weight: float = 0.0) -> float:
    """Skor kecocokan teks terhadap bahasa: jumlah log-probabilitas trigram.

    `bigram_weight` opsional menambah bobot jumlah log-probabilitas bigram.
    """
    ref = _get_reference(lang)
    cleaned = clean_text(text)
    score = 0.0
    trigram = ref["trigram"]
    for i in range(len(cleaned) - 2):
        score += trigram[cleaned[i : i + 3]]
    if bigram_weight:
        bigram = ref["bigram"]
        for i in range(len(cleaned) - 1):
            score += bigram_weight * bigram[cleaned[i : i + 2]]
    return score


def crack_caesar(ciphertext: str, lang: str) -> tuple[int, str]:
    """Pecahkan Caesar: coba 26 shift, pilih chi-square terkecil.

    Mengembalikan (shift, plaintext).
    """
    if not clean_text(ciphertext):
        return 0, ciphertext
    ref_unigram = _get_reference(lang)["unigram"]
    best_shift, best_score, best_plain = 0, float("inf"), ciphertext
    for shift in range(26):
        plain = cipher.caesar_decrypt(ciphertext, shift)
        score = chi_square(plain, ref_unigram)
        if score < best_score:
            best_shift, best_score, best_plain = shift, score, plain
    return best_shift, best_plain


def _to_dec(key_str: str) -> list[int]:
    """Ubah kunci format enkripsi menjadi array dekripsi (cipher->plain)."""
    dec = [0] * 26
    for plain_idx, ch in enumerate(key_str):
        dec[ord(ch) - 65] = plain_idx
    return dec


def _to_key_str(dec: list[int]) -> str:
    """Ubah array dekripsi (cipher->plain) menjadi kunci format enkripsi."""
    enc = [""] * 26
    for cipher_idx, plain_idx in enumerate(dec):
        enc[plain_idx] = chr(cipher_idx + 65)
    return "".join(enc)


def frequency_guess(ciphertext: str, lang: str) -> str:
    """Tebak kunci: petakan peringkat frekuensi cipher ke referensi.

    Huruf yang tak muncul diisi sisa huruf agar tetap permutasi valid.
    Mengembalikan kunci format enkripsi (siap pakai `substitution_decrypt`).
    """
    cleaned = clean_text(ciphertext)
    if not cleaned:
        return ALPHABET
    ref_unigram = _get_reference(lang)["unigram"]
    plain_order = sorted(ALPHABET, key=lambda ch: (-ref_unigram[ch], ch))
    counts = Counter(cleaned)
    cipher_order = sorted(counts, key=lambda ch: (-counts[ch], ch))
    cipher_order += [ch for ch in ALPHABET if ch not in counts]
    plain_of = dict(zip(cipher_order, plain_order))
    cipher_of = {plain: cipher for cipher, plain in plain_of.items()}
    return "".join(cipher_of[ch] for ch in ALPHABET)


def _score_key(arr: list[int], key: list[int], table: list[float]) -> float:
    """Skor trigram untuk array indeks cipher dan kunci (cipher->plain)."""
    n = len(arr)
    if n < 3:
        return 0.0
    p0, p1, p2 = key[arr[0]], key[arr[1]], key[arr[2]]
    idx = (p0 * 26 + p1) * 26 + p2
    score = table[idx]
    for k in range(3, n):
        idx = (idx % 676) * 26 + key[arr[k]]
        score += table[idx]
    return score


def hill_climb(
    ciphertext: str, lang: str, restarts: int = 10, max_iter: int = 2000, seed: int = 0
) -> tuple[str, str, float]:
    """Pecahkan substitusi dengan hill climbing + beberapa restart.

    Restart pertama mulai dari `frequency_guess`, sisanya dari kunci acak.
    Tiap iterasi menukar dua huruf kunci dan menerima bila skor naik;
    berhenti bila satu putaran penuh pasangan tanpa perbaikan atau
    anggaran `max_iter` habis. Mengembalikan (key, plaintext, score) terbaik.
    """
    table = _trigram_table(lang)
    arr = [ord(ch) - 65 for ch in clean_text(ciphertext)]
    if not arr:
        identity = ALPHABET
        return identity, ciphertext, 0.0

    rng = random.Random(seed)
    starts = [_to_dec(frequency_guess(ciphertext, lang))]
    for _ in range(restarts):
        random_key = list(range(26))
        rng.shuffle(random_key)
        starts.append(random_key)

    pairs = [(i, j) for i in range(26) for j in range(i + 1, 26)]
    best_key = list(starts[0])
    best_score = _score_key(arr, best_key, table)
    for start in starts:
        key = list(start)
        score = _score_key(arr, key, table)
        used = 0
        while used < max_iter:
            order = list(pairs)
            rng.shuffle(order)
            improved = False
            for i, j in order:
                if used >= max_iter:
                    break
                used += 1
                key[i], key[j] = key[j], key[i]
                new_score = _score_key(arr, key, table)
                if new_score > score:
                    score = new_score
                    improved = True
                else:
                    key[i], key[j] = key[j], key[i]
            if not improved:
                break
        if score > best_score:
            best_key, best_score = list(key), score

    key_str = _to_key_str(best_key)
    return key_str, cipher.substitution_decrypt(ciphertext, key_str), best_score


def detect_language(ciphertext: str) -> str:
    """Deteksi bahasa ('en' atau 'id') via cracking singkat dua bahasa."""
    results = {}
    for lang in ("en", "id"):
        _, _, score = hill_climb(ciphertext, lang, restarts=2, max_iter=500, seed=0)
        results[lang] = score
    return max(results, key=lambda lang: results[lang])
