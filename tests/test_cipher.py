"""Tes untuk M2: cipher Caesar dan substitusi."""

import string

import pytest

from src import cipher

SAMPLE = "Halo, Dunia! Ini 123 tes."
FIXED_KEY = "QWERTYUIOPASDFGHJKLZXCVBNM"


def test_caesar_known_vector():
    assert cipher.caesar_encrypt("ABC xyz", 3) == "DEF abc"


def test_caesar_roundtrip_all_shifts():
    for shift in range(26):
        encrypted = cipher.caesar_encrypt(SAMPLE, shift)
        assert cipher.caesar_decrypt(encrypted, shift) == SAMPLE


def test_caesar_shift_zero_identity():
    assert cipher.caesar_encrypt(SAMPLE, 0) == SAMPLE


def test_caesar_invalid_shift_rejected():
    for bad in (-1, 26, 100, "3", 3.0, None):
        with pytest.raises(ValueError):
            cipher.caesar_encrypt(SAMPLE, bad)
        with pytest.raises(ValueError):
            cipher.caesar_decrypt(SAMPLE, bad)


def test_generate_key_is_valid_permutation():
    for seed in (None, 0, 1, 42):
        key = cipher.generate_key(seed)
        assert cipher.validate_key(key)
        assert sorted(key) == sorted(string.ascii_uppercase)


def test_generate_key_same_seed_same_key():
    assert cipher.generate_key(7) == cipher.generate_key(7)


def test_generate_key_differs_across_seeds():
    keys = {cipher.generate_key(seed) for seed in range(10)}
    assert len(keys) > 1


def test_substitution_roundtrip_fixed_key():
    assert (
        cipher.substitution_decrypt(
            cipher.substitution_encrypt(SAMPLE, FIXED_KEY), FIXED_KEY
        )
        == SAMPLE
    )


def test_substitution_roundtrip_generated_keys():
    for seed in range(5):
        key = cipher.generate_key(seed)
        assert (
            cipher.substitution_decrypt(cipher.substitution_encrypt(SAMPLE, key), key)
            == SAMPLE
        )


def test_substitution_preserves_case_and_punctuation():
    encrypted = cipher.substitution_encrypt("AbC, xYz! 9", FIXED_KEY)
    assert encrypted[3] == "," and encrypted[8] == "!" and encrypted[-1] == "9"
    assert encrypted[0].isupper() and encrypted[1].islower() and encrypted[2].isupper()


def test_substitution_known_mapping():
    assert cipher.substitution_encrypt("ABC", FIXED_KEY) == "QWE"
    assert cipher.substitution_decrypt("QWE", FIXED_KEY) == "ABC"


def test_substitution_invalid_key_rejected():
    bad_keys = [
        "ABC",  # terlalu pendek
        "A" * 26,  # duplikat
        "abcdefghijklmnopqrstuvwxyZ",  # huruf kecil
        "QWERTYUIOPASDFGHJKLZXCVBN1",  # ada angka
        "",  # kosong
        None,  # bukan string
    ]
    for bad in bad_keys:
        assert not cipher.validate_key(bad)
        with pytest.raises(ValueError):
            cipher.substitution_encrypt(SAMPLE, bad)
        with pytest.raises(ValueError):
            cipher.substitution_decrypt(SAMPLE, bad)


def test_validate_key_accepts_identity():
    assert cipher.validate_key(string.ascii_uppercase)
