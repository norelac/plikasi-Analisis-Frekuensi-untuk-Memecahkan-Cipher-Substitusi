"""Tes untuk M4: pemecah cipher (teks uji dari data holdout)."""

from pathlib import Path

from src import cipher, cracker

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "samples"


def load_sample(lang: str, min_letters: int) -> str:
    """Ambil kalimat holdout sampai terkumpul >= min_letters huruf."""
    text, count = "", 0
    for line in (
        (DATA_DIR / f"holdout_{lang}.txt").read_text(encoding="utf-8").splitlines()
    ):
        text += line + " "
        count += sum(ch.isalpha() for ch in line)
        if count >= min_letters:
            break
    assert count >= min_letters
    return text


def accuracy(plain: str, expected: str) -> float:
    """Fraksi huruf (A-Z, case-insensitive) yang benar."""
    pairs = [(p, e) for p, e in zip(plain.upper(), expected.upper()) if e.isalpha()]
    return sum(1 for p, e in pairs if p == e) / len(pairs)


def test_crack_caesar_100_percent():
    for lang in ("en", "id"):
        text = load_sample(lang, 100)
        for shift in (3, 7, 19):
            found_shift, plain = cracker.crack_caesar(
                cipher.caesar_encrypt(text, shift), lang
            )
            assert found_shift == shift
            assert plain == text


def test_frequency_guess_returns_valid_key():
    for lang in ("en", "id"):
        text = load_sample(lang, 200)
        key = cracker.frequency_guess(
            cipher.substitution_encrypt(text, cipher.generate_key(5)), lang
        )
        assert cipher.validate_key(key)


def test_hill_climb_beats_frequency_guess():
    for lang in ("en", "id"):
        text = load_sample(lang, 400)
        ciphertext = cipher.substitution_encrypt(text, cipher.generate_key(11))
        guess_plain = cipher.substitution_decrypt(
            ciphertext, cracker.frequency_guess(ciphertext, lang)
        )
        key, plain, _ = cracker.hill_climb(
            ciphertext, lang, restarts=3, max_iter=1500, seed=0
        )
        assert cipher.validate_key(key)
        assert plain == cipher.substitution_decrypt(ciphertext, key)
        assert cracker.score_text(plain, lang) >= cracker.score_text(guess_plain, lang)
        assert accuracy(plain, text) >= accuracy(guess_plain, text)


def test_hill_climb_is_deterministic():
    text = load_sample("en", 300)
    ciphertext = cipher.substitution_encrypt(text, cipher.generate_key(3))
    first = cracker.hill_climb(ciphertext, "en", restarts=2, max_iter=500, seed=1)
    second = cracker.hill_climb(ciphertext, "en", restarts=2, max_iter=500, seed=1)
    assert first[0] == second[0] and first[1] == second[1]


def test_score_text_prefers_correct_decryption():
    text = load_sample("en", 300)
    key = cipher.generate_key(9)
    ciphertext = cipher.substitution_encrypt(text, key)
    assert cracker.score_text(text, "en") > cracker.score_text(ciphertext, "en")


def test_detect_language():
    assert cracker.detect_language(load_sample("en", 300)) == "en"
    assert cracker.detect_language(load_sample("id", 300)) == "id"


def test_crack_caesar_no_letters():
    shift, plain = cracker.crack_caesar("123 !? #$", "id")
    assert shift == 0
    assert plain == "123 !? #$"


def test_frequency_guess_no_letters():
    key = cracker.frequency_guess("123 !?", "en")
    assert key == cracker.ALPHABET


def test_key_conversion_roundtrip():
    for seed in range(5):
        key = cipher.generate_key(seed)
        dec = cracker._to_dec(key)
        assert cracker._to_key_str(dec) == key


def test_score_text_short_and_weighted():
    assert cracker.score_text("A", "en") == 0.0
    assert cracker.score_text("AB", "en") == 0.0
    unweighted = cracker.score_text("ABC", "en", bigram_weight=0.0)
    weighted = cracker.score_text("ABC", "en", bigram_weight=1.0)
    assert weighted < unweighted  # bigram logprob is negative, reduces score


def test_clear_cache():
    cracker._get_reference("id")
    cracker._trigram_table("id")
    assert "id" in cracker._ref_cache
    assert "id" in cracker._trigram_cache
    cracker.clear_cache()
    assert len(cracker._ref_cache) == 0
    assert len(cracker._trigram_cache) == 0
