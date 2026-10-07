"""Tes untuk M3: analisis frekuensi (dengan hitungan manual di komentar)."""

import math
import string

import pytest

from src import analysis

# Referensi seragam: tiap huruf 100/26 % (untuk tes chi-square).
UNIFORM_REF = {ch: 100.0 / 26 for ch in string.ascii_uppercase}


def test_letter_frequencies_aab():
    # Manual: "AAB" -> A muncul 2/3 = 66,67%, B muncul 1/3 = 33,33%.
    freq = analysis.letter_frequencies("AAB")
    assert freq["A"] == pytest.approx(200.0 / 3)
    assert freq["B"] == pytest.approx(100.0 / 3)
    assert sum(freq.values()) == pytest.approx(100.0)


def test_letter_frequencies_case_insensitive():
    # Manual: "aAbB" -> A 2/4 = 50%, B 2/4 = 50%.
    freq = analysis.letter_frequencies("aAbB, 123!")
    assert freq["A"] == pytest.approx(50.0)
    assert freq["B"] == pytest.approx(50.0)


def test_letter_frequencies_empty():
    assert all(v == 0.0 for v in analysis.letter_frequencies("123 !!!").values())


def test_ngram_counts_bigram():
    # Manual: "AABAA" -> bigram AA, AB, BA, AA = {AA:2, AB:1, BA:1}.
    assert analysis.ngram_counts("AABAA", 2) == {"AA": 2, "AB": 1, "BA": 1}


def test_ngram_counts_trigram():
    # Manual: "AABAA" -> trigram AAB, ABA, BAA masing-masing 1.
    assert analysis.ngram_counts("AABAA", 3) == {"AAB": 1, "ABA": 1, "BAA": 1}


def test_ngram_counts_invalid_n():
    with pytest.raises(ValueError):
        analysis.ngram_counts("ABC", 4)


def test_chi_square_uniform():
    # Manual: teks "AAAA" (N=4) vs ref seragam E=4/26 per huruf.
    # (4-E)^2/E + 25*(0-E)^2/E = 96,1538 + 3,8462 = 100,0.
    assert analysis.chi_square("AAAA", UNIFORM_REF) == pytest.approx(100.0)


def test_chi_square_prefers_matching_ref():
    text = "E" * 80 + "T" * 20
    skewed = dict(UNIFORM_REF, E=80.0, T=20.0)
    assert analysis.chi_square(text, skewed) < analysis.chi_square(text, UNIFORM_REF)


def test_chi_square_empty_is_inf():
    assert math.isinf(analysis.chi_square("123", UNIFORM_REF))


def test_index_of_coincidence_aab():
    # Manual: "AAB", N=3 -> (2*1 + 1*0)/(3*2) = 2/6 = 0,3333.
    assert analysis.index_of_coincidence("AAB") == pytest.approx(1.0 / 3)


def test_index_of_coincidence_uniform_letter():
    # Manual: "AAAA" -> (4*3)/(4*3) = 1,0.
    assert analysis.index_of_coincidence("AAAA") == pytest.approx(1.0)


def test_index_of_coincidence_too_short():
    assert analysis.index_of_coincidence("A") == 0.0
    assert analysis.index_of_coincidence("") == 0.0


def test_top_ngrams():
    # Manual: "AABAA" -> bigram terbanyak AA(2), lalu AB(1).
    assert analysis.top_ngrams("AABAA", 2, 2) == [("AA", 2), ("AB", 1)]
