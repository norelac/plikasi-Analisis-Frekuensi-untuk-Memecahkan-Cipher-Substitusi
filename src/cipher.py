"""Cipher substitusi: Caesar dan substitusi monoalfabetik.

Hanya huruf A-Z yang diubah; huruf besar/kecil, spasi, angka, dan tanda
baca dipertahankan. Semua fungsi murni.
"""

import random
import string

ALPHABET = string.ascii_uppercase


def _shift_char(char: str, shift: int) -> str:
    """Geser satu huruf, pertahankan besar/kecilnya."""
    if "A" <= char <= "Z":
        base = ord("A")
    elif "a" <= char <= "z":
        base = ord("a")
    else:
        return char
    return chr((ord(char) - base + shift) % 26 + base)


def _check_shift(shift: int) -> None:
    """Validasi shift berada dalam rentang 0-25."""
    if not isinstance(shift, int) or isinstance(shift, bool) or not 0 <= shift <= 25:
        raise ValueError(f"Shift harus bilangan bulat 0-25, diterima: {shift!r}.")


def caesar_encrypt(text: str, shift: int) -> str:
    """Enkripsi teks dengan Caesar cipher (geser maju `shift`)."""
    _check_shift(shift)
    return "".join(_shift_char(ch, shift) for ch in text)


def caesar_decrypt(text: str, shift: int) -> str:
    """Dekripsi teks Caesar yang dienkripsi dengan `shift` yang sama."""
    _check_shift(shift)
    return "".join(_shift_char(ch, -shift) for ch in text)


def validate_key(key: str) -> bool:
    """True bila `key` permutasi valid: 26 huruf unik A-Z."""
    return isinstance(key, str) and len(key) == 26 and set(key) == set(ALPHABET)


def _check_key(key: str) -> None:
    """Validasi kunci substitusi, raise ValueError bila tidak valid."""
    if not validate_key(key):
        raise ValueError(f"Kunci tidak valid: {key!r}. Harus permutasi 26 huruf A-Z.")


def generate_key(seed: int | None = None) -> str:
    """Buat kunci substitusi acak (permutasi A-Z).

    Seed yang sama selalu menghasilkan kunci yang sama.
    """
    rng = random.Random(seed)
    letters = list(ALPHABET)
    rng.shuffle(letters)
    return "".join(letters)


def substitution_encrypt(text: str, key: str) -> str:
    """Enkripsi teks: huruf plain A-Z dipetakan ke `key`."""
    _check_key(key)
    table = {plain: cipher for plain, cipher in zip(ALPHABET, key)}
    result = []
    for ch in text:
        if "A" <= ch <= "Z":
            result.append(table[ch])
        elif "a" <= ch <= "z":
            result.append(table[ch.upper()].lower())
        else:
            result.append(ch)
    return "".join(result)


def substitution_decrypt(text: str, key: str) -> str:
    """Dekripsi teks yang dienkripsi dengan kunci `key` yang sama."""
    _check_key(key)
    table = {cipher: plain for plain, cipher in zip(ALPHABET, key)}
    result = []
    for ch in text:
        if "A" <= ch <= "Z":
            result.append(table[ch])
        elif "a" <= ch <= "z":
            result.append(table[ch.upper()].lower())
        else:
            result.append(ch)
    return "".join(result)
